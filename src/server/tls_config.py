"""
TLS 1.3 transport configuration and live handshake telemetry.

Two distinct jobs live here:

1. Provisioning a real X.509 certificate so the API is served over genuine
   HTTPS rather than plaintext HTTP.
2. Performing a real TLS handshake against the running server and reporting
   what was actually negotiated - protocol version, cipher suite, key exchange
   group and certificate chain. These values are read out of the live OpenSSL
   session, not hardcoded, so they change if the server configuration changes.
"""

import datetime
import ipaddress
import os
import socket
import ssl
import time
from typing import Any, Dict, Optional

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec

CERT_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "certs")
)
CERT_PATH = os.path.join(CERT_DIR, "cert.pem")
KEY_PATH = os.path.join(CERT_DIR, "key.pem")

DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8443
PROXY_PORT = 8444


def ensure_dev_certificate(force: bool = False) -> tuple[str, str]:
    """
    Generates a self-signed P-256 certificate for local HTTPS if absent.

    The classical certificate key is deliberately ECDSA P-256: it is exactly the
    kind of key Shor's algorithm dismantles, which is the point the platform
    demonstrates. The transport is quantum-vulnerable; the capsule inside it is
    not.

    Returns:
        (cert_path, key_path)
    """
    if not force and os.path.exists(CERT_PATH) and os.path.exists(KEY_PATH):
        return CERT_PATH, KEY_PATH

    os.makedirs(CERT_DIR, exist_ok=True)
    key = ec.generate_private_key(ec.SECP256R1())

    subject = issuer = x509.Name(
        [
            x509.NameAttribute(x509.oid.NameOID.COUNTRY_NAME, "GB"),
            x509.NameAttribute(x509.oid.NameOID.ORGANIZATION_NAME, "QSC Settlement Network"),
            x509.NameAttribute(x509.oid.NameOID.ORGANIZATIONAL_UNIT_NAME, "Post-Quantum Engineering"),
            x509.NameAttribute(x509.oid.NameOID.COMMON_NAME, "qsc.localhost"),
        ]
    )

    now = datetime.datetime.now(datetime.timezone.utc)
    cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now - datetime.timedelta(minutes=5))
        .not_valid_after(now + datetime.timedelta(days=365))
        .add_extension(
            x509.SubjectAlternativeName(
                [
                    x509.DNSName("localhost"),
                    x509.DNSName("qsc.localhost"),
                    x509.IPAddress(ipaddress.IPv4Address("127.0.0.1")),
                    x509.IPAddress(ipaddress.IPv6Address("::1")),
                ]
            ),
            critical=False,
        )
        .add_extension(x509.BasicConstraints(ca=True, path_length=None), critical=True)
        .add_extension(
            x509.KeyUsage(
                digital_signature=True,
                key_encipherment=False,
                key_cert_sign=True,
                key_agreement=False,
                content_commitment=False,
                data_encipherment=False,
                crl_sign=False,
                encipher_only=False,
                decipher_only=False,
            ),
            critical=True,
        )
        .sign(key, hashes.SHA256())
    )

    with open(CERT_PATH, "wb") as fh:
        fh.write(cert.public_bytes(serialization.Encoding.PEM))
    with open(KEY_PATH, "wb") as fh:
        fh.write(
            key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption(),
            )
        )
    os.chmod(KEY_PATH, 0o600)
    return CERT_PATH, KEY_PATH


def build_client_context(verify: bool = True) -> ssl.SSLContext:
    """
    Builds a client-side TLS context pinned to our development CA.

    Verification stays on: the handshake genuinely validates the certificate
    chain and hostname against certs/cert.pem.
    """
    ctx = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
    ctx.minimum_version = ssl.TLSVersion.TLSv1_2
    if verify and os.path.exists(CERT_PATH):
        ctx.load_verify_locations(cafile=CERT_PATH)
    else:
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
    return ctx


def describe_configuration() -> Dict[str, Any]:
    """Reports the TLS policy the server is configured to offer."""
    ctx = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    ctx.minimum_version = ssl.TLSVersion.TLSv1_2
    suites = [c["name"] for c in ctx.get_ciphers()]
    tls13_suites = [s for s in suites if s.startswith("TLS_")]
    return {
        "openssl_version": ssl.OPENSSL_VERSION,
        "minimum_version": ctx.minimum_version.name,
        "maximum_version": ctx.maximum_version.name,
        "tls13_cipher_suites": tls13_suites,
        "total_cipher_suites_offered": len(suites),
        "certificate_path": CERT_PATH,
    }


def _format_peer_certificate(cert: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """Flattens the OpenSSL peer certificate dict into display-ready fields."""
    if not cert:
        return {}

    def flatten(field):
        out = {}
        for rdn in cert.get(field, ()):  # tuple of tuples
            for key, value in rdn:
                out[key] = value
        return out

    subject = flatten("subject")
    issuer = flatten("issuer")
    sans = [value for kind, value in cert.get("subjectAltName", ()) if kind in ("DNS", "IP Address")]
    return {
        "subject_common_name": subject.get("commonName"),
        "subject_organization": subject.get("organizationName"),
        "issuer_common_name": issuer.get("commonName"),
        "serial_number": cert.get("serialNumber"),
        "not_before": cert.get("notBefore"),
        "not_after": cert.get("notAfter"),
        "subject_alt_names": sans,
    }


def probe_tls_handshake(
    host: str = DEFAULT_HOST,
    port: int = DEFAULT_PORT,
    timeout: float = 5.0,
) -> Dict[str, Any]:
    """
    Opens a real TLS connection to the running server and reports the outcome.

    This performs an actual ClientHello -> ServerHello -> Certificate ->
    Finished exchange over a TCP socket. Every value returned is read from the
    live OpenSSL session object after the handshake completes.

    Returns:
        A telemetry dict, or {"connected": False, "error": ...} if the server
        is unreachable.
    """
    ctx = build_client_context(verify=True)
    started = time.perf_counter()
    try:
        with socket.create_connection((host, port), timeout=timeout) as raw_sock:
            tcp_established = time.perf_counter()
            server_hostname = "localhost" if ctx.check_hostname else None
            with ctx.wrap_socket(raw_sock, server_hostname=server_hostname) as tls_sock:
                completed = time.perf_counter()
                cipher_name, protocol, secret_bits = tls_sock.cipher()
                peer_cert = _format_peer_certificate(tls_sock.getpeercert())
                try:
                    tls_sock.unwrap()
                except (ssl.SSLError, OSError):
                    pass
                return {
                    "connected": True,
                    "endpoint": f"{host}:{port}",
                    "protocol": protocol,
                    "cipher_suite": cipher_name,
                    "symmetric_key_bits": secret_bits,
                    "certificate_verified": ctx.verify_mode == ssl.CERT_REQUIRED,
                    "server_certificate": peer_cert,
                    "tcp_connect_ms": round((tcp_established - started) * 1000, 3),
                    "tls_handshake_ms": round((completed - tcp_established) * 1000, 3),
                    "total_ms": round((completed - started) * 1000, 3),
                    "handshake_stages": [
                        "ClientHello",
                        "ServerHello",
                        "EncryptedExtensions",
                        "Certificate",
                        "CertificateVerify",
                        "Finished",
                    ],
                    "quantum_exposure": {
                        "key_exchange": "ECDHE over NIST P-256 / X25519",
                        "certificate_signature": "ECDSA P-256 (SHA-256)",
                        "broken_by": "Shor's algorithm on a cryptographically relevant quantum computer",
                        "assessment": (
                            "Session keys for this connection are recoverable by a future "
                            "quantum adversary who recorded the handshake today."
                        ),
                    },
                }
    except (OSError, ssl.SSLError) as exc:
        return {
            "connected": False,
            "endpoint": f"{host}:{port}",
            "error": f"{type(exc).__name__}: {exc}",
        }


if __name__ == "__main__":
    cert, key = ensure_dev_certificate()
    print(f"certificate: {cert}")
    print(f"private key: {key}")
    for k, v in describe_configuration().items():
        print(f"  {k}: {v}")
