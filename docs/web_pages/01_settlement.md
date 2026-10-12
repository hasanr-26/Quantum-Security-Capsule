# Tab 01 &mdash; Settlement Console Specification

[![NIST PQC](https://img.shields.io/badge/NIST-FIPS%20203%20%7C%20FIPS%20204-green.svg)](https://csrc.nist.gov/projects/post-quantum-cryptography)
[![Tab](https://img.shields.io/badge/Workbench-Tab%2001%20Settlement-blue.svg)](https://127.0.0.1:8443)
[![Status](https://img.shields.io/badge/Status-Operational-brightgreen.svg)]()

---

## 1. Overview & Operational Purpose

The **Settlement Console** (Tab 01) is the core operational interface of the Quantum Security Capsule platform. It enables operators, evaluators, and auditors to:
1. Construct genuine post-quantum cryptographic capsules around live institutional banking messages (ISO 20022 `pacs.008`, SWIFT MT103, and card authorization payloads).
2. Transmit those capsules across real TLS 1.3 network paths (either directly to the settlement node or through a TLS-terminating interception proxy).
3. Observe the server's **5-stage zero-trust validation pipeline** executing in real time, inspecting microsecond timings and diagnostic acceptance traces.
4. Verify the recovered financial plaintext at the clearing engine.
5. Inspect raw HTTP network telemetry (wire latency vs. server cryptographic processing latency).

---

## 2. Interface Layout & Feature Breakdown

```
┌──────────────────────────────────────────────────┬──────────────────────────────────────────────────┐
│ INSTRUCTION BUILDER (Left Panel)                 │ ZERO-TRUST VALIDATION PIPELINE (Right Panel)     │
├──────────────────────────────────────────────────┼──────────────────────────────────────────────────┤
│ • Message Standard (ISO 20022 / MT103 / Card)    │ • Stage 1: Protocol Version (QSC-1.0)     [~1 µs]│
│ • Validity Window (TTL in seconds)               │ • Stage 2: Freshness Window (TTL Expiry)  [~7 µs]│
│ • [Rotate Keys]                                  │ • Stage 3: Replay Token (SHA3-512)        [~2 µs]│
│ • [Build Capsule]                                │ • Stage 4: Integrity Lock (SHA3-512)     [~60 µs]│
│ • [Transmit & Settle]                            │ • Stage 5: Origin Signature (ML-DSA-65)  [~17 ms]│
│ • Network Route (Direct :8443 / Proxy :8444)     ├──────────────────────────────────────────────────┤
│ • Current Capsule Metadata & Component Sizes     │ DECRYPTED PAYLOAD AT SETTLEMENT ENGINE           │
│                                                  ├──────────────────────────────────────────────────┤
│                                                  │ LIVE NETWORK CONSOLE                             │
│                                                  │ Timestamp | POST /api/... | 200 | Wire ms | Srv ms│
└──────────────────────────────────────────────────┴──────────────────────────────────────────────────┘
```

---

## 3. Left Panel: Instruction Builder

### 3.1 Message Standard Selector
- **DOM Element:** `<select id="payload-kind">`
- **Options Available:**
  1. `ISO 20022 pacs.008 — Interbank Credit Transfer` (High-value institutional clearing)
  2. `SWIFT MT103 — Customer Credit Transfer` (International correspondent wire)
  3. `Card Authorisation Record (PCI DSS)` (E-commerce / retail transaction with PAN & CVV)
- **What it does:** Selects the template schema passed to `/api/v1/capsule/encapsulate`.
- **What it shows:** Sets the transaction category and downstream wire layout.
- **How it works:** When building a capsule, [`src/server/payloads.py`](../../src/server/payloads.py) dynamically generates unique message identifiers, fresh UTC creation timestamps, randomized amounts, valid BICs (`BARCGB22XXX` to `HDFCINBBXXX`), and unique EndToEndIds/UETRs per invocation.
- **Theory behind it:** Proves that QSC is **transport and payload agnostic**. It does not protect fixed mock strings; it encrypts arbitrary byte streams conforming to global banking standards.

---

### 3.2 Validity Window (TTL in Seconds)
- **DOM Element:** `<input type="number" id="ttl" value="300">` (Range: 5 to 86,400 seconds)
- **What it does:** Defines the time-to-live expiration delta added to the current UTC timestamp during capsule construction (`expires_at = now + ttl`).
- **What it shows:** An editable numeric input defaulting to 300 seconds (5 minutes).
- **How it works:** Transmitted in `EncapsulateRequest.policy.ttl_seconds`. Verified by the validator at **Stage 2** using wall-clock UTC comparisons.
- **Theory behind it:** **Temporal Freshness Enforcement.** A cryptographic token without temporal bounds can be captured and hoarded by an adversary for indefinite future replay. Strict TTLs narrow the exposure window to minutes. Setting TTL to `5`, waiting 10 seconds, and settling live triggers a clean Stage 2 expiration rejection.

---

### 3.3 "Rotate Keys" Button
- **DOM Element:** `<button id="btn-keys">`
- **What it does:** Generates a brand-new ML-KEM-768 keypair and ML-DSA-65 keypair on the settlement server.
- **What it shows:** Updates key generation timings (`ml_kem_768_keygen_ms`, `ml_dsa_65_keygen_ms`) in the console, alters the ML-KEM fingerprint in the masthead, and invalidates previously built capsules.
- **How it works:** Dispatches `POST /api/v1/pqc/keys/generate`. The server executes `MLKEM768.generate_keypair()` and `MLDSA65.generate_keypair()` and rebuilds the `SecureReceiver` instance in memory.
- **Theory behind it:** Demonstrates **Cryptographic Agility & Key Lifecycle Isolation**. In post-quantum systems, key rotation must be instantaneous. If an operator builds a capsule, rotates keys, and then attempts settlement, the transaction is rejected at **Stage 5** because the origin signature does not match the new keyset.

---

### 3.4 "Build Capsule" Button
- **DOM Element:** `<button id="btn-build" class="btn btn--primary">`
- **What it does:** Triggers the server's full **8-step construction pipeline** to wrap the selected financial payload into a sealed Quantum Security Capsule.
- **What it shows:** Populates the "Current Capsule" summary card with real metrics (Capsule ID, Payload Size, Wire Size, Expansion Ratio, KEM Ciphertext Bytes, Signature Bytes, Build Time in ms) and enables the "Transmit & Settle" button.
- **How it works:** Sends `POST /api/v1/capsule/encapsulate` to the settlement node. The server executes:
  1. Identifiers & Timestamps (`capsule_id`, `issued_at`, `expires_at`)
  2. ML-KEM-768 Encapsulation (Generates 256-bit shared secret $K$ and 1088-byte ciphertext)
  3. HKDF-SHA3-512 Key Derivation (Derives AES key from $K$ salted with `capsule_id`)
  4. AES-256-GCM Encryption (Authenticates associated data = `capsule_id`)
  5. Replay Token Derivation (`SHA3-512(capsule_id + issued_at + sender_id + nonce)`)
  6. Canonical JSON Schema Assembly
  7. SHA3-512 Canonical Integrity Locking
  8. ML-DSA-65 Lattice Digital Signing
- **Theory behind it:** **Autonomous Armoring.** The payload is mathematically secure *before* it ever touches a network interface or communication pipe.

---

### 3.5 "Transmit & Settle" Button
- **DOM Element:** `<button id="btn-settle" class="btn btn--go">`
- **What it does:** Transmits the current capsule over HTTPS to the settlement engine, runs the 5-stage validation gate, decapsulates the key, decrypts the payload, and commits the settlement.
- **What it shows:** Renders the live pass/fail status of all 5 validation gates with microsecond timings, displays the decrypted payload in green phosphor, increments the API request and capsule counters, and outputs wire latency telemetry.
- **How it works:** Sends `POST /api/v1/capsule/settle` containing the capsule JSON. The server invokes `SESSION.receiver.settle_with_report(capsule, sender_public_key)`.
- **Theory behind it:** **Zero-Trust Settlement.** Decryption is never attempted unless 100% of validation stages pass. The single-use replay token is committed to the registry only upon successful completion.

---

### 3.6 Network Route Selector
- **DOM Element:** `<select id="route">`
  - `Direct to settlement node (:8443)`
  - `Via interception proxy (:8444)`
- **What it does:** Toggles whether `fetch()` sends the request directly to port 8443 or routes it through the TLS-terminating MITM proxy on port 8444.
- **What it shows:** Logs show `INTERCEPTED` tag when routed through the proxy.
- **How it works:** [`api_client.js`](../../src/frontend/js/api_client.js) redirects the destination URL to `https://127.0.0.1:8444/api/v1/capsule/settle`.
- **Theory behind it:** **Multi-Hop Resilience.** Demonstrates that QSC capsules survive hostile intermediary network hops. The proxy terminates TLS, logs all bytes, and forwards the capsule &mdash; yet cannot read or corrupt the inner payload.

---

## 4. Right Panel: Zero-Trust Validation Pipeline

Every inbound settlement request must traverse five sequential gates:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ STAGE 1: Protocol Version Check                                             │
│ Status: PASS | Elapsed: ~1.2 µs | Control: Schema conformance               │
├─────────────────────────────────────────────────────────────────────────────┤
│ STAGE 2: Freshness Window Enforcement                                       │
│ Status: PASS | Elapsed: ~6.8 µs | Control: TTL / Expiry deadline            │
├─────────────────────────────────────────────────────────────────────────────┤
│ STAGE 3: Replay Cache Verification                                          │
│ Status: PASS | Elapsed: ~2.1 µs | Control: SHA3-512 single-use token lookup │
├─────────────────────────────────────────────────────────────────────────────┤
│ STAGE 4: Integrity Lock Verification                                        │
│ Status: PASS | Elapsed: ~58.4 µs| Control: SHA3-512 canonical digest match  │
├─────────────────────────────────────────────────────────────────────────────┤
│ STAGE 5: Origin Authenticity Verification                                   │
│ Status: PASS | Elapsed: 16.8 ms | Control: ML-DSA-65 lattice signature     │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 4.1 Stage Ordering & Microsecond Fast-Path Theory
- **Ordering Philosophy:** Cheapest checks run first.
- Stages 1&ndash;3 take **less than 10 microseconds combined**. Malformed, expired, or replayed traffic is terminated at the edge before consuming server memory.
- Stage 4 re-computes the SHA3-512 integrity lock in **~60 microseconds**. Single-bit tampering is caught here before invoking the lattice verifier.
- Stage 5 verifies the ML-DSA-65 lattice signature (**~17 ms in Python**). This heavy mathematical operation is invoked *only* for verified, fresh, intact traffic &mdash; preventing lattice signature DoS exhaustion attacks.

---

## 5. Bottom Panels: Output & Telemetry

### 5.1 Decrypted Payload at Settlement Engine
- **DOM Element:** `<pre id="decrypted-output">`
- **What it shows:**
  - On success: The full decrypted plaintext banking payload (XML ISO 20022 or text SWIFT MT103) formatted in green phosphor with timing breakdown (`Validation: X ms | Decryption: Y ms`).
  - On failure: Displays the exact rejection reason and which stage blocked the capsule in bold red text.

### 5.2 Live Network Console
- **DOM Element:** `<div id="net-log">`
- **What it shows:** Continuous timestamped log of genuine `fetch()` network activity:
  ```
  14:32:01.412  POST /api/v1/capsule/settle  ->  200  28.4ms wire  21.2ms server
  ```
- **Theory behind it:**
  - **Wire Time (`performance.now()`):** Total browser-to-server round-trip time.
  - **Server Time (`X-QSC-Process-Time-Ms`):** Server-side execution duration.
  - The gap between wire time and server time reflects actual TCP/TLS transport latency.
