"""
Barclays Quantum Security Capsule (QSC) - File Encryption & Decryption Demo
Demonstrates real-world end-to-end file protection using NIST Post-Quantum Cryptography standards:
- ML-KEM-768 (FIPS 203) Key Encapsulation
- ML-DSA-65 (FIPS 204) Lattice Signature
- AES-256-GCM Authenticated Encryption
- SHA3-512 Canonical Integrity Lock
"""

import sys
import os
import json
import base64

# Add root directory to python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.crypto import MLKEM768, MLDSA65
from src.capsule import CapsuleBuilder, SecureReceiver, PolicyMetadata, QuantumSecurityCapsule

def demo_file_encryption():
    print("=" * 80)
    print(" BARCLAYS INNOVATION LAB - QUANTUM SECURITY CAPSULE (QSC)")
    print(" REAL-WORLD USE CASE: QUANTUM-SAFE FILE ENCRYPTION & DECRYPTION")
    print("=" * 80)

    # 1. Setup Sample File
    input_filename = "confidential_wire_instructions.pdf"
    output_qsc_file = "encrypted_wire_instructions.qsc"
    restored_filename = "decrypted_wire_instructions.pdf"

    sample_content = (
        "CONFIDENTIAL SECURE DOCUMENT\n"
        "----------------------------------------\n"
        "Transfer ID  : TXN-QSC-2026-991823\n"
        "Sender       : Alice\n"
        "Recipient    : Bob\n"
        "Amount       : GBP 50,000,000.00\n"
        "Value Date   : 2026-07-28\n"
        "Auth Status  : QUANTUM_LEVEL_3_APPROVED\n"
    ).encode('utf-8')

    print(f"\n[Step 1] Creating sample sensitive file: '{input_filename}'...")
    with open(input_filename, "wb") as f:
        f.write(sample_content)
    print(f"  -> File created ({len(sample_content)} bytes).")

    # 2. Key Generation
    print("\n[Step 2] Generating NIST PQC Cryptographic Keypairs...")
    sender_dsa_pub, sender_dsa_priv = MLDSA65.generate_keypair()
    receiver_kem_pub, receiver_kem_priv = MLKEM768.generate_keypair()
    print(f"  -> Sender ML-DSA-65 Public Key   : {len(sender_dsa_pub)} bytes")
    print(f"  -> Receiver ML-KEM-768 Public Key : {len(receiver_kem_pub)} bytes")

    # 3. Read File and Encapsulate into QSC
    print(f"\n[Step 3] Encrypting & Encapsulating '{input_filename}' into QSC format...")
    with open(input_filename, "rb") as f:
        file_payload = f.read()

    builder = CapsuleBuilder(
        sender_id="alice",
        sender_private_dsa_key=sender_dsa_priv
    )

    policy = PolicyMetadata(
        classification="TOP_SECRET_TREASURY",
        jurisdiction="UK_IN",
        max_hops=1
    )

    capsule = builder.build_capsule(
        recipient_id="bob",
        recipient_public_kem_key=receiver_kem_pub,
        payload=file_payload,
        validity_seconds=600,
        policy=policy
    )

    # 4. Save Capsule to Disk as .qsc (JSON wire format)
    capsule_json_str = json.dumps(capsule.to_dict(), indent=2)
    with open(output_qsc_file, "w") as f:
        f.write(capsule_json_str)

    print(f"  [OK] Encrypted Capsule saved to disk: '{output_qsc_file}' ({len(capsule_json_str)} bytes)")
    print(f"  -> Capsule ID        : {capsule.capsule_id}")
    print(f"  -> Replay Token      : {capsule.replay_token[:32]}...")
    print(f"  -> SHA3-512 Hash     : {capsule.integrity_hash[:32]}...")
    print(f"  -> ML-DSA Signature  : {capsule.signature[:32]}...")

    # 5. Read .qsc File and Decrypt on Recipient Side
    print(f"\n[Step 4] Reading '{output_qsc_file}' on Receiver side and performing verification...")
    with open(output_qsc_file, "r") as f:
        loaded_dict = json.load(f)
    
    loaded_capsule = QuantumSecurityCapsule(**loaded_dict)

    receiver = SecureReceiver(
        recipient_id="bob",
        recipient_private_kem_key=receiver_kem_priv
    )

    success, decrypted_bytes, status_msg = receiver.process_and_decrypt(
        capsule=loaded_capsule,
        sender_public_dsa_key=sender_dsa_pub
    )

    print(f"  -> Validation Status : {'SUCCESS' if success else 'FAILED'}")
    print(f"  -> Receiver Message  : {status_msg}")

    if success:
        with open(restored_filename, "wb") as f:
            f.write(decrypted_bytes)
        print(f"\n[Step 5] Restored decrypted file to '{restored_filename}'!")
        print("\n--- DECRYPTED FILE CONTENT ---")
        print(decrypted_bytes.decode('utf-8'))
        print("-------------------------------")
        assert decrypted_bytes == sample_content, "Decrypted content must match original payload!"
        print(" [VERIFIED] Original content and decrypted content are 100% identical!")

    # Cleanup created temp files
    for tmp in [input_filename, output_qsc_file, restored_filename]:
        if os.path.exists(tmp):
            os.remove(tmp)
            print(f"  -> Cleaned up demo file '{tmp}'")

    print("\n" + "=" * 80)
    print(" USE CASE DEMO COMPLETE - QUANTUM-SAFE FILE ENCRYPTION & INTEGRITY VERIFIED")
    print("=" * 80)

if __name__ == "__main__":
    demo_file_encryption()
