"""
Tests for the settlement API surface.

Driven through FastAPI's TestClient, so these exercise the real routing,
validation and serialisation without needing a TLS listener - the transport
itself is covered by test_tls_handshake.py.
"""

import base64

import pytest
from fastapi.testclient import TestClient

from src.server.api import app


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as test_client:
        test_client.post("/api/v1/pqc/keys/generate")
        yield test_client


def build_capsule(client, kind="pacs008"):
    response = client.post("/api/v1/capsule/encapsulate", json={"payload_kind": kind})
    assert response.status_code == 200
    return response.json()


# --------------------------------------------------------------- basics

def test_health_reports_operational(client):
    body = client.get("/api/v1/health").json()
    assert body["status"] == "OPERATIONAL"
    assert body["keys_loaded"] is True


def test_responses_carry_processing_telemetry(client):
    response = client.get("/api/v1/health")
    assert float(response.headers["X-QSC-Process-Time-Ms"]) >= 0
    assert response.headers["X-QSC-Version"] == "1.0"


def test_parameters_expose_the_nist_standards(client):
    body = client.get("/api/v1/pqc/parameters").json()
    assert body["kem"]["standard"] == "NIST FIPS 203"
    assert body["dsa"]["standard"] == "NIST FIPS 204"
    assert body["hash"]["standard"] == "NIST FIPS 202"


def test_keygen_returns_standard_sized_public_keys(client):
    body = client.post("/api/v1/pqc/keys/generate").json()
    assert body["key_sizes"]["ml_kem_768_public_bytes"] == 1184
    assert body["key_sizes"]["ml_dsa_65_public_bytes"] == 1952
    assert len(base64.b64decode(body["receiver_kem_pub"])) == 1184
    assert body["timings"]["ml_kem_768_keygen_ms"] > 0


# -------------------------------------------------------------- payloads

@pytest.mark.parametrize("kind", ["pacs008", "mt103", "card"])
def test_payload_generation_produces_fresh_messages(client, kind):
    first = client.post("/api/v1/payloads/generate", params={"kind": kind}).json()
    second = client.post("/api/v1/payloads/generate", params={"kind": kind}).json()

    assert first["size_bytes"] > 0
    assert first["payload_raw"] != second["payload_raw"], "payloads must not be canned"


def test_mt103_uses_swift_fin_block_structure(client):
    body = client.post("/api/v1/payloads/generate", params={"kind": "mt103"}).json()
    raw = body["payload_raw"]
    assert raw.startswith("{1:F01")
    for tag in (":20:", ":32A:", ":50K:", ":59:", ":71A:"):
        assert tag in raw


def test_pacs008_carries_iso20022_namespace(client):
    body = client.post("/api/v1/payloads/generate", params={"kind": "pacs008"}).json()
    assert "pacs.008.001.08" in body["payload_raw"]


# --------------------------------------------------------------- capsules

def test_encapsulate_returns_a_complete_capsule(client):
    body = build_capsule(client)

    assert body["capsule"]["version"] == "QSC-1.0"
    assert body["component_sizes"]["kem_ciphertext_bytes"] == 1088
    assert body["component_sizes"]["signature_bytes"] == 3309
    assert body["component_sizes"]["gcm_tag_bytes"] == 16
    assert body["timings"]["capsule_build_ms"] > 0


def test_wire_format_decodes_to_the_reported_size(client):
    body = build_capsule(client)
    wire = base64.b64decode(body["wire_format_b64"])
    assert len(wire) == body["wire_size_bytes"]


def test_field_offsets_point_at_the_right_bytes(client):
    """Offsets drive the hex inspector, so they must be exact, not approximate."""
    body = build_capsule(client)
    wire = base64.b64decode(body["wire_format_b64"])

    for name, span in body["field_offsets"].items():
        segment = wire[span["value_start"]:span["value_end"]].decode()
        expected = body["capsule"][name]
        if isinstance(expected, str):
            assert segment == f'"{expected}"', f"offset mismatch for {name}"


def test_settle_runs_all_five_stages_and_releases_the_payload(client):
    body = build_capsule(client, kind="mt103")
    result = client.post("/api/v1/capsule/settle", json={"capsule": body["capsule"]}).json()

    assert result["status"] == "SETTLED"
    assert [s["stage"] for s in result["stage_diagnostics"]] == [1, 2, 3, 4, 5]
    assert all(s["status"] == "PASS" for s in result["stage_diagnostics"])
    assert result["decrypted_payload"].startswith("{1:F01")


def test_settle_rejects_a_malformed_capsule(client):
    response = client.post("/api/v1/capsule/settle", json={"capsule": {"version": "QSC-1.0"}})
    assert response.status_code == 400


def test_hexdump_rows_match_the_wire_bytes(client):
    body = build_capsule(client)
    dump = client.get(f"/api/v1/capsule/{body['capsule_id']}/hexdump", params={"limit": 64}).json()

    assert dump["total_bytes"] == body["wire_size_bytes"]
    assert dump["rows"][0]["ascii"].startswith('{"capsule_id"')
    assert len(dump["rows"][0]["hex"]) == 16


def test_hexdump_for_an_unknown_capsule_is_a_404(client):
    assert client.get("/api/v1/capsule/qsc_missing/hexdump").status_code == 404


# ------------------------------------------------------------ attack lab

def test_tampering_a_capsule_is_rejected(client):
    body = build_capsule(client)
    offset = body["field_offsets"]["payload_ciphertext"]["value_start"] + 2

    result = client.post("/api/v1/attack/tamper", json={
        "capsule_id": body["capsule_id"], "byte_offset": offset, "bit": 1,
    }).json()

    assert result["status"] == "REJECTED"
    assert result["affected_field"] == "payload_ciphertext"
    assert result["byte_before"] != result["byte_after"]


def test_tamper_offset_beyond_the_capsule_is_a_400(client):
    body = build_capsule(client)
    response = client.post("/api/v1/attack/tamper", json={
        "capsule_id": body["capsule_id"], "byte_offset": 10_000_000, "bit": 0,
    })
    assert response.status_code == 400


def test_replaying_a_settled_capsule_is_rejected(client):
    body = build_capsule(client)
    client.post("/api/v1/capsule/settle", json={"capsule": body["capsule"]})

    result = client.post("/api/v1/attack/replay",
                         params={"capsule_id": body["capsule_id"]}).json()
    assert result["status"] == "REJECTED"
    assert "Replay" in result["reason"]


# ------------------------------------------------------------- legacy path

def test_legacy_endpoint_echoes_plaintext_and_flags_the_weakness(client):
    body = client.post("/api/v1/legacy/transfer", json={"payload_kind": "card"}).json()

    assert body["protection_model"] == "CHANNEL_SECURITY_ONLY"
    assert body["message_layer_protection"] is None
    assert '"pan"' in body["payload_echo"]


# -------------------------------------------------------------- telemetry

def test_telemetry_counts_real_activity(client):
    before = client.get("/api/v1/network/telemetry").json()
    build_capsule(client)
    after = client.get("/api/v1/network/telemetry").json()

    assert after["capsules_built"] > before["capsules_built"]
    assert after["api_requests_served"] > before["api_requests_served"]
    assert after["keyset_fingerprints"]["ml_kem_768_public"] is not None
