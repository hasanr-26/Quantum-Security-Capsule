# Tab 04 &mdash; Interception Lab & Proxy Forensics Specification

[![NIST PQC](https://img.shields.io/badge/NIST-FIPS%20203%20%7C%20FIPS%20204-green.svg)](https://csrc.nist.gov/projects/post-quantum-cryptography)
[![MITM Proxy](https://img.shields.io/badge/Proxy-TLS%201.3%20MITM%20:8444-orange.svg)](https://127.0.0.1:8444)
[![Tab](https://img.shields.io/badge/Workbench-Tab%2004%20Interception%20Lab-blue.svg)](https://127.0.0.1:8443)

---

## 1. Overview & Operational Purpose

The **Interception Lab** (Tab 04) provides empirical evidence for the project's central thesis by capturing, archiving, and analyzing real network traffic flowing through a genuine TLS-terminating forward proxy.

While Tab 03 explains the theoretical argument through 3D animation, Tab 04 delivers concrete experimental verification. It allows evaluators to transmit identical payments through an active man-in-the-middle proxy using (1) traditional TLS 1.3 transport security and (2) a Quantum Security Capsule &mdash; and then simulate a quantum computer breaking the recorded TLS sessions.

### What is Real vs. What is Modelled
- **REAL:** The network hops, the TLS 1.3 socket negotiation, the TLS termination on port 8444, and the captured wire bytes stored in memory.
- **MODELLED:** The assumption that a future quantum computer running Shor's algorithm has solved discrete logarithms to recover the TLS session key. This applies the anticipated 2030s threat model to genuine network captures.

---

## 2. Interface Layout

```
┌─────────────────────────────────────────────────────┬─────────────────────────────────────────────────┐
│ INTERCEPTION CONTROL (Left Panel)                   │ HARVESTED NETWORK FLOWS (Right Panel, Top)      │
├─────────────────────────────────────────────────────┼─────────────────────────────────────────────────┤
│ • Message Standard (Card / pacs.008 / MT103)        │ Table of Intercepted Wire Flows:                │
│ • [Send Payment via TLS Only]                       │ Cap ID | Method | Path | Req B | RTT | Security │
│ • [Send Payment as Capsule]                         │ cap_001| POST   |/legacy| 420 B | 8ms | TLS_ONLY │
│ • [Break Archived TLS Sessions]                     │ cap_002| POST   |/settle| 9.5 KB| 38ms| QSC      │
│ • [Clear Harvest Archive]                           ├─────────────────────────────────────────────────┤
│ • Harvest Archive Stats: flows & total bytes        │ POST-QUANTUM FORENSIC ANALYSIS (Right, Bottom)  │
│ • Threat Realism Explanatory Box                    │ Side-by-side disclosure analysis of recovered   │
│                                                     │ cleartext vs opaque lattice ciphertext.         │
└─────────────────────────────────────────────────────┴─────────────────────────────────────────────────┘
```

---

## 3. Left Panel: Interception Controls

### 3.1 Message Standard Selector
- **DOM Element:** `<select id="intercept-kind">`
- **Options:** `Card Authorisation Record (PCI DSS)`, `ISO 20022 pacs.008`, `SWIFT MT103`.
- **Why Card Authorisation is the strongest demo choice:** A leaked credit card record (Primary Account Number, CVV2, expiration date, cardholder name) represents an immediate, undeniable data breach to non-technical evaluators.

---

### 3.2 "Send Payment via TLS Only" (The Control Group)
- **DOM Element:** `<button id="btn-send-legacy">`
- **Network Path:** `POST https://127.0.0.1:8444/api/v1/legacy/transfer`
- **What it does:** Generates a real financial payment and transmits it through the interception proxy protected **solely by TLS 1.3**.
- **How it works:** The proxy terminates the client's TLS 1.3 session, buffers the raw bytes, opens a separate TLS session to the settlement node (`:8443`), relays the request, and records the flow.
- **Theory behind it:** This represents how 99.9% of modern banking APIs operate today. TLS 1.3 with AES-256-GCM is strong transport encryption, but its protection ends at the proxy interface.

---

### 3.3 "Send Payment as Capsule" (The QSC Treatment Group)
- **DOM Element:** `<button id="btn-send-capsule">`
- **Network Path:** `POST https://127.0.0.1:8444/api/v1/capsule/settle`
- **What it does:** Builds a full post-quantum capsule (ML-KEM-768 + ML-DSA-65 + AES-256-GCM) and transmits it through the identical proxy hop to the settlement node.
- **How it works:** The proxy terminates TLS identically and logs every byte. However, the data payload inside the HTTP body is an armored QSC container.
- **Theory behind it:** Proves that QSC is middlebox-transparent. The proxy forwards the capsule without requiring custom protocol adapters, yet cannot inspect or modify the underlying transaction.

---

### 3.4 "Break Archived TLS Sessions" (The Quantum Breach)
- **DOM Element:** `<button id="btn-quantum" class="btn btn--danger">`
- **What it does:** Simulates an adversary applying Shor's algorithm in the 2030s against the recorded TLS handshakes, stripping the outer transport layer to expose the harvested body.
- **What it shows:** Populates the **Post-Quantum Forensics** panel with side-by-side technical disclosures for every harvested flow.

---

### 3.5 "Clear Harvest Archive"
- **DOM Element:** `<button id="btn-clear-captures">`
- **Endpoint:** Calls client-side reset and clears the proxy capture ring buffer.
- **What it shows:** Empties the flows table and resets harvest byte counters to zero.

---

## 4. Right Panel: Harvested Flows & Forensic Disclosures

### 4.1 Intercepted Network Flows Table
- **DOM Element:** `<tbody id="capture-rows">`
- **Columns:**
  - `Capture ID`: Monotonic sequence identifier (`cap_00001`, `cap_00002`).
  - `Method & Path`: `POST /api/v1/legacy/transfer` vs `POST /api/v1/capsule/settle`.
  - `Req Bytes`: Size of the captured request payload.
  - `RTT`: Measured round-trip proxy relay latency in milliseconds.
  - `Protection`: High-contrast badge: `TLS_ONLY` (Amber) vs. `QSC_CAPSULE` (Green).

---

### 4.2 Post-Quantum Forensic Analysis

When an operator clicks "Break Archived TLS Sessions", [`src/server/mitm_proxy.py`](../../src/server/mitm_proxy.py) classifies every captured body and renders the comparative forensic results:

#### Scenario A: The Legacy TLS Transfer (`TLS_ONLY`)
```json
{
  "verdict": "FULL DISCLOSURE",
  "status": "CRITICAL DATA BREACH",
  "leaked_fields": ["pan", "cvv", "cardholder", "amount", "account_number"],
  "recovered_body": {
    "account_number": "GB29BARC20000088910245",
    "pan": "4929-8812-4401-9982",
    "cvv": "781",
    "amount": 75000000.00,
    "currency": "GBP",
    "cardholder": "GlaxoSmithKline Treasury"
  }
}
```
- **Forensic Outcome:** The panel lights up with a **red critical breach banner**. Every sensitive marker (`pan`, `cvv`, `iban`, `amount`, `bicfi`) is displayed in raw cleartext.
- **Regulatory Reality:** Under PCI DSS Requirement 3.4 and GDPR Article 32, this constitutes an immediate notification-grade breach resulting in severe regulatory fines and reputational destruction.

---

#### Scenario B: The Quantum Security Capsule (`QSC_CAPSULE`)
```json
{
  "verdict": "ZERO DISCLOSURE",
  "status": "MATHEMATICALLY SECURE",
  "recovered_plaintext_fields": [],
  "opaque_ciphertext": {
    "kem_ciphertext": {"bytes": 1088, "preview": "7c12d8a4f91e0b..."},
    "payload_ciphertext": {"bytes": 2856, "preview": "e8810c3b991a..."},
    "payload_tag": {"bytes": 16, "preview": "33f019b8..."},
    "nonce": {"bytes": 12, "preview": "91a2b4f7..."}
  },
  "visible_metadata": {
    "capsule_id": "qsc_7f2b918a3e0c45d1",
    "sender_id": "BARCGB22XXX",
    "recipient_id": "HDFCINBBXXX",
    "issued_at": "2026-09-13T01:30:00Z"
  }
}
```
- **Forensic Outcome:** The panel renders a **green shield banner**.
- **Recovered Plaintext:** Exactly `0` bytes. The attacker finds only non-sensitive routing headers (`sender_id`, `recipient_id`, `capsule_id`).
- **Cryptographic Resistance:** The payment itself is locked behind AES-256-GCM under an ML-KEM-768 shared secret. Breaking this requires solving Module-LWE over polynomial rings &mdash; which Shor's algorithm cannot solve.

---

## 5. Theoretical Summary: Middlebox Reality in Banking

Evaluators often ask: *"Why would an attacker control a proxy?"*

The answer is that the proxy is not an attacker:
1. Modern banks deploy dozens of middleboxes: **API Gateways (Kong, Apigee)**, **WAFs (Cloudflare, AWS WAF)**, **Service Mesh Sidecars (Envoy, Istio)**, and **Corporate TLS Inspection Appliances (Blue Coat, Zscaler)**.
2. Every one of these devices **terminates TLS** in order to inspect traffic.
3. If an adversary compromises a single proxy appliance or records the wire before and after it, traditional TLS provides zero confidentiality.
4. QSC encapsulates the payload at the origin client and keeps it encrypted through all proxies until reaching the final destination.
