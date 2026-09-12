"""
Interception proxy - the "harvest now, decrypt later" demonstrator.

This is a genuine TLS-terminating forward proxy, not a mock. A client connects
to it over TLS, the proxy decrypts the request, records the raw bytes, then
opens its own TLS connection to the settlement API and relays the response.

That architecture is not exotic: corporate TLS inspection appliances, API
gateways, service meshes, CDN edges and load balancers all terminate TLS
exactly this way. Any one of them - or a state-level adversary holding a
harvested session key - sees precisely what this proxy records.

The honest division of labour:

  * REAL   - the network hops, the TLS termination, the captured bytes.
  * FUTURE - the assumption that a quantum computer has recovered the session
             key of a recorded TLS stream. That is the 2030s threat model, and
             it is the only simulated element here.

What the demonstration shows is that this assumption is devastating for a
channel-encrypted payload and inert against a capsule-encrypted one.
"""

import base64
import json
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import httpx
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.server import tls_config

UPSTREAM = f"https://{tls_config.DEFAULT_HOST}:{tls_config.DEFAULT_PORT}"
MAX_CAPTURES = 100

# Capsule fields that are opaque ciphertext to anyone without the ML-KEM private key.
OPAQUE_FIELDS = ("kem_ciphertext", "payload_ciphertext", "payload_tag", "nonce")

# Field names that constitute a material data breach if recovered in plaintext.
SENSITIVE_MARKERS = (
    "pan", "cvv", "iban", "account", "cardholder", "amount", "bicfi",
    "debtor", "creditor", ":50k:", ":59:", ":32a:",
)


class CaptureStore:
    """Ring buffer of intercepted network flows."""

    def __init__(self) -> None:
        self.flows: List[Dict[str, Any]] = []
        self.total_bytes = 0
        self.sequence = 0

    def record(self, flow: Dict[str, Any]) -> Dict[str, Any]:
        self.sequence += 1
        flow["capture_id"] = f"cap_{self.sequence:05d}"
        self.flows.insert(0, flow)
        self.total_bytes += flow.get("request_bytes", 0) + flow.get("response_bytes", 0)
        del self.flows[MAX_CAPTURES:]
        return flow

    def clear(self) -> None:
        self.flows.clear()
        self.total_bytes = 0


CAPTURES = CaptureStore()


def _classify(body: bytes) -> Dict[str, Any]:
    """
    Determines what an interceptor actually recovers from a captured body.

    Returns a verdict describing the exposure, plus the concrete evidence: the
    fields recovered in the clear, or the ciphertext blobs that remain opaque.
    """
    if not body:
        return {"protection": "EMPTY", "exposure": "NONE", "detail": "No request body."}

    try:
        parsed = json.loads(body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return {
            "protection": "OPAQUE_BINARY",
            "exposure": "NONE",
            "detail": "Body is not parseable text; nothing legible recovered.",
        }

    capsule = parsed.get("capsule") if isinstance(parsed, dict) else None
    if isinstance(capsule, dict) and "kem_ciphertext" in capsule:
        blobs = {}
        for name in OPAQUE_FIELDS:
            value = capsule.get(name, "")
            try:
                raw_len = len(base64.b64decode(value))
            except Exception:
                raw_len = 0
            blobs[name] = {
                "bytes": raw_len,
                "preview": (value[:48] + "...") if len(value) > 48 else value,
            }
        return {
            "protection": "QSC_CAPSULE",
            "exposure": "NONE",
            "detail": (
                "Payload is sealed under AES-256-GCM with a key established by "
                "ML-KEM-768. Recovering it requires solving Module-LWE, which "
                "Shor's algorithm does not address."
            ),
            "recovered_plaintext_fields": [],
            "opaque_ciphertext": blobs,
            "visible_metadata": {
                key: capsule.get(key)
                for key in ("capsule_id", "sender_id", "recipient_id", "issued_at", "expires_at")
            },
        }

    flat = json.dumps(parsed).lower()
    leaked = sorted({m for m in SENSITIVE_MARKERS if m in flat})
    return {
        "protection": "TLS_ONLY",
        "exposure": "FULL",
        "detail": (
            "Payload travelled as plaintext inside the TLS tunnel. Once the "
            "tunnel is stripped, every field is readable."
        ),
        "recovered_plaintext_fields": leaked,
        "recovered_body": parsed,
    }


proxy_app = FastAPI(
    title="QSC Interception Proxy",
    description=(
        "A TLS-terminating man-in-the-middle hop that records every byte it "
        "relays, used to demonstrate harvest-now-decrypt-later exposure."
    ),
    docs_url="/_intercept/docs",
    openapi_url="/_intercept/openapi.json",
)


# The workbench is served from the settlement node on :8443 while the proxy
# listens on :8444, so its control endpoints are cross-origin to the browser.
proxy_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Intercepted-By", "X-Proxy-Round-Trip-Ms", "X-QSC-Process-Time-Ms"],
)


@proxy_app.get("/_intercept/captures")
async def list_captures(limit: int = 25) -> Dict[str, Any]:
    """Returns the flows harvested so far, newest first."""
    return {
        "total_flows": len(CAPTURES.flows),
        "total_bytes_harvested": CAPTURES.total_bytes,
        "upstream": UPSTREAM,
        "flows": CAPTURES.flows[:limit],
    }


@proxy_app.delete("/_intercept/captures")
async def clear_captures() -> Dict[str, Any]:
    """Empties the attacker's harvest archive."""
    CAPTURES.clear()
    return {"status": "CLEARED", "total_flows": 0}


@proxy_app.post("/_intercept/quantum-decrypt")
async def quantum_decrypt() -> Dict[str, Any]:
    """
    Applies the 2030s threat model to everything harvested so far.

    Assumption: a cryptographically relevant quantum computer has run Shor's
    algorithm against the recorded ECDHE handshakes, recovering every TLS
    session key. The outer tunnel is therefore gone.

    The captured bytes are real. What follows is what each flow yields once
    that tunnel is stripped away.
    """
    breached: List[Dict[str, Any]] = []
    resisted: List[Dict[str, Any]] = []

    for flow in CAPTURES.flows:
        verdict = flow.get("analysis", {})
        entry = {
            "capture_id": flow["capture_id"],
            "captured_at": flow["captured_at"],
            "path": flow["path"],
            "request_bytes": flow["request_bytes"],
            "protection": verdict.get("protection"),
            "detail": verdict.get("detail"),
        }
        if verdict.get("exposure") == "FULL":
            entry["recovered_plaintext_fields"] = verdict.get("recovered_plaintext_fields", [])
            entry["recovered_body"] = verdict.get("recovered_body")
            breached.append(entry)
        elif verdict.get("protection") == "QSC_CAPSULE":
            entry["opaque_ciphertext"] = verdict.get("opaque_ciphertext")
            entry["visible_metadata"] = verdict.get("visible_metadata")
            entry["residual_hardness"] = {
                "problem": "Module Learning With Errors over R_q = Z_q[X]/(X^256+1), q=3329",
                "shor_applicable": False,
                "reason": (
                    "Shor's algorithm solves hidden subgroup problems in abelian "
                    "groups - integer factorisation and discrete logarithms. "
                    "Lattice problems expose no such structure."
                ),
                "best_known_quantum_attack": "Grover-accelerated sieving, sub-quadratic speedup only",
            }
            resisted.append(entry)

    return {
        "threat_model": {
            "event": "Shor's algorithm recovers ECDHE session keys from archived TLS traffic",
            "status": "SIMULATED FUTURE CAPABILITY",
            "captured_bytes_are_real": True,
            "tls_layer": "STRIPPED",
        },
        "flows_analysed": len(CAPTURES.flows),
        "breached_count": len(breached),
        "resisted_count": len(resisted),
        "breached": breached,
        "resisted": resisted,
        "conclusion": (
            f"{len(breached)} channel-protected flow(s) fully exposed; "
            f"{len(resisted)} capsule-protected flow(s) remain sealed."
        ),
        "analysed_at": datetime.now(timezone.utc).isoformat(),
    }


@proxy_app.api_route(
    "/{full_path:path}",
    methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
)
async def intercept_and_forward(full_path: str, request: Request) -> Response:
    """
    Relays a request upstream, recording both directions on the way through.

    The proxy holds the decrypted request body in memory because it terminated
    TLS. That is the whole point: a hop like this one is a legitimate part of
    most production architectures, and it is a total compromise for any payload
    whose only protection was the tunnel.
    """
    body = await request.body()
    started = time.perf_counter()

    target = f"{UPSTREAM}/{full_path}"
    forward_headers = {
        k: v for k, v in request.headers.items()
        if k.lower() not in ("host", "content-length")
    }
    forward_headers["X-Forwarded-By"] = "QSC-Interception-Proxy"

    try:
        async with httpx.AsyncClient(
            verify=tls_config.CERT_PATH, timeout=30.0
        ) as client:
            upstream_response = await client.request(
                request.method,
                target,
                content=body,
                headers=forward_headers,
                params=dict(request.query_params),
            )
        response_body = upstream_response.content
        status_code = upstream_response.status_code
        upstream_error: Optional[str] = None
    except httpx.HTTPError as exc:
        response_body = json.dumps(
            {"error": "upstream_unreachable", "detail": str(exc)}
        ).encode()
        status_code = 502
        upstream_error = str(exc)

    elapsed_ms = (time.perf_counter() - started) * 1000

    CAPTURES.record(
        {
            "captured_at": datetime.now(timezone.utc).isoformat(),
            "method": request.method,
            "path": f"/{full_path}",
            "client": request.client.host if request.client else "unknown",
            "upstream": target,
            "status_code": status_code,
            "request_bytes": len(body),
            "response_bytes": len(response_body),
            "round_trip_ms": round(elapsed_ms, 3),
            "tls_terminated_at_proxy": True,
            "upstream_error": upstream_error,
            "request_preview": body[:220].decode("utf-8", errors="replace"),
            "analysis": _classify(body),
        }
    )

    passthrough = {
        k: v for k, v in (
            upstream_response.headers.items() if upstream_error is None else {}.items()
        )
        if k.lower() not in ("content-length", "content-encoding", "transfer-encoding")
    }
    passthrough["X-Intercepted-By"] = "QSC-Interception-Proxy"
    passthrough["X-Proxy-Round-Trip-Ms"] = f"{elapsed_ms:.3f}"

    return Response(
        content=response_body,
        status_code=status_code,
        headers=passthrough,
        media_type=passthrough.get("content-type", "application/json"),
    )
