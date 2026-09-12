# Quantum Security Capsule (QSC)

[![Barclays Innovation Lab](https://img.shields.io/badge/Barclays-Innovation%20Lab-blue.svg)](https://www.barclays.com)
[![NIST PQC](https://img.shields.io/badge/NIST-FIPS%20203%20%7C%20FIPS%20204-green.svg)](https://csrc.nist.gov/projects/post-quantum-cryptography)
[![Tests](https://img.shields.io/badge/tests-69%20passed%20%7C%20100%25-brightgreen.svg)](tests/)
[![Python](https://img.shields.io/badge/python-3.11%20%7C%203.12-blue.svg)](https://www.python.org)
[![License](https://img.shields.io/badge/License-MIT-purple.svg)](LICENSE)

> **Message-Centric Post-Quantum Cryptographic Communication Architecture for Financial Infrastructure**

---

## Why This Project is Required

### 1. The "Harvest Now, Decrypt Later" (HNDL) Reality
Modern financial communications — SWIFT messaging, interbank settlement APIs, ISO 20022 transactions, enterprise message queues (Kafka, IBM MQ), and file transfers — rely almost exclusively on classical public-key cryptography (RSA-2048/3072 and ECDH/ECDSA P-256) inside TLS 1.3 or IPSec tunnels.

Hostile actors and state-sponsored adversaries are actively intercepting and archiving petabytes of encrypted financial wire traffic today. When a Cryptographically Relevant Quantum Computer (CRQC) becomes operational, **Shor's algorithm** will calculate the private keys and recover the session keys of every archived handshake. **Every stored historic transaction, payment authorization, and account credential will become readable in cleartext.**

```
[ Client / Core Bank ] <========= TLS Tunnel (RSA / ECDH) =========> [ Ingress Gateway ]
                                         │
                              Captured Network Traffic
                     (Harvest Now, Decrypt Later - HNDL)
                                         │
                                         ▼ (Quantum Era - Shor's Algorithm)
                                PLAINTEXT FINANCIAL DATA
```

### 2. The Multi-Hop Blindspot: Channel Security vs Message Security
TLS only encrypts the **connection pipe between two immediate network hops**, not the data itself:
- **Middlebox Plaintext Exposure:** In modern cloud-native banking, TLS terminates at the first reverse proxy, WAF, or API gateway. Downstream traffic traverses internal microservices, proxies, and message brokers where payloads are decrypted.
- **Asynchronous Message Pipelines:** Critical banking workflows (e.g., payment clearing and settlement) traverse asynchronous queues (Kafka, RabbitMQ, IBM MQ). TLS cannot protect data while resting in an intermediate message topic or long-term datastore.
- **Why "Hybrid TLS" is Insufficient:** Swapping post-quantum certificates into TLS (Hybrid TLS 1.3) protects the socket pipe against quantum eavesdropping, but leaves data completely unprotected the moment the socket terminates at a gateway or enters an internal bus.

```
TRADITIONAL TLS:
Client ──[TLS Encrypted]──► API Gateway ──[Plaintext / Internal Hop]──► Kafka ──[Plaintext]──► Settlement Node
                              ▲                                           ▲
                              └── Decrypted at boundary                   └── Exposed in transit/at rest

QUANTUM SECURITY CAPSULE:
Client ──[QSC Sealed Capsule]─────────────────────────────────────────────────────────────────► Settlement Node
           └─ ML-KEM-768 Key Encapsulation + ML-DSA-65 Signature + AES-256-GCM Payload ─┘
           (Protected across TLS hops, API gateways, Kafka queues, and proxies untouched)
```

### 3. The Paradigm Shift: The Autonomous Quantum Capsule
The **Quantum Security Capsule (QSC)** shifts cryptographic boundaries from the *transient communication channel* into the *data payload itself*. Every payment instruction is transformed into an autonomous, tamper-evident, quantum-resistant digital capsule that:
- **Remains Post-Quantum Secure Everywhere:** Protected with NIST FIPS 203 ([ML-KEM-768](src/crypto/kem.py)) and FIPS 204 ([ML-DSA-65](src/crypto/dsa.py)) end-to-end, across all intermediate network hops, clouds, and queues.
- **Enforces Zero-Trust Validation:** Evaluated by a 5-stage validation gate that rejects malformed, expired, or replayed traffic in microseconds before invoking heavy cryptographic verification.
- **Is Completely Transport-Agnostic:** Operates seamlessly over HTTPS/REST, gRPC, WebSocket, raw TCP, Kafka, MQ, SWIFT networks, or offline file containers (`.qsc`).

### Comparison Matrix

| Dimension | Legacy Transport Security (TLS 1.3 / mTLS) | Hybrid TLS (PQ-TLS) | Quantum Security Capsule (QSC) |
| :--- | :--- | :--- | :--- |
| **Protection Scope** | Channel / Socket pipe only | Channel / Socket pipe only | **The message payload itself** |
| **HNDL Resistance** | Vulnerable (broken by Shor's) | Protected in transit only | **Protected end-to-end for decades** |
| **Middlebox Exposure** | Decrypted at API gateway/proxy | Decrypted at API gateway/proxy | **Zero exposure** (stays sealed until receiver) |
| **Async Queues (Kafka/MQ)** | No protection for data at rest | No protection for data at rest | **Cryptographically secure in any queue/store** |
| **Replay Defense** | Socket-session bound | Socket-session bound | **Cryptographic per-message SHA3-512 token** |
| **Non-Repudiation** | Connection endpoint only | Connection endpoint only | **Cryptographic ML-DSA-65 signature on wire payload** |

---

## What is Actually Real Here

This matters more than any feature list, so it is stated up front:

| Component | Status | Details |
| :--- | :--- | :--- |
| **ML-KEM-768 / ML-DSA-65** | **Real** | `kyber-py` and `dilithium-py`, validated against NIST ACVP test vectors for FIPS 203/204. Genuine lattice arithmetic, standard key sizes, real signature verification. |
| **AES-256-GCM, SHA3-512, HKDF** | **Real** | Backed by `cryptography` (OpenSSL FIPS-compliant primitives). |
| **TLS 1.3 Transport** | **Real** | Uvicorn running with a live X.509 certificate. The workbench reports cipher suites negotiated by actual handshakes. |
| **Interception Proxy** | **Real** | A live TLS-terminating man-in-the-middle proxy that records intercepted wire bytes. |
| **Financial Payloads** | **Real Formats** | Generated dynamically per call — ISO 20022 (`pacs.008`) and SWIFT MT103, with live identifiers and unique UETRs. |
| **Performance Figures** | **Measured** | Benchmark numbers reflect real execution timings (see [docs/05](docs/05_advantages_performance.md)). |
| **Shor's Algorithm Simulation** | **Modelled** | The theoretical quantum attack against captured classical TLS sessions is modelled to demonstrate retrospective compromise. |

> Pure-Python PQC libraries are chosen for auditability and zero-dependency compilation. Cryptographic wrapper classes in `src/crypto/` are cleanly decoupled so hardware-accelerated engines (`liboqs` or AWS-LC) can drop in with zero interface changes.

---

## Verification & Tests Passed

The repository undergoes comprehensive verification across **8 dedicated test suites**, covering all cryptographic primitives, wire formats, attack vectors, and API endpoints.

```
================================== TEST SUMMARY ==================================
Tests Passed: 69 / 69 (100%)
Status:       All Suites Passing Green
Coverage:     Cryptographic primitives, MITM resistance, API contracts, TLS handshake
Command:      pytest tests/ -v
==================================================================================
```

### Test Suites Breakdown

| Test Suite | Tests Passed | What It Verifies |
| :--- | :---: | :--- |
| **[`test_pqc_crypto.py`](tests/test_pqc_crypto.py)** | **21 passed** | **NIST PQC Standards Compliance:** FIPS 203 (ML-KEM-768) and FIPS 204 (ML-DSA-65) key-pair generation, exact key/ciphertext byte sizes, encapsulation/decapsulation roundtrips, implicit rejection of corrupted KEM ciphertexts, ML-DSA-65 lattice signature verification, signature forgery rejection, HKDF-SHA3-512 key derivation domain separation, and AES-256-GCM authenticated encryption. |
| **[`test_settlement_api.py`](tests/test_settlement_api.py)** | **21 passed** | **Settlement Engine & API Contracts:** End-to-end `/api/settle` pipeline, batch settlement validation, malformed payload rejection, wire offset accuracy, hex packet inspector responses, and attack lab simulation endpoints. |
| **[`test_mitm_resistance.py`](tests/test_mitm_resistance.py)** | **12 passed** | **Adversarial & MITM Resistance:** Live TLS-terminating proxy capture verification (proving zero plaintext exposure), single-bit payload tampering rejection, ciphertext modification detection, and replay attack blocking. |
| **[`test_tls_handshake.py`](tests/test_tls_handshake.py)** | **9 passed** | **Real TLS 1.3 Transport:** Certificate chain verification, TLS 1.3 protocol enforcement, negotiated cipher suite validation (`TLS_AES_256_GCM_SHA384`), and handshake timing telemetry. |
| **[`test_api_endpoints.py`](tests/test_api_endpoints.py)** | **3 passed** | **Service Health & Configuration:** API endpoint availability, OpenAPI schema compliance, and settlement service readiness. |
| **[`test_builder.py`](tests/test_builder.py)** | **1 passed** | **Capsule Construction Pipeline:** Canonical serialization, deterministic field ordering, and metadata header generation. |
| **[`test_validator.py`](tests/test_validator.py)** | **1 passed** | **Zero-Trust Validation Pipeline:** Ordered execution of all 5 security stages and fail-closed behavior on invalid inputs. |
| **[`test_replay_protection.py`](tests/test_replay_protection.py)** | **1 passed** | **Replay Protection Engine:** Single-use SHA3-512 replay token consumption, cache validation, and immediate rejection of duplicate capsules. |

### Attack Vectors Verified & Prevented

- **Harvest Now, Decrypt Later (HNDL):** Intercepted wire bytes reveal nothing even if the transport layer is breached.
- **Man-in-the-Middle (MITM) Tampering:** Single-bit modifications on wire bytes trigger stage-4 integrity rejection.
- **Replay Attacks:** Identical capsules re-submitted within or outside the TTL window are rejected by single-use replay tokens.
- **Signature Forgery:** Altered message contents or swapped origin public keys fail ML-DSA-65 lattice verification.
- **Expired Instructions:** Out-of-window messages are eliminated at Stage 2 without consuming downstream CPU cycles.

---

## Cryptographic Stack

| Security Property | Standard / Primitive | Purpose |
| :--- | :--- | :--- |
| **Key Encapsulation** | **ML-KEM-768** (NIST FIPS 203) | Post-quantum shared secret establishment, fresh per capsule |
| **Digital Signature** | **ML-DSA-65** (NIST FIPS 204) | Quantum-resistant lattice signature for origin authenticity and non-repudiation |
| **Key Derivation** | **HKDF-SHA3-512** (NIST SP 800-56C Rev. 2) | Derives content encryption key from KEM secret with domain separation |
| **Symmetric Encryption** | **AES-256-GCM** (NIST SP 800-38D) | Authenticated symmetric encryption of financial transaction payloads |
| **Integrity Digest** | **SHA3-512** (NIST FIPS 202) | Cryptographic capsule binding, canonical checksum, and replay token derivation |

---

## Architecture & Zero-Trust Pipeline

```
                 Client App / Originator
                           │
             ┌─────────────┴─────────────┐
             ▼                           ▼
      Financial Payload            Policy Metadata
   (ISO 20022 / SWIFT MT103)      (TTL, IDs, Routing)
             │                           │
             └─────────────┬─────────────┘
                           │
                Quantum Capsule Builder
     ┌─────────────────────┼─────────────────────┐
     │                     │                     │
 Encrypt (AES-256-GCM)  Sign (ML-DSA-65)  Encapsulate (ML-KEM-768)
     │                     │                     │
     └─────────────────────┼─────────────────────┘
                           │
                Quantum Security Capsule
                           │
     ┌─────────────────────┴─────────────────────┐
     │  Untrusted Hops: REST / Kafka / MQ / TLS  │
     └─────────────────────┬─────────────────────┘
                           │
                Capsule Validator & Receiver
     ┌─────────────────────┼─────────────────────┐
  Verify Sig           Verify Hash          Decapsulate & Decrypt
     └─────────────────────┼─────────────────────┘
                           │
                 Core Settlement Engine
```

### 5-Stage Zero-Trust Validation Pipeline

Every capsule passes through five strict security gates in order, cheapest first, failing closed at the earliest objection. The single-use replay token is committed only after all stages pass:

| Stage | Control | Typical Cost | Purpose |
| :---: | :--- | ---: | :--- |
| **1** | **Protocol Version Check** | ~1 µs | Drops malformed or incompatible capsule versions immediately. |
| **2** | **Freshness Window (TTL)** | ~7 µs | Rejects expired transactions before performing any cryptography. |
| **3** | **Replay Token Check** | ~2 µs | Checks single-use SHA3-512 token cache to defeat replay attempts. |
| **4** | **Integrity Lock (SHA3-512)** | ~60 µs | Validates exact canonical digest; catches bit flips before expensive math. |
| **5** | **Origin Signature (ML-DSA-65)**| ~17 ms | Verifies lattice signature for cryptographic origin authenticity. |

> Ordering is deliberate: unauthorized or junk traffic is filtered out in microseconds, shielding the heavier lattice verification engine from denial-of-service pressure.

---

## Quick Start

```bash
# Clone the repository
git clone https://github.com/hasanr-26/Quantum-Security-Capsule.git
cd Quantum-Security-Capsule

# Install dependencies
pip install -r requirements.txt

# Run the full test suite
pytest tests/ -v
```

### Launch the Settlement Node & Workbench

```bash
python -m src.server.run
```

This generates local TLS certificates on first run and exposes:

| Service | Address | Role |
| :--- | :--- | :--- |
| **Security Workbench + API** | `https://127.0.0.1:8443` | Settlement node and interactive UI |
| **Interception Proxy** | `https://127.0.0.1:8444` | TLS-terminating MITM inspection hop |
| **Interactive OpenAPI Docs** | `https://127.0.0.1:8443/api/docs` | Live API reference and Swagger UI |

*(Self-signed certificates trigger a standard browser warning on first visit — accept it to proceed over real TLS.)*

### Interactive Security Workbench

The browser workbench at `https://127.0.0.1:8443` provides 5 dedicated exploration labs:

1. **01 Settlement:** Construct real capsules from ISO 20022 / MT103 payloads and settle them. Inspect each validation stage with microsecond timings and live network console metrics.
2. **02 Packet Inspector:** Wireshark-style hex dump of the raw wire bytes. Click any field to highlight its exact byte offset; introduce bit flips to test validation controls.
3. **03 3D Visualizer:** Real-time visual comparison of channel security vs message security under simulated quantum attack conditions.
4. **04 Interception Lab:** Dispatch identical transactions over traditional TLS and QSC through the proxy, break the recorded sessions, and compare recovered data.
5. **05 Cryptography:** Active NIST parameter sets, lattice key sizes, and live TLS handshake telemetry.

### Standalone CLI Demonstrations

```bash
# Live HNDL demonstration: same payment, dual protection models, live proxy
python src/demo/hndl_demo.py

# High-value interbank wire transfer, end-to-end
python src/demo/banking_transfer.py

# Replay, tampering, and signature forgery rejection demo
python src/demo/replay_attack_demo.py

# Capsule transmission over raw TLS 1.3 socket
python src/demo/tls_qsc_demo.py

# File encryption into a portable .qsc container
python src/demo/file_encrypt_demo.py

# Measured benchmark of every cryptographic primitive
python src/demo/benchmark.py
```

---

## Documentation Index

| Deliverable | Topics Covered | Document |
| :--- | :--- | :--- |
| **01 Vision & Problem** | HNDL threat, channel vs message security, vision statement | [docs/01_vision_and_problem.md](docs/01_vision_and_problem.md) |
| **02 Architecture & Spec** | System components, message flows, capsule binary format | [docs/02_architecture.md](docs/02_architecture.md), [CAPSULE_SPEC.md](CAPSULE_SPEC.md) |
| **03 Architecture Diagrams** | End-to-end flows, multi-hop routing, sequence diagrams | [docs/03_diagrams.md](docs/03_diagrams.md) |
| **04 Security Analysis** | Threat model, attack tree, cryptanalysis, side-channel posture | [docs/04_security_analysis.md](docs/04_security_analysis.md) |
| **05 Performance & Benchmarks**| Micro-benchmarks, latency analysis, scaling considerations | [docs/05_advantages_performance.md](docs/05_advantages_performance.md) |
| **06 Compliance & Deployment** | NIST FIPS roadmap, regulatory alignment, migration blueprint | [docs/06_compliance_deployment.md](docs/06_compliance_deployment.md) |
| **07 Comparison & Roadmap** | Comparison with Hybrid TLS, PQ-VPNs, implementation roadmap | [docs/07_comparison_roadmap.md](docs/07_comparison_roadmap.md) |
| **08 Presentation & Pitch** | Presentation materials, elevator pitch, 5-minute executive script | [docs/08_presentation.md](docs/08_presentation.md) |

---

## License

Released under the [MIT License](LICENSE).
