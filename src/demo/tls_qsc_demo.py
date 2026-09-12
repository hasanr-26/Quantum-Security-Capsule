import sys
import os
import ssl
import socket
import threading
import json
import time
import datetime

# Add root directory to python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa

from src.crypto import MLKEM768, MLDSA65
from src.capsule import CapsuleBuilder, SecureReceiver, PolicyMetadata

def generate_self_signed_cert():
    """Generates an in-memory self-signed TLS X.509 certificate and private key for demonstration."""
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COMMON_NAME, u"localhost"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, u"Barclays Innovation Lab"),
    ])
    cert = x509.CertificateBuilder().subject_name(
        subject
    ).issuer_name(
        issuer
    ).public_key(
        key.public_key()
    ).serial_number(
        x509.random_serial_number()
    ).not_valid_before(
        datetime.datetime.now(datetime.timezone.utc)
    ).not_valid_after(
        datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=1)
    ).sign(key, hashes.SHA256())

    cert_pem = cert.public_bytes(serialization.Encoding.PEM)
    key_pem = key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption()
    )

    cert_file = os.path.abspath("temp_cert.pem")
    key_file = os.path.abspath("temp_key.pem")

    with open(cert_file, "wb") as f:
        f.write(cert_pem)
    with open(key_file, "wb") as f:
        f.write(key_pem)

    return cert_file, key_file

def main():
    print("=" * 75)
    print(" QUANTUM SECURITY CAPSULE (QSC) OVER TLS 1.3 HANDSHAKE DEMONSTRATION")
    print(" Dual-Layer Security: Transport Channel Encryption (TLS) + Post-Quantum Payload (QSC)")
    print("=" * 75)

    # 1. Generate Certificates & PQC Keypairs
    print("\n[Step 1] Initializing Keys & SSL/TLS Certificates...")
    cert_file, key_file = generate_self_signed_cert()
    print("  -> SSL/TLS X.509 Certificate generated (localhost)")

    sender_dsa_pub, sender_dsa_priv = MLDSA65.generate_keypair()
    receiver_kem_pub, receiver_kem_priv = MLKEM768.generate_keypair()

    print(f"  -> Sender ML-DSA-65 Signing Public Key Size : {len(sender_dsa_pub)} bytes")
    print(f"  -> Receiver ML-KEM-768 Key Encapsulation Public Key Size: {len(receiver_kem_pub)} bytes")

    # Shared results structure
    server_received_data = {}

    # 2. Define TLS Server
    def run_tls_server():
        server_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        server_context.load_cert_chain(certfile=cert_file, keyfile=key_file)

        raw_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        raw_socket.bind(('127.0.0.1', 9443))
        raw_socket.listen(1)
        raw_socket.settimeout(5)

        try:
            conn, addr = raw_socket.accept()
            tls_conn = server_context.wrap_socket(conn, server_side=True)
            print("  [TLS Server] Client connected & TLS Handshake completed successfully!")
            
            # Read transmitted payload length + payload
            data_bytes = tls_conn.recv(65536)
            server_received_data["raw_payload"] = data_bytes
            
            # Process received QSC payload
            capsule_dict = json.loads(data_bytes.decode('utf-8'))
            from src.capsule.models import QuantumSecurityCapsule
            received_capsule = QuantumSecurityCapsule(**capsule_dict)

            receiver = SecureReceiver(
                recipient_id="barclays-core-settlement-engine",
                recipient_private_kem_key=receiver_kem_priv
            )

            success, decrypted_bytes, status_msg = receiver.process_and_decrypt(
                capsule=received_capsule,
                sender_public_dsa_key=sender_dsa_pub
            )

            server_received_data["success"] = success
            server_received_data["status_msg"] = status_msg
            server_received_data["decrypted_payload"] = decrypted_bytes.decode('utf-8') if success else ""

            # Send response back to TLS client
            response = json.dumps({"status": "SUCCESS", "message": "QSC Capsule decrypted and processed"}).encode('utf-8')
            tls_conn.sendall(response)
            tls_conn.close()
        except socket.timeout:
            pass
        finally:
            raw_socket.close()

    # Start TLS Server thread
    server_thread = threading.Thread(target=run_tls_server)
    server_thread.start()
    time.sleep(0.5)

    # 3. TLS Client Workflow
    print("\n[Step 2] Establishing TLS Handshake & Transmitting QSC Payload...")
    
    # Build QSC Capsule payload
    payload_json = json.dumps({
        "instruction": "POST_QUANTUM_SWIFT_TRANSFER",
        "sender_bank": "BARCLAYS_LONDON",
        "receiver_bank": "BARCLAYS_MUMBAI",
        "amount": 2500000.00,
        "currency": "GBP"
    }).encode('utf-8')

    builder = CapsuleBuilder(
        sender_id="barclays-mobile-client-0091",
        sender_private_dsa_key=sender_dsa_priv
    )
    capsule = builder.build_capsule(
        recipient_id="barclays-core-settlement-engine",
        recipient_public_kem_key=receiver_kem_pub,
        payload=payload_json,
        validity_seconds=300
    )

    capsule_json_bytes = json.dumps(capsule.to_dict()).encode('utf-8')

    # TLS Connection & Handshake
    client_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    client_context.check_hostname = False
    client_context.verify_mode = ssl.CERT_NONE

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tls_client = client_context.wrap_socket(sock, server_hostname='localhost')
    print("  [TLS Client] Initiating TCP SYN & TLS Handshake to 127.0.0.1:9443...")
    tls_client.connect(('127.0.0.1', 9443))
    print(f"  [TLS Client] Handshake Completed! Cipher: {tls_client.cipher()[0]}, Version: {tls_client.version()}")

    print("\n[Step 3] Transmitting QSC Payload over Encrypted TLS Tunnel...")
    print(f"  -> Encapsulated QSC Payload Size: {len(capsule_json_bytes)} bytes")
    tls_client.sendall(capsule_json_bytes)

    response = tls_client.recv(4096)
    print(f"  -> TLS Server Reply: {response.decode('utf-8')}")
    tls_client.close()

    server_thread.join()

    # Clean up temp cert files
    if os.path.exists(cert_file):
        os.remove(cert_file)
    if os.path.exists(key_file):
        os.remove(key_file)

    # 4. Display Results & Security Architecture Comparison
    print("\n" + "=" * 75)
    print(" VERIFICATION & DECRYPTION RESULTS AT TLS SERVER")
    print("=" * 75)
    print(f"  Processing Status  : {server_received_data.get('success')}")
    print(f"  Status Message     : {server_received_data.get('status_msg')}")
    print(f"  Decrypted Payload  : {server_received_data.get('decrypted_payload')}")

    print("\n" + "=" * 75)
    print(" ARCHITECTURAL COMPARISON: WHY USE QSC WITH TLS?")
    print("=" * 75)
    print(" 1. TLS Handshake protects the NETWORK CHANNEL (pipe).")
    print(" 2. QSC protects the MESSAGE PAYLOAD (data) with NIST PQC (ML-KEM-768 + ML-DSA-65).")
    print(" 3. Zero-Trust Security: Even if a WAF / Reverse Proxy terminates TLS,")
    print("    the payload remains fully encrypted & tamper-proof until reaching the core engine.")
    print(" 4. Harvest-Now-Decrypt-Later Defense: Adversaries storing encrypted TLS traffic")
    print("    cannot decrypt stored QSC capsules even if session keys are later compromised.")
    print("=" * 75)

if __name__ == "__main__":
    main()
