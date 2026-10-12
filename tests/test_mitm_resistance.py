"""
Tests for resistance to an interception hop.

The central claim of this project is that a capsule crossing a TLS-terminating
proxy leaks nothing but routing metadata, while a conventionally protected
payload leaks everything. These tests assert exactly that, against the same
classification logic the live proxy runs.
"""

import base64
import json

import pytest

from src.capsule import CapsuleBuilder, CapsuleValidator, SecureReceiver
from src.capsule.wire import field_offsets, flip_bit, from_wire_bytes, to_wire_bytes
from src.crypto import MLDSA65, MLKEM768
from src.server.mitm_proxy import _classify
from src.server.payloads import build_payload

SENDER = "BARCGB22XXX"
RECIPIENT = "HDFCINBBXXX"


@pytest.fixture
def keyset():
    dsa_public, dsa_private = MLDSA65.generate_keypair()
    kem_public, kem_private = MLKEM768.generate_keypair()
    return {
        "dsa_public": dsa_public,
        "dsa_private": dsa_private,
        "kem_public": kem_public,
        "kem_private": kem_private,
    }


@pytest.fixture
def payment():
    raw, _ = build_payload("card")
    return raw


def make_capsule(keyset, payload):
    builder = CapsuleBuilder(SENDER, keyset["dsa_private"])
    return builder.build_capsule(RECIPIENT, keyset["kem_public"], payload)


# ------------------------------------------------ what an interceptor sees

def test_interceptor_recovers_everything_from_a_tls_only_payload(payment):
    """The control group: plaintext in the tunnel is plaintext at the hop."""
    body = json.dumps({"payload_raw": payment.decode()}).encode()
    verdict = _classify(body)

    assert verdict["protection"] == "TLS_ONLY"
    assert verdict["exposure"] == "FULL"
    assert "pan" in verdict["recovered_plaintext_fields"]
    assert "cvv" in verdict["recovered_plaintext_fields"]


def test_interceptor_recovers_no_payload_fields_from_a_capsule(keyset, payment):
    capsule = make_capsule(keyset, payment)
    body = json.dumps({"capsule": capsule.to_dict()}).encode()
    verdict = _classify(body)

    assert verdict["protection"] == "QSC_CAPSULE"
    assert verdict["exposure"] == "NONE"
    assert verdict["recovered_plaintext_fields"] == []


def test_capsule_body_contains_no_plaintext_payment_data(keyset, payment):
    """
    The strongest form of the claim: search the raw wire bytes for the actual
    secret values and confirm none of them appear.
    """
    record = json.loads(payment)
    capsule = make_capsule(keyset, payment)
    wire = to_wire_bytes(capsule)

    for field in ("pan", "cvv", "cardholder", "merchant_id"):
        # For short 3-digit values like CVV, check the quoted JSON value to avoid
        # false-positive substring matches inside 6 KB of random Base64/hex bytes.
        secret = f'"{record[field]}"'.encode() if field == "cvv" else str(record[field]).encode()
        assert secret not in wire, f"{field} leaked into the capsule wire format"


def test_only_routing_metadata_is_visible_to_the_interceptor(keyset, payment):
    capsule = make_capsule(keyset, payment)
    verdict = _classify(json.dumps({"capsule": capsule.to_dict()}).encode())

    visible = verdict["visible_metadata"]
    assert visible["sender_id"] == SENDER
    assert visible["recipient_id"] == RECIPIENT
    # Everything else the interceptor holds is sized ciphertext, not content.
    assert verdict["opaque_ciphertext"]["kem_ciphertext"]["bytes"] == 1088
    assert verdict["opaque_ciphertext"]["payload_tag"]["bytes"] == 16


# ------------------------------------------- survival across the network

def test_capsule_settles_after_a_full_wire_roundtrip(keyset, payment):
    """A capsule serialised, relayed and re-parsed must still validate."""
    capsule = make_capsule(keyset, payment)
    relayed = from_wire_bytes(to_wire_bytes(capsule))

    receiver = SecureReceiver(RECIPIENT, keyset["kem_private"], CapsuleValidator())
    ok, plaintext, message = receiver.process_and_decrypt(relayed, keyset["dsa_public"])

    assert ok is True, message
    assert plaintext == payment


def test_proxy_cannot_decrypt_without_the_recipient_private_key(keyset, payment):
    """An interceptor holding the capsule and its own PQC keys still gets nothing."""
    capsule = make_capsule(keyset, payment)
    _, attacker_kem_private = MLKEM768.generate_keypair()

    attacker = SecureReceiver(RECIPIENT, attacker_kem_private, CapsuleValidator())
    ok, plaintext, message = attacker.process_and_decrypt(capsule, keyset["dsa_public"])

    assert ok is False
    assert plaintext == b""
    assert "decryption failed" in message.lower()


# ------------------------------------------------- active tampering at the hop

def test_single_bit_flip_in_ciphertext_is_caught_by_the_integrity_lock(keyset, payment):
    capsule = make_capsule(keyset, payment)
    wire = to_wire_bytes(capsule)
    offset = field_offsets(capsule)["payload_ciphertext"]["value_start"] + 1

    tampered = from_wire_bytes(flip_bit(wire, offset, bit=1))
    report = CapsuleValidator().validate_detailed(tampered, keyset["dsa_public"])

    assert report.accepted is False
    failed = [s for s in report.stages if s.status == "FAIL"]
    assert len(failed) == 1
    assert failed[0].stage == 4
    assert failed[0].name == "Integrity Lock"


def test_single_bit_flip_in_signature_is_caught_by_ml_dsa(keyset, payment):
    """
    The signature is excluded from the integrity hash, so tampering there slips
    past stage 4 and must be stopped by lattice verification at stage 5.
    """
    capsule = make_capsule(keyset, payment)
    wire = to_wire_bytes(capsule)
    offset = field_offsets(capsule)["signature"]["value_start"] + 40

    tampered = from_wire_bytes(flip_bit(wire, offset, bit=2))
    report = CapsuleValidator().validate_detailed(tampered, keyset["dsa_public"])

    assert report.accepted is False
    failed = [s for s in report.stages if s.status == "FAIL"]
    assert failed[0].stage == 5
    assert failed[0].name == "Origin Signature"


def test_replayed_capsule_is_rejected_at_stage_three(keyset, payment):
    capsule = make_capsule(keyset, payment)
    validator = CapsuleValidator()

    assert validator.validate_detailed(capsule, keyset["dsa_public"]).accepted is True

    second = validator.validate_detailed(capsule, keyset["dsa_public"])
    assert second.accepted is False
    failed = [s for s in second.stages if s.status == "FAIL"]
    assert failed[0].stage == 3
    # Later, more expensive stages must not even run once a control has failed.
    assert [s.status for s in second.stages[3:]] == ["SKIPPED", "SKIPPED"]


def test_capsule_resigned_by_a_rogue_key_is_rejected(keyset, payment):
    """An attacker who rebuilds the capsule with their own signing key fails."""
    _, rogue_private = MLDSA65.generate_keypair()
    rogue = CapsuleBuilder(SENDER, rogue_private).build_capsule(
        RECIPIENT, keyset["kem_public"], payment
    )

    report = CapsuleValidator().validate_detailed(rogue, keyset["dsa_public"])
    assert report.accepted is False
    assert [s for s in report.stages if s.status == "FAIL"][0].stage == 5


def test_swapped_kem_ciphertext_fails_gcm_authentication(keyset, payment):
    """
    Substituting another capsule's KEM ciphertext changes the derived key. The
    integrity hash is recomputed by the attacker, so stage 4 passes - but
    AES-GCM tag verification still fails closed.
    """
    victim = make_capsule(keyset, payment)
    other = make_capsule(keyset, payment)

    victim.kem_ciphertext = other.kem_ciphertext
    receiver = SecureReceiver(RECIPIENT, keyset["kem_private"], CapsuleValidator())
    ok, _, message = receiver.decrypt_payload(victim)

    assert ok is False
    assert "decryption failed" in message.lower()


def test_capsule_expansion_is_bounded(keyset, payment):
    """
    Post-quantum armour is not free. The overhead is fixed (KEM ciphertext plus
    signature plus headers), so it must stay flat rather than scale with payload.
    """
    capsule = make_capsule(keyset, payment)
    wire = to_wire_bytes(capsule)
    overhead = len(wire) - len(payment)

    kem_bytes = len(base64.b64decode(capsule.kem_ciphertext))
    sig_bytes = len(base64.b64decode(capsule.signature))
    assert kem_bytes == 1088
    assert sig_bytes == 3309
    # Base64 inflates by 4/3; headers and policy add the remainder.
    assert overhead < 8000
