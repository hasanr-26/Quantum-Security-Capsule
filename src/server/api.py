"""
QSC Settlement Network - live HTTPS API.

Served over real TLS by Uvicorn. Every endpoint performs genuine cryptographic
work on each call: keys come out of ML-KEM/ML-DSA keygen, capsules are built
and verified with real lattice arithmetic, and the timings reported are
measured with a performance counter around the actual operations.
"""

import base64
import json
import os
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from src.capsule import CapsuleBuilder, CapsuleValidator, PolicyMetadata, SecureReceiver
from src.capsule.wire import (
    field_offsets,
    flip_bit,
    from_wire_bytes,
    hex_dump,
    to_wire_bytes,
)
from src.crypto import compute_sha3_512, MLDSA65, MLKEM768
from src.server import tls_config
from src.server.payloads import AVAILABLE_PAYLOADS, build_payload

API_VERSION = "1.0"
SERVICE_NAME = "QSC Settlement Network"


# --------------------------------------------------------------------------
# Session state
# --------------------------------------------------------------------------

class SessionState:
    """
    In-process state for one running instance of the settlement node.

    A production deployment would back the keystore with an HSM and the replay
    cache with a distributed KV store; the security properties are identical,
    only the durability differs.
    """

    def __init__(self) -> None:
        self.started_at = datetime.now(timezone.utc)
        self.sender_id = "BARCGB22XXX"
        self.recipient_id = "HDFCINBBXXX"

        self.dsa_public: Optional[bytes] = None
        self.dsa_private: Optional[bytes] = None
        self.kem_public: Optional[bytes] = None
        self.kem_private: Optional[bytes] = None
        self.keygen_timings: Dict[str, float] = {}

        self.validator = CapsuleValidator()
        self.receiver: Optional[SecureReceiver] = None

        self.capsules: Dict[str, Dict[str, Any]] = {}
        self.settlements: List[Dict[str, Any]] = []
        self.request_count = 0
        self.rejected_count = 0

    def rotate_keys(self) -> Dict[str, float]:
        """Generates a fresh PQC keyset and rebuilds the receiver around it."""
        t0 = time.perf_counter()
        self.dsa_public, self.dsa_private = MLDSA65.generate_keypair()
        dsa_ms = (time.perf_counter() - t0) * 1000

        t0 = time.perf_counter()
        self.kem_public, self.kem_private = MLKEM768.generate_keypair()
        kem_ms = (time.perf_counter() - t0) * 1000

        self.receiver = SecureReceiver(
            recipient_id=self.recipient_id,
            recipient_private_kem_key=self.kem_private,
            validator=self.validator,
        )
        self.keygen_timings = {
            "ml_dsa_65_keygen_ms": round(dsa_ms, 3),
            "ml_kem_768_keygen_ms": round(kem_ms, 3),
        }
        return self.keygen_timings

    def ensure_keys(self) -> None:
        if self.dsa_private is None or self.kem_private is None:
            self.rotate_keys()


SESSION = SessionState()


def fingerprint(key: bytes, length: int = 32) -> str:
    """Short SHA3-512 fingerprint used to identify a key in the UI."""
    return compute_sha3_512(key)[:length]


# --------------------------------------------------------------------------
# Request models
# --------------------------------------------------------------------------

class PolicyRequest(BaseModel):
    classification: str = "CONFIDENTIAL"
    jurisdiction: str = "UK"
    max_hops: int = 3
    ttl_seconds: int = Field(default=300, ge=5, le=86400)


class EncapsulateRequest(BaseModel):
    sender_id: Optional[str] = None
    recipient_id: Optional[str] = None
    payload_raw: Optional[str] = None
    payload_kind: str = "pacs008"
    policy: PolicyRequest = Field(default_factory=PolicyRequest)


class SettleRequest(BaseModel):
    capsule: Dict[str, Any]


class TamperRequest(BaseModel):
    capsule_id: str
    byte_offset: int = Field(ge=0)
    bit: int = Field(default=0, ge=0, le=7)


# --------------------------------------------------------------------------
# Application
# --------------------------------------------------------------------------

app = FastAPI(
    title=SERVICE_NAME,
    version=API_VERSION,
    description=(
        "Message-centric post-quantum settlement API. ML-KEM-768 (FIPS 203) "
        "key establishment, ML-DSA-65 (FIPS 204) origin signatures, "
        "AES-256-GCM payload encryption, SHA3-512 integrity locking."
    ),
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_telemetry_headers(request: Request, call_next):
    """Stamps every response with real server-side processing time."""
    start = time.perf_counter()
    response = await call_next(request)
    elapsed_ms = (time.perf_counter() - start) * 1000
    response.headers["X-QSC-Version"] = API_VERSION
    response.headers["X-QSC-Process-Time-Ms"] = f"{elapsed_ms:.3f}"
    response.headers["X-QSC-Node"] = SESSION.recipient_id
    if request.url.path.startswith("/api/"):
        SESSION.request_count += 1
    return response


@app.get("/api/v1/health")
async def health() -> Dict[str, Any]:
    """Liveness probe with uptime."""
    uptime = (datetime.now(timezone.utc) - SESSION.started_at).total_seconds()
    return {
        "status": "OPERATIONAL",
        "service": SERVICE_NAME,
        "api_version": API_VERSION,
        "uptime_seconds": round(uptime, 1),
        "keys_loaded": SESSION.dsa_public is not None,
    }


# --------------------------------------------------------------------------
# PQC key management
# --------------------------------------------------------------------------

@app.get("/api/v1/pqc/parameters")
async def pqc_parameters() -> Dict[str, Any]:
    """Returns the NIST parameter sets in force, for the cryptographic HUD."""
    return {
        "kem": MLKEM768.parameters(),
        "dsa": MLDSA65.parameters(),
        "symmetric": {
            "algorithm": "AES-256-GCM",
            "standard": "NIST SP 800-38D",
            "key_bits": 256,
            "nonce_bits": 96,
            "tag_bits": 128,
        },
        "hash": {
            "algorithm": "SHA3-512",
            "standard": "NIST FIPS 202",
            "construction": "Keccak-f[1600] sponge",
            "digest_bits": 512,
        },
        "kdf": {
            "algorithm": "HKDF-SHA3-512",
            "standard": "NIST SP 800-56C Rev. 2",
        },
    }


@app.post("/api/v1/pqc/keys/generate")
def generate_keys() -> Dict[str, Any]:
    """
    Generates a fresh post-quantum keyset for this settlement node.

    Rotating keys invalidates every capsule built against the previous keyset -
    signatures will fail stage 5 - which is itself a demonstrable property.
    """
    timings = SESSION.rotate_keys()
    return {
        "sender_dsa_pub": base64.b64encode(SESSION.dsa_public).decode(),
        "receiver_kem_pub": base64.b64encode(SESSION.kem_public).decode(),
        "key_fingerprints": {
            "ml_dsa_65_public": fingerprint(SESSION.dsa_public),
            "ml_kem_768_public": fingerprint(SESSION.kem_public),
        },
        "key_sizes": {
            "ml_dsa_65_public_bytes": len(SESSION.dsa_public),
            "ml_dsa_65_private_bytes": len(SESSION.dsa_private),
            "ml_kem_768_public_bytes": len(SESSION.kem_public),
            "ml_kem_768_private_bytes": len(SESSION.kem_private),
        },
        "timings": timings,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }


# --------------------------------------------------------------------------
# Payload catalogue
# --------------------------------------------------------------------------

@app.get("/api/v1/payloads")
async def list_payloads() -> Dict[str, Any]:
    """Lists the financial message formats this node can generate."""
    return {"payloads": AVAILABLE_PAYLOADS}


@app.post("/api/v1/payloads/generate")
def generate_payload(kind: str = "pacs008") -> Dict[str, Any]:
    """Generates a fresh wire message with live identifiers and timestamps."""
    raw, descriptor = build_payload(kind)
    return {
        "descriptor": descriptor,
        "payload_raw": raw.decode("utf-8"),
        "size_bytes": len(raw),
        "sha3_512": compute_sha3_512(raw),
    }


# --------------------------------------------------------------------------
# Capsule lifecycle
# --------------------------------------------------------------------------

@app.post("/api/v1/capsule/encapsulate")
def encapsulate(req: EncapsulateRequest) -> Dict[str, Any]:
    """
    Builds a Quantum Security Capsule around a financial payload.

    Timings are measured around the real primitive calls, so the reported
    figures reflect actual lattice arithmetic cost on this machine.
    """
    SESSION.ensure_keys()

    if req.payload_raw:
        payload_bytes = req.payload_raw.encode("utf-8")
        descriptor = {
            "kind": "custom",
            "label": "Operator-supplied payload",
            "media_type": "text/plain",
        }
    else:
        payload_bytes, descriptor = build_payload(req.payload_kind)

    policy = PolicyMetadata(
        classification=req.policy.classification,
        jurisdiction=req.policy.jurisdiction,
        max_hops=req.policy.max_hops,
    )

    builder = CapsuleBuilder(
        sender_id=req.sender_id or SESSION.sender_id,
        sender_private_dsa_key=SESSION.dsa_private,
    )

    t0 = time.perf_counter()
    capsule = builder.build_capsule(
        recipient_id=req.recipient_id or SESSION.recipient_id,
        recipient_public_kem_key=SESSION.kem_public,
        payload=payload_bytes,
        validity_seconds=req.policy.ttl_seconds,
        policy=policy,
    )
    build_ms = (time.perf_counter() - t0) * 1000

    wire = to_wire_bytes(capsule)
    offsets = field_offsets(capsule)

    SESSION.capsules[capsule.capsule_id] = {
        "capsule": capsule,
        "plaintext": payload_bytes,
        "descriptor": descriptor,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    return {
        "capsule_id": capsule.capsule_id,
        "capsule": capsule.to_dict(),
        "wire_format_b64": base64.b64encode(wire).decode(),
        "wire_size_bytes": len(wire),
        "plaintext_size_bytes": len(payload_bytes),
        "expansion_ratio": round(len(wire) / max(len(payload_bytes), 1), 2),
        "field_offsets": offsets,
        "sha3_hash": capsule.integrity_hash,
        "ml_dsa_sig": capsule.signature[:64] + "...",
        "descriptor": descriptor,
        "timings": {"capsule_build_ms": round(build_ms, 3)},
        "component_sizes": {
            "kem_ciphertext_bytes": len(base64.b64decode(capsule.kem_ciphertext)),
            "signature_bytes": len(base64.b64decode(capsule.signature)),
            "payload_ciphertext_bytes": len(base64.b64decode(capsule.payload_ciphertext)),
            "gcm_tag_bytes": len(base64.b64decode(capsule.payload_tag)),
            "nonce_bytes": len(base64.b64decode(capsule.nonce)),
        },
    }


@app.post("/api/v1/capsule/settle")
def settle(req: SettleRequest, request: Request) -> Dict[str, Any]:
    """
    Runs an inbound capsule through the zero-trust pipeline and settles it.

    Returns the full five-stage diagnostic trace whether the capsule is
    accepted or rejected, so a rejection is as legible as a success.
    """
    SESSION.ensure_keys()

    try:
        capsule = from_wire_bytes(json.dumps(req.capsule).encode("utf-8"))
    except (TypeError, ValueError, KeyError) as exc:
        raise HTTPException(status_code=400, detail=f"Malformed capsule: {exc}")

    t0 = time.perf_counter()
    report, plaintext = SESSION.receiver.settle_with_report(capsule, SESSION.dsa_public)
    validate_ms = round(report.total_us / 1000, 3)
    total_ms = (time.perf_counter() - t0) * 1000
    decrypt_ms = max(total_ms - validate_ms, 0.0)

    decrypted: Optional[str] = (
        plaintext.decode("utf-8", errors="replace") if report.accepted else None
    )

    status = "SETTLED" if report.accepted else "REJECTED"
    if not report.accepted:
        SESSION.rejected_count += 1

    record = {
        "status": status,
        "capsule_id": capsule.capsule_id,
        "sender_id": capsule.sender_id,
        "recipient_id": capsule.recipient_id,
        "reason": report.reason,
        "settled_at": datetime.now(timezone.utc).isoformat(),
        "client": request.client.host if request.client else "unknown",
        "validate_ms": round(validate_ms, 3),
    }
    SESSION.settlements.insert(0, record)
    del SESSION.settlements[200:]

    return {
        "status": status,
        "capsule_id": capsule.capsule_id,
        "stage_diagnostics": report.to_dict()["stages"],
        "reason": report.reason,
        "decrypted_payload": decrypted,
        "timings": {
            "validation_ms": round(validate_ms, 3),
            "decryption_ms": round(decrypt_ms, 3),
            "total_ms": round(validate_ms + decrypt_ms, 3),
        },
        "replay_cache_size": SESSION.validator.replay_cache_size,
    }


@app.get("/api/v1/capsule/{capsule_id}/hexdump")
def capsule_hexdump(capsule_id: str, limit: int = 2048) -> Dict[str, Any]:
    """Returns the capsule's raw wire bytes as hex-dump rows."""
    entry = SESSION.capsules.get(capsule_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Unknown capsule id")
    wire = to_wire_bytes(entry["capsule"])
    return {
        "capsule_id": capsule_id,
        "total_bytes": len(wire),
        "rows": hex_dump(wire, limit=limit),
        "truncated": len(wire) > limit,
        "field_offsets": field_offsets(entry["capsule"]),
    }


# --------------------------------------------------------------------------
# Legacy channel-security endpoint (the control group)
# --------------------------------------------------------------------------

class LegacyTransferRequest(BaseModel):
    """A conventional payment instruction: plaintext JSON, protected only by TLS."""
    payload_raw: Optional[str] = None
    payload_kind: str = "pacs008"


@app.post("/api/v1/legacy/transfer")
def legacy_transfer(req: LegacyTransferRequest) -> Dict[str, Any]:
    """
    Accepts a payment the way essentially every production banking API does today:
    as plaintext inside a TLS tunnel.

    Nothing here is strawmanned - TLS 1.3 with AES-256-GCM is genuinely strong
    transport security, and this endpoint really is protected by it in transit.
    The weakness is structural rather than cryptographic: the protection ends at
    the tunnel. Any TLS-terminating hop, and any future adversary holding a
    harvested session key, reads the body in full.

    Routing a payment through this endpoint via the interception proxy is what
    makes that concrete.
    """
    if req.payload_raw:
        raw = req.payload_raw.encode("utf-8")
        descriptor = {"kind": "custom", "label": "Operator-supplied payload"}
    else:
        raw, descriptor = build_payload(req.payload_kind)

    return {
        "status": "ACCEPTED",
        "protection_model": "CHANNEL_SECURITY_ONLY",
        "transport": "TLS 1.3",
        "message_layer_protection": None,
        "payload_echo": raw.decode("utf-8"),
        "descriptor": descriptor,
        "size_bytes": len(raw),
        "warning": (
            "This payload is plaintext at every TLS termination point and is "
            "recoverable from any archived session whose key is later broken."
        ),
    }


# --------------------------------------------------------------------------
# Attack lab
# --------------------------------------------------------------------------

@app.post("/api/v1/attack/tamper")
def tamper(req: TamperRequest) -> Dict[str, Any]:
    """
    Flips one bit in a capsule on the wire and re-submits it for settlement.

    A single bit is the smallest possible modification. If the integrity lock
    holds against that, it holds against anything larger.
    """
    entry = SESSION.capsules.get(req.capsule_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Unknown capsule id")

    original = to_wire_bytes(entry["capsule"])
    try:
        mutated = flip_bit(original, req.byte_offset, req.bit)
    except (IndexError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    before = original[req.byte_offset]
    after = mutated[req.byte_offset]

    affected_field = None
    for name, span in field_offsets(entry["capsule"]).items():
        if span["key_start"] <= req.byte_offset < span["value_end"]:
            affected_field = name
            break

    try:
        tampered_capsule = from_wire_bytes(mutated)
    except (UnicodeDecodeError, ValueError) as exc:
        return {
            "status": "REJECTED",
            "reason": f"Tampered capsule is no longer parseable JSON: {exc}",
            "byte_offset": req.byte_offset,
            "affected_field": affected_field,
            "byte_before": f"{before:02x}",
            "byte_after": f"{after:02x}",
            "stage_diagnostics": [],
        }

    report = SESSION.validator.validate_detailed(tampered_capsule, SESSION.dsa_public)
    if not report.accepted:
        SESSION.rejected_count += 1

    return {
        "status": "SETTLED" if report.accepted else "REJECTED",
        "reason": report.reason,
        "byte_offset": req.byte_offset,
        "bit": req.bit,
        "affected_field": affected_field,
        "byte_before": f"{before:02x}",
        "byte_after": f"{after:02x}",
        "stage_diagnostics": report.to_dict()["stages"],
    }


@app.post("/api/v1/attack/replay")
def replay(capsule_id: str) -> Dict[str, Any]:
    """Re-submits a previously settled capsule verbatim, as an attacker would."""
    entry = SESSION.capsules.get(capsule_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Unknown capsule id")

    report = SESSION.validator.validate_detailed(entry["capsule"], SESSION.dsa_public)
    if not report.accepted:
        SESSION.rejected_count += 1
    return {
        "status": "SETTLED" if report.accepted else "REJECTED",
        "reason": report.reason,
        "stage_diagnostics": report.to_dict()["stages"],
        "replay_cache_size": SESSION.validator.replay_cache_size,
    }


# --------------------------------------------------------------------------
# Network telemetry
# --------------------------------------------------------------------------

@app.get("/api/v1/network/telemetry")
async def telemetry() -> Dict[str, Any]:
    """Live operational counters for this node."""
    uptime = (datetime.now(timezone.utc) - SESSION.started_at).total_seconds()
    return {
        "node_id": SESSION.recipient_id,
        "uptime_seconds": round(uptime, 1),
        "api_requests_served": SESSION.request_count,
        "capsules_built": len(SESSION.capsules),
        "settlements_recorded": len(SESSION.settlements),
        "capsules_rejected": SESSION.rejected_count,
        "replay_cache_size": SESSION.validator.replay_cache_size,
        "keyset_fingerprints": {
            "ml_dsa_65_public": fingerprint(SESSION.dsa_public) if SESSION.dsa_public else None,
            "ml_kem_768_public": fingerprint(SESSION.kem_public) if SESSION.kem_public else None,
        },
        "keygen_timings": SESSION.keygen_timings,
        "recent_settlements": SESSION.settlements[:12],
    }


@app.get("/api/v1/network/tls")
def tls_telemetry() -> Dict[str, Any]:
    """
    Performs a real TLS handshake against this server and reports the result.

    The server dials itself over the loopback interface, so the values below
    come from an actual OpenSSL session rather than a configuration file.
    """
    return {
        "configuration": tls_config.describe_configuration(),
        "live_handshake": tls_config.probe_tls_handshake(),
        "probed_at": datetime.now(timezone.utc).isoformat(),
    }


# --------------------------------------------------------------------------
# Workbench frontend
# --------------------------------------------------------------------------

FRONTEND_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "frontend")
)

if os.path.isdir(FRONTEND_DIR):
    app.mount(
        "/static",
        StaticFiles(directory=FRONTEND_DIR),
        name="static",
    )

    @app.get("/", include_in_schema=False)
    def workbench() -> FileResponse:
        """Serves the security workbench over the same TLS connection as the API."""
        return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Fails closed with a structured error rather than leaking a stack trace."""
    return JSONResponse(
        status_code=500,
        content={"error": type(exc).__name__, "detail": str(exc)},
    )
