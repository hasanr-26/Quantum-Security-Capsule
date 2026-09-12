# Quantum Security Capsule (QSC)

[![Barclays Innovation Lab](https://img.shields.io/badge/Barclays-Innovation%20Lab-blue.svg)](https://www.barclays.com)
[![NIST PQC](https://img.shields.io/badge/NIST-FIPS%20203%20%7C%20FIPS%20204-green.svg)](https://csrc.nist.gov/projects/post-quantum-cryptography)
[![Tests](https://img.shields.io/badge/tests-69%20passing-brightgreen.svg)](tests/)
[![License](https://img.shields.io/badge/License-MIT-purple.svg)](LICENSE)

> **Message-Centric Post-Quantum Cryptographic Communication Architecture for Financial Infrastructure**

---

## Executive Summary

Today's financial communication protocols — TLS, IPSec, VPNs, REST, gRPC —
encrypt the **connection channel**. An adversary recording that traffic today
("Harvest Now, Decrypt Later") only needs to wait: when a Cryptographically
Relevant Quantum Computer arrives, Shor's algorithm recovers the session keys of
every archived handshake and the historic payloads become readable.

The **Quantum Security Capsule** moves security from the channel to the message.
Every payload becomes a self-contained, post-quantum encrypted, signed,
time-bounded and tamper-evident capsule that is safe on any transport and at
every intermediate hop.

---

## What is actually real here

This matters more than any feature list, so it is stated up front.

| Component | Status |
| :--- | :--- |
| ML-KEM-768 / ML-DSA-65 | **Real.** `kyber-py` and `dilithium-py`, validated against the NIST ACVP test vectors for FIPS 203/204. Genuine lattice arithmetic, standard key sizes, real signature verification. |
| AES-256-GCM, SHA3-512, HKDF | **Real.** From `cryptography` (OpenSSL). |
| TLS 1.3 transport | **Real.** Uvicorn with a real X.509 certificate. The workbench reports the cipher suite negotiated by an actual handshake. |
| Interception proxy | **Real.** A TLS-terminating hop that records the bytes it relays. |
| Financial payloads | **Real formats**, freshly generated per call — ISO 20022 pacs.008 and SWIFT MT103, with live identifiers and a new UETR each time. Counterparties are fictional. |
| Performance figures | **Measured**, not quoted. See [docs/05](docs/05_advantages_performance.md). |
| "Shor's algorithm breaks the archived TLS sessions" | **Modelled.** This is the one simulated element: the 2030s threat applied to genuinely captured bytes. It is labelled as such everywhere it appears in the UI. |

The pure-Python PQC libraries are chosen for auditability over speed. They are
one to two orders of magnitude slower than optimised C; the wrapper classes in
`src/crypto/` are structured so `liboqs` or AWS-LC drops in without touching
anything above them. See the caveat in
[docs/05, §2.4](docs/05_advantages_performance.md).

---

## Cryptographic Stack

| Security Property | Standard / Primitive | Purpose |
| :--- | :--- | :--- |
| Key Encapsulation | **ML-KEM-768** (NIST FIPS 203) | Post-quantum shared secret, fresh per message |
| Digital Signature | **ML-DSA-65** (NIST FIPS 204) | Lattice signature for origin authenticity and non-repudiation |
| Key Derivation | **HKDF-SHA3-512** (NIST SP 800-56C Rev. 2) | Derives the content key from the KEM secret |
| Symmetric Encryption | **AES-256-GCM** (NIST SP 800-38D) | Authenticated payload encryption |
| Integrity Digest | **SHA3-512** (NIST FIPS 202) | Capsule binding and replay token derivation |

---

## Quick Start

```bash
git clone https://github.com/hasanr-26/Quantum-Security-Capsule.git
cd Quantum-Security-Capsule
pip install -r requirements.txt
```

### Launch the settlement node

```bash
python -m src.server.run
```

This generates a local TLS certificate on first run and starts two listeners:

| Service | Address | Role |
| :--- | :--- | :--- |
| Security Workbench + API | `https://127.0.0.1:8443` | Settlement node and UI |
| Interception Proxy | `https://127.0.0.1:8444` | TLS-terminating MITM hop |
| OpenAPI docs | `https://127.0.0.1:8443/api/docs` | Interactive API reference |

The certificate is self-signed, so your browser warns once — accept it to reach
the workbench over genuine TLS.

### The workbench

| Tab | What it does |
| :--- | :--- |
| **01 Settlement** | Build a real capsule from an ISO 20022 / MT103 / card payload and settle it. Shows all five validation stages with microsecond timings, the decrypted payload, and a live network console with per-request latency. |
| **02 Packet Inspector** | Wireshark-style hex dump of the actual wire bytes. Click a field to highlight its exact byte range; flip a single bit and watch which control catches it. |
| **03 3D Visualizer** | Channel security vs message security. Run the quantum attack in each mode and compare outcomes. |
| **04 Interception Lab** | Send the same payment via TLS-only and as a capsule, both through the proxy, then break the archived sessions and compare what the interceptor recovers. |
| **05 Cryptography** | NIST parameter sets in force, and the live TLS session details from a real handshake probe. |

### Command-line demos

```bash
# The headline demo: same payment, two protection models, live network
# (requires the node to be running)
python src/demo/hndl_demo.py

# High-value interbank wire transfer, end to end
python src/demo/banking_transfer.py

# Replay, tampering and signature forgery, all rejected
python src/demo/replay_attack_demo.py

# Capsule over a raw TLS 1.3 socket
python src/demo/tls_qsc_demo.py

# File encryption into a portable .qsc container
python src/demo/file_encrypt_demo.py

# Measured performance of every primitive
python src/demo/benchmark.py
```

### Tests

```bash
pytest tests/ -v
```

| Suite | Covers |
| :--- | :--- |
| `test_pqc_crypto.py` | FIPS 203/204 key sizes, roundtrips, implicit rejection, forgery resistance, KDF separation |
| `test_tls_handshake.py` | Real TLS 1.3 negotiation, certificate chain validation, handshake timings |
| `test_mitm_resistance.py` | Nothing sensitive appears in the wire bytes; bit flips and replays rejected at the right stage |
| `test_settlement_api.py` | Every endpoint, byte-offset accuracy, attack lab behaviour |
| `test_builder.py`, `test_validator.py`, `test_replay_protection.py` | Core capsule lifecycle |

---

## Architecture

```
                 Client App / Originator
                           │
             ┌─────────────┴─────────────┐
             ▼                           ▼
      Message Payload              Policy Metadata
             │                           │
             └─────────────┬─────────────┘
                           │
                Quantum Capsule Builder
     ┌─────────────────────┼─────────────────────┐
     │                     │                     │
 Encrypt (AES-256-GCM) Sign (ML-DSA-65) Key Encapsulation (ML-KEM-768)
     │                     │                     │
     └─────────────────────┼─────────────────────┘
                           │
                Quantum Security Capsule
                           │
     ┌─────────────────────┴─────────────────────┐
     │  REST / Kafka / MQ / TLS - untrusted hops │
     └─────────────────────┬─────────────────────┘
                           │
                Capsule Validator & Receiver
     ┌─────────────────────┼─────────────────────┐
  Verify Sig           Verify Hash          Decapsulate & Decrypt
     └─────────────────────┼─────────────────────┘
                           │
                     Core Banking Engine
```

### Zero-trust validation pipeline

Every capsule passes five controls in order, cheapest first, failing closed at
the first objection. The replay token is consumed only after all five pass.

| Stage | Control | Typical cost |
| :--- | :--- | ---: |
| 1 | Protocol version | ~1 µs |
| 2 | Freshness window (TTL) | ~7 µs |
| 3 | Replay token (single-use SHA3-512) | ~2 µs |
| 4 | Integrity lock (SHA3-512 canonical digest) | ~60 µs |
| 5 | Origin signature (ML-DSA-65) | ~17 ms |

The ordering is the point: junk traffic is discarded for microseconds and never
reaches the expensive lattice verifier.

---

## Project Structure

```
QSC/
├── certs/                        # Generated TLS material (gitignored)
├── docs/                         # Specifications and analysis
├── src/
│   ├── crypto/                   # NIST primitives
│   │   ├── kem.py                #   ML-KEM-768   (FIPS 203)
│   │   ├── dsa.py                #   ML-DSA-65    (FIPS 204)
│   │   ├── kdf.py                #   HKDF-SHA3-512 (SP 800-56C)
│   │   ├── symmetric.py          #   AES-256-GCM  (SP 800-38D)
│   │   └── hashing.py            #   SHA3-512     (FIPS 202)
│   ├── capsule/                  # Capsule lifecycle
│   │   ├── models.py             #   Data model
│   │   ├── builder.py            #   8-step construction pipeline
│   │   ├── validator.py          #   5-stage zero-trust validator
│   │   ├── receiver.py           #   Settlement engine
│   │   └── wire.py               #   Wire format, byte offsets, hex dump
│   ├── server/                   # Live TLS backend
│   │   ├── api.py                #   FastAPI settlement API
│   │   ├── tls_config.py         #   Certificates and handshake telemetry
│   │   ├── mitm_proxy.py         #   Interception proxy
│   │   ├── payloads.py           #   ISO 20022 / MT103 generators
│   │   └── run.py                #   Launcher
│   ├── frontend/                 # Security workbench
│   │   ├── index.html
│   │   ├── css/terminal.css
│   │   └── js/                   #   api_client, hex_inspector, attack_lab,
│   │                             #   visualizer_3d, pipeline_view, workbench
│   ├── demo/                     # Runnable demonstrations
│   └── visualizer/               # Earlier standalone viewer (port 8000)
└── tests/
```

---

## Documentation Index

| # | Deliverable | Location |
| ---: | :--- | :--- |
| 1–3 | Title, Vision, Problem Statement | [docs/01](docs/01_vision_and_problem.md) |
| 4–8 | Existing vs proposed architecture, workflow, components, capsule internals | [docs/02](docs/02_architecture.md), [CAPSULE_SPEC.md](CAPSULE_SPEC.md) |
| 9–10 | Architecture and sequence diagrams | [docs/03](docs/03_diagrams.md) |
| 11–12 | Security analysis and threat model | [docs/04](docs/04_security_analysis.md) |
| 13–15 | Advantages, performance, scalability | [docs/05](docs/05_advantages_performance.md) |
| 16–18 | NIST compliance, deployment strategy, use cases | [docs/06](docs/06_compliance_deployment.md) |
| 19–20 | Comparison with hybrid TLS, roadmap | [docs/07](docs/07_comparison_roadmap.md) |
| 21–23 | Presentation diagrams, elevator pitch, 5-minute script | [docs/08](docs/08_presentation.md) |

---

## License

Released under the MIT License.
