import json
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.crypto import MLKEM768, MLDSA65
from src.capsule import CapsuleBuilder, SecureReceiver

def main():
    print("=" * 70)
    print(" BARCLAYS INNOVATION LAB - QSC SECURITY & REPLAY PROTECTION DEMO")
    print(" Testing Resilience against Replay Attacks & Network Tampering")
    print("=" * 70)

    # Key Setup
    sender_pub, sender_priv = MLDSA65.generate_keypair()
    receiver_pub, receiver_priv = MLKEM768.generate_keypair()

    builder = CapsuleBuilder("mobile-app-client", sender_priv)
    receiver = SecureReceiver("payment-gateway-server", receiver_priv)

    payload = b'{"action": "TRANSFER", "amount": 100000.00, "to": "ACC-991"}'
    original_capsule = builder.build_capsule("payment-gateway-server", receiver_pub, payload)

    # 1. Legitimate Request Processing
    print("\n--- TEST 1: Legitimate First Transmission ---")
    ok, data, msg = receiver.process_and_decrypt(original_capsule, sender_pub)
    print(f"Outcome: Success={ok} | Msg='{msg}'")

    # 2. Replay Attack Attempt
    print("\n--- TEST 2: Attacker Replays Exact Same Capsule ---")
    ok, data, msg = receiver.process_and_decrypt(original_capsule, sender_pub)
    print(f"Outcome: Success={ok} | Msg='{msg}'")
    assert not ok, "Replay attack should have been blocked!"

    # 3. Payload Tampering Attempt
    print("\n--- TEST 3: Attacker Tampers Ciphertext in Transit ---")
    tampered_capsule = builder.build_capsule("payment-gateway-server", receiver_pub, payload)
    # Modify one byte in payload_ciphertext
    tampered_capsule.payload_ciphertext = tampered_capsule.payload_ciphertext[:-2] + "AA"
    
    receiver_fresh = SecureReceiver("payment-gateway-server", receiver_priv)
    ok, data, msg = receiver_fresh.process_and_decrypt(tampered_capsule, sender_pub)
    print(f"Outcome: Success={ok} | Msg='{msg}'")
    assert not ok, "Tampered payload should have failed integrity check!"

    # 4. Signature Forgery Attempt
    print("\n--- TEST 4: Rogue Key Signature Forgery ---")
    rogue_pub, rogue_priv = MLDSA65.generate_keypair()
    rogue_builder = CapsuleBuilder("mobile-app-client", rogue_priv)
    forged_capsule = rogue_builder.build_capsule("payment-gateway-server", receiver_pub, payload)
    
    receiver_fresh_2 = SecureReceiver("payment-gateway-server", receiver_priv)
    # Validate with legitimate sender's public key (not rogue key)
    ok, data, msg = receiver_fresh_2.process_and_decrypt(forged_capsule, sender_pub)
    print(f"Outcome: Success={ok} | Msg='{msg}'")
    assert not ok, "Forged signature from rogue key should have been rejected!"

    print("\n" + "=" * 70)
    print(" ALL THREAT MODEL ATTACK SCENARIOS SUCCESSFULLY MITIGATED")
    print("=" * 70)

if __name__ == "__main__":
    main()
