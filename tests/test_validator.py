import pytest
from src.crypto import MLKEM768, MLDSA65
from src.capsule import CapsuleBuilder, CapsuleValidator

def test_validator_success_and_tampering():
    sender_pub, sender_priv = MLDSA65.generate_keypair()
    recip_pub, recip_priv = MLKEM768.generate_keypair()

    builder = CapsuleBuilder("sender-1", sender_priv)
    validator = CapsuleValidator()

    capsule = builder.build_capsule("recip-1", recip_pub, b"Sensitive financial payload")

    # Valid capsule
    is_valid, msg = validator.validate_capsule(capsule, sender_pub)
    assert is_valid is True
    assert msg == "Validation successful"

    # Tampered integrity hash
    capsule_tampered = builder.build_capsule("recip-1", recip_pub, b"Sensitive financial payload")
    capsule_tampered.integrity_hash = "0" * 128
    validator_2 = CapsuleValidator()
    is_valid_2, msg_2 = validator_2.validate_capsule(capsule_tampered, sender_pub)
    assert is_valid_2 is False
    assert "Integrity Lock failure" in msg_2
