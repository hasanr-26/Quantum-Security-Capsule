# 02 — Architecture and System Specification

[![NIST PQC](https://img.shields.io/badge/NIST-FIPS%20203%20%7C%20FIPS%20204-green.svg)](https://csrc.nist.gov/projects/post-quantum-cryptography)
[![Tests](https://img.shields.io/badge/tests-69%20passed%20%7C%20100%25-brightgreen.svg)](../tests/)
[![FastAPI](https://img.shields.io/badge/FastAPI-TLS%201.3-009688.svg)](https://fastapi.tiangolo.com)

---

## 1. Architectural Philosophy: Channel vs. Message Security

### 1.1 Legacy Transport-Centric Model
In standard financial IT infrastructure, security relies on encrypted connection pipes established between immediate point-to-point hops:

```
+------------------+         Encrypted TLS 1.3 Tunnel         +------------------+
|  Client / App    | =======================================> |  API Gateway     |
+------------------+       (Secures point-to-point pipe)      +--------+---------+
                                                                       │ Decrypts at boundary
                                                                       ▼
+------------------+          Internal Plaintext / Queues     +------------------+
| Internal Service | <─────────────────────────────────────── | Message Broker   |
+------------------+                                          +------------------+
```

Under this architecture:
- Encryption ceases at the edge proxy, load balancer, or WAF.
- Traffic recorded on the wire today can be decrypted retroactively once Shor's algorithm solves RSA/ECC discrete logarithms.
- Message brokers (Kafka, IBM MQ) and caching layers store plaintext payloads in process memory and on disk.

### 1.2 Proposed Quantum Security Capsule Paradigm
QSC shifts security directly into the financial data payload. Each transaction is transformed into an autonomous, tamper-evident, post-quantum encrypted, and digitally signed container:

```
                  Sender Application / Originating Client
                                     │
                        ┌────────────┴────────────┐
                        ▼                         ▼
                 Financial Payload          Policy Metadata
             (ISO 20022 / SWIFT MT103)    (TTL, Max Hops, BICs)
                        │                         │
                        └────────────┬────────────┘
                                     │
           Capsule Builder ([builder.py](../src/capsule/builder.py)) - 8-Step Pipeline
      ┌──────────────────────────────┼──────────────────────────────┐
      │                              │                              │
  Key Encapsulation           Key Derivation               Symmetric Encryption
   (ML-KEM-768)               (HKDF-SHA3-512)                 (AES-256-GCM)
   [FIPS 203]                 [SP 800-56C]                    [SP 800-38D]
      │                              │                              │
      └──────────────────────────────┼──────────────────────────────┘
                                     │
                     Deterministic Canonicalization & Hashing
                             (SHA3-512) [FIPS 202]
                                     │
                     Post-Quantum Digital Signature
                          (ML-DSA-65) [FIPS 204]
                                     │
                   Quantum Security Capsule ([models.py](../src/capsule/models.py))
                                     │
      ┌──────────────────────────────┴──────────────────────────────┐
      │  Transmitted via HTTPS (:8443) / Kafka / MQ / SWIFT / Disk  │
      └──────────────────────────────┬──────────────────────────────┘
                                     │
           Capsule Validator ([validator.py](../src/capsule/validator.py)) - 5-Stage Zero-Trust Gates
      ┌──────────────────────────────┼──────────────────────────────┐
      │ Version Check                │ Replay Token Check           │ Origin Signature
      │ Freshness (TTL) Check        │ Canonical SHA3-512 Check     │ (ML-DSA-65)
      └──────────────────────────────┼──────────────────────────────┘
                                     │ ALL 5 PASS
                                     ▼
           Secure Receiver ([receiver.py](../src/capsule/receiver.py)) - Decapsulate & Decrypt
      ┌──────────────────────────────┴──────────────────────────────┐
      │ 1. ML-KEM-768 Decapsulation -> Recover Shared Secret (K)     │
      │ 2. HKDF-SHA3-512 Derivation -> Reconstruct Content Key       │
      │ 3. AES-256-GCM Decryption -> Authenticate & Release Plaintext│
      └──────────────────────────────┬──────────────────────────────┘
                                     │
                       Core Settlement Ledger Engine
```

---

## 2. Core Subsystems and Component Breakdown

The QSC system comprises six core modular subsystems spanning cryptographic primitives, lifecycle engines, network services, and institutional user interfaces:

```
src/
├── crypto/        # 1. NIST Post-Quantum & Classical Cryptographic Primitives
├── capsule/       # 2. Capsule Lifecycle, Validation & Wire Serialisation
├── server/        # 3. Live TLS 1.3 FastAPI Backend & Interception Proxy
├── frontend/      # 4. Institutional Security Workbench & 3D Visualizer
├── demo/          # 5. Executable CLI Demonstrations & Benchmarks
└── utils/         # 6. Replay Token Derivation & ISO-8601 Timestamps
```

### Subsystem 1: Cryptographic Engine ([`src/crypto/`](../src/crypto/))
- **`kem.py` ([`MLKEM768`](../src/crypto/kem.py)):** Implements NIST FIPS 203 Module-Lattice Key Encapsulation Mechanism. Establishes a 256-bit symmetric shared secret between sender and recipient per message without interactive handshakes (Public Key: 1184 B, Private Key: 2400 B, Ciphertext: 1088 B).
- **`dsa.py` ([`MLDSA65`](../src/crypto/dsa.py)):** Implements NIST FIPS 204 Module-Lattice Digital Signatures. Computes unforgeable lattice signatures over SHA3-512 integrity hashes using the sender's private key (Public Key: 1952 B, Private Key: 4032 B, Signature: 3309 B).
- **`kdf.py` ([`derive_payload_key`](../src/crypto/kdf.py)):** Implements NIST SP 800-56C Rev. 2 Key Derivation via HKDF-SHA3-512. Salts derivation with `capsule_id` and binds domain separation string `QSC-1.0/AES-256-GCM`.
- **`symmetric.py` ([`encrypt_aes_256_gcm`](../src/crypto/symmetric.py)):** Implements NIST SP 800-38D Authenticated Encryption with Associated Data (AEAD). Cryptographically binds `capsule_id` into the 16-byte GCM authentication tag.
- **`hashing.py` ([`compute_sha3_512`](../src/crypto/hashing.py)):** Implements NIST FIPS 202 Keccak sponge permutation for 512-bit canonical integrity hashes and single-use replay tokens.

### Subsystem 2: Capsule Lifecycle Engine ([`src/capsule/`](../src/capsule/))
- **`models.py`:** Defines [`QuantumSecurityCapsule`](../src/capsule/models.py) and [`PolicyMetadata`](../src/capsule/models.py) data structures.
- **`builder.py`:** Orchestrates the deterministic 8-step capsule assembly pipeline.
- **`validator.py`:** Implements the 5-stage zero-trust validation pipeline with microsecond fast-path rejection.
- **`receiver.py`:** Coordinates validation enforcement, ML-KEM decapsulation, HKDF re-derivation, and AES-256-GCM authenticated payload recovery.
- **`wire.py`:** Canonical JSON wire serialisation, UTF-8 byte stream encoding, byte-offset tracking, and bit-flipping utilities for the packet inspector.

### Subsystem 3: Live Network & TLS 1.3 Server ([`src/server/`](../src/server/))
- **`run.py`:** Unified launcher initiating the live settlement node (`https://127.0.0.1:8443`) and interception proxy (`https://127.0.0.1:8444`) in a single process.
- **`api.py`:** Production FastAPI application exposing live REST endpoints for PQC key management, capsule encapsulation, zero-trust settlement, hex dump generation, attack simulations, and telemetry.
- **`tls_config.py`:** Manages TLS context generation, local self-signed X.509 certificate provisioning, and loopback TLS handshake probing.
- **`mitm_proxy.py`:** Genuine TLS-terminating forward proxy simulating intermediary inspection hops and demonstrating Harvest Now, Decrypt Later against real captured wire bytes.
- **`payloads.py`:** Institutional financial payload generator for ISO 20022 `pacs.008.001.08`, SWIFT MT103, and card authorization messages.

### Subsystem 4: Institutional Security Workbench ([`src/frontend/`](../src/frontend/))
- High-density, institutional dark-charcoal UI inspired by Bloomberg Terminal and Cloudflare Radar (strictly free of "AI slop" template gimmicks).
- Includes 5 operational tabs: Settlement Console, Wireshark-Style Packet Inspector, Three.js 3D Visualizer, Interception Lab, and Cryptography HUD.

---

## 3. The 8-Step Capsule Builder Pipeline

When creating a capsule, [`CapsuleBuilder.build_capsule()`](../src/capsule/builder.py) executes the following sequence:

```
[ Step 1: Identifiers & Timestamps ]
   ├── Generate unique capsule_id (qsc_<uuid_hex>)
   └── Establish ISO-8601 UTC issued_at and expires_at (now + 300s TTL)

[ Step 2: ML-KEM-768 Shared Secret Encapsulation ]
   ├── Encapsulate 256-bit shared secret (K) against recipient's public key
   └── Produce 1088-byte KEM ciphertext

[ Step 3: Content Key Derivation via HKDF-SHA3-512 ]
   ├── Salt: capsule_id
   ├── Info: "QSC-1.0/AES-256-GCM"
   └── Output: 256-bit derived symmetric content key (prevents direct K reuse)

[ Step 4: AES-256-GCM Authenticated Payload Encryption ]
   ├── Generate 96-bit cryptographically random IV (nonce)
   ├── Bind associated_data = capsule_id
   └── Produce payload_ciphertext and 16-byte payload_tag

[ Step 5: Replay Token Generation ]
   └── replay_token = SHA3-512(capsule_id || issued_at || sender_id || nonce)

[ Step 6: Canonical JSON Assembly ]
   └── Construct preliminary capsule structure and sort dictionary keys deterministically

[ Step 7: SHA3-512 Canonical Integrity Digest ]
   └── Compute 512-bit integrity_hash over canonical fields (excluding signature & hash)

[ Step 8: ML-DSA-65 Lattice Signature ]
   ├── Sign integrity_hash with sender's private ML-DSA-65 key
   └── Produce 3309-byte post-quantum digital signature
```

---

## 4. The 5-Stage Zero-Trust Validation Pipeline

Before decapsulating ciphertexts, [`CapsuleValidator.validate_detailed()`](../src/capsule/validator.py) enforces 5 sequential security gates:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ Stage 1: Protocol Version & Schema Check                                    │
│ Enforces version == "QSC-1.0". Rejects malformed JSON immediately.          │
│ Cost: ~1 µs                                                                 │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │ PASS
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ Stage 2: Freshness Window Enforcement                                       │
│ Verifies current_time <= expires_at using ISO-8601 UTC wall-clock checks.   │
│ Cost: ~7 µs                                                                 │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │ PASS
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ Stage 3: Replay Cache Verification                                          │
│ Checks single-use SHA3-512 replay_token against registry. Rejects duplicates.│
│ Cost: ~2 µs                                                                 │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │ PASS
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ Stage 4: Canonical Integrity Lock                                           │
│ Re-serializes canonical fields and computes SHA3-512. Rejects if 1 bit changed│
│ Cost: ~60 µs                                                                │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │ PASS
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ Stage 5: ML-DSA-65 Origin Authenticity Verification                         │
│ Verifies lattice signature against sender's registered public key.          │
│ Cost: ~17 ms                                                                │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │ ALL PASS
                                       ▼
                         Commit Replay Token to Store
                                       ▼
                    Forward to SecureReceiver for Decryption
```

### Ordering Rationale: Fast-Path Rejection
The stage ordering is deliberate: cheap structural checks (Stages 1&ndash;3, costing &lt;10 µs combined) run first. If a capsule is malformed, expired, or replayed, it is dropped in microseconds without consuming CPU cycles on expensive lattice mathematical operations (Stage 5, costing ~17 ms). Under a denial-of-service attack, invalid capsules are rejected almost instantaneously.

---

## 5. QSC Wire Format & Data Schema ([`models.py`](../src/capsule/models.py))

```json
{
  "version": "QSC-1.0",
  "capsule_id": "qsc_99a81f3b7c2a41d0",
  "issued_at": "2026-09-13T01:30:00Z",
  "expires_at": "2026-09-13T01:35:00Z",
  "replay_token": "a4f89b12... (128 hex chars SHA3-512 digest)",
  "sender_id": "BARCGB22XXX",
  "recipient_id": "HDFCINBBXXX",
  "kem_ciphertext": "7c12d... (Base64 ML-KEM-768 ciphertext, 1088 bytes)",
  "payload_ciphertext": "e8810... (Base64 AES-256-GCM encrypted payload)",
  "payload_tag": "33f01... (Base64 16-byte GCM authentication tag)",
  "nonce": "91a2b... (Base64 12-byte GCM initialization vector)",
  "integrity_hash": "b9012... (128 hex chars canonical SHA3-512 digest)",
  "signature": "d2218... (Base64 ML-DSA-65 lattice signature, 3309 bytes)",
  "policy": {
    "classification": "CONFIDENTIAL",
    "jurisdiction": "UK",
    "max_hops": 3,
    "allowed_channels": ["HTTPS", "KAFKA", "MQ", "SWIFT"]
  }
}
```

---

## 6. Network & Service Topology

```
+────────────────────────────────────────────────────────────────────────────+
|                     QSC PRODUCTION TOPOLOGY                                |
+────────────────────────────────────────────────────────────────────────────+

 [ Client Applications / Browser Workbench ]
        │
        ├── Direct HTTPS / TLS 1.3 Requests ──────────────────┐
        │                                                     │
        └── Via Interception Proxy ──────────┐                │
                                             │                │
                                             ▼                ▼
+──────────────────────────────────+  +──────────────────────────────────────+
| INTERCEPTION PROXY (:8444)       |  | SETTLEMENT NODE (:8443)              |
| • Live TLS 1.3 Termination       |  | • Live TLS 1.3 / HTTPS Service       |
| • Wire Byte Interception Store   |  | • Web Security Workbench UI          |
| • Quantum Decrypt Simulation Lab |  | • REST API (/api/v1/...)             |
| • Relays traffic to :8443        |  | • 5-Stage Zero-Trust Validation Gate |
+────────────────┬─────────────────+  | • Core Settlement Ledger Engine      |
                 │                    +──────────────────▲───────────────────+
                 └────── Internal Forward ───────────────┘
```
