import pytest
from src.crypto import MLKEM768, MLDSA65
from src.capsule import CapsuleBuilder, SecureReceiver

def test_replay_attack_prevention():
    sender_pub, sender_priv = MLDSA65.generate_keypair()
    recip_pub, recip_priv = MLKEM768.generate_keypair()

    builder = CapsuleBuilder("client-node", sender_priv)
    receiver = SecureReceiver("server-node", recip_priv)

    capsule = builder.build_capsule("server-node", recip_pub, b"PAYOUT_50000_USD")

    # First attempt should succeed
    ok1, data1, msg1 = receiver.process_and_decrypt(capsule, sender_pub)
    assert ok1 is True
    assert data1 == b"PAYOUT_50000_USD"

    # Second attempt with identical replay token should fail
    ok2, data2, msg2 = receiver.process_and_decrypt(capsule, sender_pub)
    assert ok2 is False
    assert "Replay attack detected" in msg2
