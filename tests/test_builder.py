import pytest
import base64
from src.crypto import MLKEM768, MLDSA65
from src.capsule import CapsuleBuilder

def test_capsule_builder_creation():
    sender_pub, sender_priv = MLDSA65.generate_keypair()
    recip_pub, recip_priv = MLKEM768.generate_keypair()

    builder = CapsuleBuilder("sender-123", sender_priv)
    payload = b"Hello Quantum Security Capsule"
    
    capsule = builder.build_capsule("recip-456", recip_pub, payload)

    assert capsule.version == "QSC-1.0"
    assert capsule.sender_id == "sender-123"
    assert capsule.recipient_id == "recip-456"
    assert len(capsule.integrity_hash) == 128  # SHA3-512 hex length
    assert len(capsule.replay_token) == 128
    assert len(capsule.signature) > 0
    assert len(capsule.kem_ciphertext) > 0
