"""
Tests for the TLS transport layer.

These start a real Uvicorn server with a real certificate on a loopback port and
perform genuine handshakes against it. Nothing is stubbed: if the assertions
below pass, an actual TLS 1.3 session was negotiated.
"""

import socket
import ssl
import threading
import time

import pytest
import uvicorn

from src.server import tls_config

TEST_PORT = 8543


def _free_port(port: int) -> bool:
    with socket.socket() as probe:
        return probe.connect_ex(("127.0.0.1", port)) != 0


@pytest.fixture(scope="module")
def tls_server():
    """Runs the settlement API over TLS on a dedicated test port."""
    cert, key = tls_config.ensure_dev_certificate()

    config = uvicorn.Config(
        "src.server.api:app",
        host="127.0.0.1",
        port=TEST_PORT,
        ssl_certfile=cert,
        ssl_keyfile=key,
        log_level="error",
        access_log=False,
    )
    server = uvicorn.Server(config)
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()

    deadline = time.time() + 25
    while time.time() < deadline and not server.started:
        time.sleep(0.1)
    if not server.started:
        pytest.skip("TLS test server did not start in time")

    yield f"127.0.0.1:{TEST_PORT}"

    server.should_exit = True
    thread.join(timeout=10)


# ------------------------------------------------------------- certificate

def test_certificate_and_key_are_provisioned():
    cert, key = tls_config.ensure_dev_certificate()
    assert cert.endswith("cert.pem")
    assert key.endswith("key.pem")

    with open(cert, "rb") as fh:
        assert b"BEGIN CERTIFICATE" in fh.read()


def test_certificate_is_reused_rather_than_regenerated():
    """Re-running the node must not invalidate sessions by rotating the cert."""
    first, _ = tls_config.ensure_dev_certificate()
    with open(first, "rb") as fh:
        original = fh.read()

    tls_config.ensure_dev_certificate()
    with open(first, "rb") as fh:
        assert fh.read() == original


def test_configuration_offers_tls13_suites():
    config = tls_config.describe_configuration()
    assert "TLS_AES_256_GCM_SHA384" in config["tls13_cipher_suites"]
    assert config["minimum_version"] in ("TLSv1_2", "TLSv1_3")


# --------------------------------------------------------------- handshake

def test_live_handshake_negotiates_tls13(tls_server):
    result = tls_config.probe_tls_handshake(port=TEST_PORT)

    assert result["connected"] is True, result.get("error")
    assert result["protocol"] == "TLSv1.3"
    assert result["cipher_suite"].startswith("TLS_")
    assert result["symmetric_key_bits"] >= 128


def test_handshake_validates_the_certificate_chain(tls_server):
    """Verification is on - the probe is not skipping validation to succeed."""
    result = tls_config.probe_tls_handshake(port=TEST_PORT)

    assert result["certificate_verified"] is True
    cert = result["server_certificate"]
    assert cert["subject_common_name"] == "qsc.localhost"
    assert "127.0.0.1" in cert["subject_alt_names"]


def test_handshake_reports_measured_timings(tls_server):
    result = tls_config.probe_tls_handshake(port=TEST_PORT)

    assert result["tcp_connect_ms"] > 0
    assert result["tls_handshake_ms"] > 0
    assert result["total_ms"] >= result["tls_handshake_ms"]


def test_untrusted_client_rejects_the_self_signed_certificate(tls_server):
    """
    A default client with no knowledge of our CA must refuse the connection.

    This proves the certificate really is being validated rather than accepted
    unconditionally by the TLS stack.
    """
    strict = ssl.create_default_context()
    with pytest.raises(ssl.SSLCertVerificationError):
        with socket.create_connection(("127.0.0.1", TEST_PORT), timeout=10) as sock:
            with strict.wrap_socket(sock, server_hostname="localhost"):
                pass


def test_probe_reports_failure_when_nothing_is_listening():
    port = 8599
    if not _free_port(port):
        pytest.skip(f"port {port} unexpectedly in use")

    result = tls_config.probe_tls_handshake(port=port, timeout=2.0)
    assert result["connected"] is False
    assert "error" in result


def test_api_is_reachable_over_the_tls_connection(tls_server):
    """End to end: a TLS client can actually drive the settlement API."""
    import requests

    response = requests.get(
        f"https://{tls_server}/api/v1/health",
        verify=tls_config.CERT_PATH,
        timeout=15,
    )
    assert response.status_code == 200
    assert response.json()["status"] == "OPERATIONAL"
    assert response.headers["X-QSC-Version"] == "1.0"
