import json
import sys
import os

# Add root directory to python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.crypto import MLKEM768, MLDSA65
from src.capsule import CapsuleBuilder, SecureReceiver, PolicyMetadata

def main():
    print("=" * 70)
    print(" BARCLAYS INNOVATION LAB - QUANTUM SECURITY CAPSULE (QSC) DEMO")
    print(" Scenario: High-Value Interbank Wire Transfer (INR 50,000 / GBP 500,000)")
    print("=" * 70)

    # 1. Key Generation for Sender (Client/Mobile App) and Receiver (Core Banking Server)
    print("\n[Step 1] Initializing NIST Post-Quantum Cryptographic Keypairs...")
    sender_dsa_pub, sender_dsa_priv = MLDSA65.generate_keypair()
    receiver_kem_pub, receiver_kem_priv = MLKEM768.generate_keypair()

    print(f"  -> Sender ML-DSA-65 Public Key Size: {len(sender_dsa_pub)} bytes")
    print(f"  -> Receiver ML-KEM-768 Public Key Size: {len(receiver_kem_pub)} bytes")

    # 2. Banking Transaction Request
    transaction_payload = json.dumps({
        "transaction_id": "TXN-BARC-2026-991823",
        "sender_account": "GB82BARC20000012345678",
        "recipient_account": "GB91BARC20000087654321",
        "amount": 50000.00,
        "currency": "INR",
        "reference": "Supplier Invoice Payment #8821"
    }).encode('utf-8')

    print("\n[Step 2] Original Plaintext Banking Instruction Payload:")
    print(f"  {transaction_payload.decode('utf-8')}")

    # 3. Capsule Assembly by CapsuleBuilder
    print("\n[Step 3] Encapsulating Message into Quantum Security Capsule (QSC)...")
    builder = CapsuleBuilder(
        sender_id="barclays-mobile-client-0091",
        sender_private_dsa_key=sender_dsa_priv
    )

    policy = PolicyMetadata(
        classification="RESTRICTED_FINANCIAL",
        jurisdiction="UK_IN",
        max_hops=2
    )

    capsule = builder.build_capsule(
        recipient_id="barclays-core-settlement-engine",
        recipient_public_kem_key=receiver_kem_pub,
        payload=transaction_payload,
        validity_seconds=300,
        policy=policy
    )

    print("  [OK] Capsule Assembly Complete!")
    print(f"  -> Capsule ID        : {capsule.capsule_id}")
    print(f"  -> Issued At         : {capsule.issued_at}")
    print(f"  -> Expires At        : {capsule.expires_at}")
    print(f"  -> Replay Token      : {capsule.replay_token[:32]}...")
    print(f"  -> SHA3-512 Hash     : {capsule.integrity_hash[:32]}...")
    print(f"  -> ML-DSA Signature  : {capsule.signature[:32]}...")

    # 4. Transmit Capsule over Untrusted Network (Simulated)
    print("\n[Step 4] Transmitting Capsule over Network (API / Kafka / MQ / TLS)...")
    print("  [Simulated Interception] An attacker records the raw network stream ('Harvest Now, Decrypt Later').")
    print("  Notice: Attacker cannot read payload (AES-256-GCM encrypted under ephemeral ML-KEM shared key)")
    print("  Notice: Attacker cannot modify payload (Integrity lock + ML-DSA signature will fail)")

    # 5. Receiver Validation & Decryption
    print("\n[Step 5] Core Banking Server processes and validates Capsule...")
    receiver = SecureReceiver(
        recipient_id="barclays-core-settlement-engine",
        recipient_private_kem_key=receiver_kem_priv
    )

    success, decrypted_bytes, message = receiver.process_and_decrypt(
        capsule=capsule,
        sender_public_dsa_key=sender_dsa_pub
    )

    print(f"\n[Result] Processing Status: {success}")
    print(f"  -> Status Message   : {message}")
    print(f"  -> Decrypted Payload: {decrypted_bytes.decode('utf-8')}")

    print("\n" + "=" * 70)
    print(" DEMO COMPLETED SUCCESSFULLY: End-to-End Quantum Security Achieved")
    print("=" * 70)

if __name__ == "__main__":
    main()
