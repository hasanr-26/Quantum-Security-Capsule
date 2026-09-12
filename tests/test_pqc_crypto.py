"""
Tests for the NIST post-quantum primitives.

These assert the properties the whole architecture rests on: that key material
is the standard size, that decapsulation genuinely requires the right private
key, and that signature verification rejects forgery rather than waving it
through. If any of these fail, nothing above them means anything.
"""

import pytest

from src.crypto import derive_payload_key, MLDSA65, MLKEM768
from src.crypto.dsa import PRIVATE_KEY_BYTES, PUBLIC_KEY_BYTES, SIGNATURE_BYTES
from src.crypto.kem import (
    CIPHERTEXT_BYTES,
    DECAPSULATION_KEY_BYTES,
    ENCAPSULATION_KEY_BYTES,
    SHARED_SECRET_BYTES,
)


# ---------------------------------------------------------------- ML-KEM-768

def test_kem_key_sizes_match_fips_203():
    public, private = MLKEM768.generate_keypair()
    assert len(public) == ENCAPSULATION_KEY_BYTES == 1184
    assert len(private) == DECAPSULATION_KEY_BYTES == 2400


def test_kem_encapsulation_roundtrip():
    public, private = MLKEM768.generate_keypair()
    secret, ciphertext = MLKEM768.encapsulate(public)

    assert len(secret) == SHARED_SECRET_BYTES == 32
    assert len(ciphertext) == CIPHERTEXT_BYTES == 1088
    assert MLKEM768.decapsulate(private, ciphertext) == secret


def test_kem_secrets_are_unique_per_encapsulation():
    public, _ = MLKEM768.generate_keypair()
    secrets = {MLKEM768.encapsulate(public)[0] for _ in range(8)}
    assert len(secrets) == 8, "Encapsulation must produce fresh entropy each call"


def test_kem_wrong_private_key_yields_wrong_secret():
    public, _ = MLKEM768.generate_keypair()
    _, other_private = MLKEM768.generate_keypair()
    secret, ciphertext = MLKEM768.encapsulate(public)

    assert MLKEM768.decapsulate(other_private, ciphertext) != secret


def test_kem_tampered_ciphertext_triggers_implicit_rejection():
    """
    FIPS 203 specifies implicit rejection: a corrupted ciphertext does not raise,
    it returns a deterministic decoy secret. That decoy must not match the real
    one, so AES-GCM authentication fails closed downstream.
    """
    public, private = MLKEM768.generate_keypair()
    secret, ciphertext = MLKEM768.encapsulate(public)

    corrupted = bytearray(ciphertext)
    corrupted[17] ^= 0x01
    recovered = MLKEM768.decapsulate(private, bytes(corrupted))

    assert len(recovered) == SHARED_SECRET_BYTES
    assert recovered != secret


@pytest.mark.parametrize("bad_key", [b"", b"short", b"\x00" * 100])
def test_kem_rejects_malformed_public_key(bad_key):
    with pytest.raises(ValueError):
        MLKEM768.encapsulate(bad_key)


def test_kem_parameters_report_fips_203_lattice():
    params = MLKEM768.parameters()
    assert params["standard"] == "NIST FIPS 203"
    assert params["modulus_q"] == 3329
    assert params["polynomial_degree_n"] == 256
    assert params["module_rank_k"] == 3


# ---------------------------------------------------------------- ML-DSA-65

def test_dsa_key_and_signature_sizes_match_fips_204():
    public, private = MLDSA65.generate_keypair()
    assert len(public) == PUBLIC_KEY_BYTES == 1952
    assert len(private) == PRIVATE_KEY_BYTES == 4032
    assert len(MLDSA65.sign(private, "digest")) == SIGNATURE_BYTES == 3309


def test_dsa_valid_signature_verifies():
    public, private = MLDSA65.generate_keypair()
    signature = MLDSA65.sign(private, "a" * 128)
    assert MLDSA65.verify(public, "a" * 128, signature) is True


def test_dsa_rejects_signature_over_a_different_message():
    public, private = MLDSA65.generate_keypair()
    signature = MLDSA65.sign(private, "original digest")
    assert MLDSA65.verify(public, "modified digest", signature) is False


def test_dsa_rejects_signature_from_a_rogue_key():
    """An attacker signing with their own key must not pass as the real sender."""
    public, _ = MLDSA65.generate_keypair()
    _, rogue_private = MLDSA65.generate_keypair()
    forged = MLDSA65.sign(rogue_private, "digest")
    assert MLDSA65.verify(public, "digest", forged) is False


def test_dsa_rejects_single_bit_tampering_in_the_signature():
    public, private = MLDSA65.generate_keypair()
    signature = bytearray(MLDSA65.sign(private, "digest"))
    signature[512] ^= 0x01
    assert MLDSA65.verify(public, "digest", bytes(signature)) is False


@pytest.mark.parametrize("bad_signature", [b"", b"\x00" * 64, b"\x00" * 3308])
def test_dsa_verify_returns_false_rather_than_raising(bad_signature):
    """Verification is a boolean gate: malformed input is a failure, not a crash."""
    public, _ = MLDSA65.generate_keypair()
    assert MLDSA65.verify(public, "digest", bad_signature) is False


def test_dsa_accepts_both_text_and_byte_messages():
    public, private = MLDSA65.generate_keypair()
    signature = MLDSA65.sign(private, "abc")
    assert MLDSA65.verify(public, b"abc", signature) is True


# --------------------------------------------------------------------- KDF

def test_kdf_derives_a_256_bit_key_deterministically():
    secret = b"\x2a" * 32
    first = derive_payload_key(secret, "qsc_alpha")
    assert len(first) == 32
    assert derive_payload_key(secret, "qsc_alpha") == first


def test_kdf_separates_keys_by_capsule_id():
    """The capsule id is the HKDF salt, so identical secrets still diverge."""
    secret = b"\x2a" * 32
    assert derive_payload_key(secret, "qsc_alpha") != derive_payload_key(secret, "qsc_beta")


def test_kdf_output_differs_from_the_raw_shared_secret():
    """SP 800-56C forbids using a KEM secret directly as a working key."""
    secret = b"\x2a" * 32
    assert derive_payload_key(secret, "qsc_alpha") != secret
