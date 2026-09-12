"""
Harvest Now, Decrypt Later - live network demonstration.

Sends the SAME payment instruction twice over real HTTPS, through a real
TLS-terminating interception proxy:

    1. The way banks send payments today  - plaintext inside a TLS tunnel.
    2. The way QSC sends them             - sealed in a post-quantum capsule.

Then applies the 2030s threat model to what the interceptor harvested.

Requires the node to be running:

    python -m src.server.run

Then:

    python src/demo/hndl_demo.py
"""

import json
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import requests

from src.server.tls_config import CERT_PATH, DEFAULT_HOST, DEFAULT_PORT, PROXY_PORT

API = f"https://{DEFAULT_HOST}:{DEFAULT_PORT}"
PROXY = f"https://{DEFAULT_HOST}:{PROXY_PORT}"
RULE = "=" * 78


def banner(text: str) -> None:
    print(f"\n{RULE}\n {text}\n{RULE}")


def main() -> int:
    session = requests.Session()
    session.verify = CERT_PATH

    banner("HARVEST NOW, DECRYPT LATER - LIVE NETWORK DEMONSTRATION")
    print(f"  Settlement API     {API}")
    print(f"  Interception proxy {PROXY}  (terminates TLS, records every byte)")

    try:
        health = session.get(f"{API}/api/v1/health", timeout=10).json()
    except requests.RequestException as exc:
        print(f"\n  Cannot reach the settlement node: {exc}")
        print("  Start it first with:  python -m src.server.run")
        return 1
    print(f"  Node status        {health['status']} (up {health['uptime_seconds']}s)")

    session.delete(f"{PROXY}/_intercept/captures", timeout=10)
    keys = session.post(f"{API}/api/v1/pqc/keys/generate", timeout=30).json()
    print(f"  ML-KEM-768 public  {keys['key_sizes']['ml_kem_768_public_bytes']} bytes "
          f"({keys['timings']['ml_kem_768_keygen_ms']} ms)")
    print(f"  ML-DSA-65 public   {keys['key_sizes']['ml_dsa_65_public_bytes']} bytes "
          f"({keys['timings']['ml_dsa_65_keygen_ms']} ms)")

    # ---- One payment instruction, composed by the client -------------------
    banner("STEP 1  -  THE PAYMENT INSTRUCTION")
    generated = session.post(
        f"{API}/api/v1/payloads/generate", params={"kind": "card"}, timeout=30
    ).json()
    payload = generated["payload_raw"]
    print(f"  {generated['descriptor']['label']}  ({generated['size_bytes']} bytes)")
    for line in payload.splitlines()[:8]:
        print(f"    {line}")

    # ---- Path A: conventional, channel-protected ---------------------------
    banner("STEP 2  -  PATH A: SENT THE WAY BANKS SEND PAYMENTS TODAY")
    resp_a = session.post(
        f"{PROXY}/api/v1/legacy/transfer", json={"payload_raw": payload}, timeout=30
    )
    body_a = resp_a.json()
    print(f"  POST {PROXY}/api/v1/legacy/transfer")
    print(f"  HTTP {resp_a.status_code}  |  transport {body_a['transport']}  |  "
          f"message layer: {body_a['message_layer_protection']}")
    print(f"  Proxy round trip: {resp_a.headers.get('X-Proxy-Round-Trip-Ms')} ms")
    print(f"  Protection model: {body_a['protection_model']}")

    # ---- Path B: capsule-protected ----------------------------------------
    banner("STEP 3  -  PATH B: SENT AS A QUANTUM SECURITY CAPSULE")
    cap = session.post(
        f"{API}/api/v1/capsule/encapsulate", json={"payload_raw": payload}, timeout=60
    ).json()
    print(f"  Capsule {cap['capsule_id']}")
    print(f"  Built in {cap['timings']['capsule_build_ms']} ms  |  "
          f"{cap['plaintext_size_bytes']} B payload -> {cap['wire_size_bytes']} B on the wire "
          f"({cap['expansion_ratio']}x)")
    sizes = cap["component_sizes"]
    print(f"  ML-KEM ciphertext {sizes['kem_ciphertext_bytes']} B  |  "
          f"ML-DSA signature {sizes['signature_bytes']} B  |  "
          f"GCM tag {sizes['gcm_tag_bytes']} B")

    resp_b = session.post(
        f"{PROXY}/api/v1/capsule/settle", json={"capsule": cap["capsule"]}, timeout=60
    )
    settled = resp_b.json()
    print(f"\n  POST {PROXY}/api/v1/capsule/settle  ->  {settled['status']}")
    for stage in settled["stage_diagnostics"]:
        print(f"    stage {stage['stage']}  {stage['name']:<18} {stage['status']:<8} "
              f"{stage['elapsed_us']:>9.1f} us   {stage['control']}")

    # ---- What the interceptor holds ---------------------------------------
    banner("STEP 4  -  WHAT THE INTERCEPTOR HARVESTED")
    captures = session.get(f"{PROXY}/_intercept/captures", timeout=10).json()
    print(f"  {captures['total_flows']} flows, {captures['total_bytes_harvested']} bytes "
          "recorded off the wire")
    for flow in reversed(captures["flows"]):
        print(f"    {flow['capture_id']}  {flow['method']:<5} {flow['path']:<26} "
              f"{flow['request_bytes']:>6} B   {flow['analysis']['protection']}")

    # ---- The future event --------------------------------------------------
    banner("STEP 5  -  2030s: SHOR'S ALGORITHM BREAKS THE ARCHIVED TLS SESSIONS")
    result = session.post(f"{PROXY}/_intercept/quantum-decrypt", timeout=30).json()
    tm = result["threat_model"]
    print(f"  Event      {tm['event']}")
    print(f"  Status     {tm['status']}")
    print(f"  TLS layer  {tm['tls_layer']}   (captured bytes are real: {tm['captured_bytes_are_real']})")

    for breach in result["breached"]:
        print(f"\n  [ BREACHED ]  {breach['capture_id']}  {breach['path']}")
        print(f"     Sensitive fields recovered in the clear: "
              f"{', '.join(breach['recovered_plaintext_fields'])}")
        recovered = breach.get("recovered_body", {})
        inner = recovered.get("payload_raw", json.dumps(recovered))
        for line in str(inner).splitlines()[:7]:
            print(f"       {line}")

    for held in result["resisted"]:
        print(f"\n  [ RESISTED ]  {held['capture_id']}  {held['path']}")
        print(f"     Routing metadata visible: "
              f"{held['visible_metadata']['sender_id']} -> {held['visible_metadata']['recipient_id']}")
        print("     Payload remains:")
        for name, blob in held["opaque_ciphertext"].items():
            print(f"       {name:<20} {blob['bytes']:>5} B ciphertext   {blob['preview'][:34]}...")
        hardness = held["residual_hardness"]
        print(f"     Underlying problem: {hardness['problem']}")
        print(f"     Shor applicable:    {hardness['shor_applicable']}  - {hardness['reason']}")

    banner("CONCLUSION")
    print(f"  {result['conclusion']}")
    print("\n  Both payments crossed the same wire, through the same proxy, under the")
    print("  same TLS. The difference is where the protection lives: in the channel,")
    print("  or in the message itself.")
    print(RULE)
    return 0


if __name__ == "__main__":
    sys.exit(main())
