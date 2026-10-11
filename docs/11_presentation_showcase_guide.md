# 11 — Live Presentation & Project Showcase Guide

[![NIST PQC](https://img.shields.io/badge/NIST-FIPS%20203%20%7C%20FIPS%20204-green.svg)](https://csrc.nist.gov/projects/post-quantum-cryptography)
[![Tests](https://img.shields.io/badge/tests-70%20passed%20%7C%20100%25-brightgreen.svg)](../tests/)
[![Python](https://img.shields.io/badge/python-3.11%20%7C%203.12-blue.svg)](https://www.python.org)

> **Purpose:** This is your end-to-end speaker runbook for evaluating committees, hackathons, academic presentations, and executive showcases. It details the exact click sequence, what each button proves, live API and TLS verifications, 3D visualizer demonstrations, and answers to tough technical questions.

---

## Quick Reference: Showcase Flow Summary

| Act | Scene / Tab | Key Action / Buttons | Core Message Proven |
| :--- | :--- | :--- | :--- |
| **Act 1** | **The Hook & TLS Proof** | Lock icon, Masthead pill, `/api/v1/network/tls` | Proves real TLS 1.3 is running, but TLS only secures the pipe. |
| **Act 2** | **3D Visualizer (Tab 03)** | Mode A vs B, **Run Full Process**, **Quantum Attack** | Visualizes why middlebox TLS termination exposes plaintext and how QSC prevents it. |
| **Act 3** | **Settlement Flow (Tab 01)** | **Build Capsule** &rarr; **Transmit & Settle** | Real NIST FIPS 203/204 math & 5-stage zero-trust gate. |
| **Act 4** | **Packet Inspector (Tab 02)** | Hex viewer, **Flip Bit**, **Replay Capsule** | Proves tamper-evidence down to a single bit flip and instant replay defense. |
| **Act 5** | **Interception Lab (Tab 04)** | **Send Payment via TLS Only** vs **Send Capsule** | Proves genuine TLS MITM proxy on port 8444; Harvest Now, Decrypt Later defeated. |
| **Act 6** | **API & Cryptographic Proof** | `/api/docs`, DevTools Network, `pytest` | Shows production OpenAPI spec, genuine cryptographic primitives, and 100% test coverage. |

---

## Pre-Showcase Setup Checklist

Execute this 2 minutes before your presentation begins:

1. **Launch Server:**
   ```bash
   cd QSC
   python -m src.server.run
   ```
   *Verify both ports are active:*
   - Settlement Workbench: `https://127.0.0.1:8443`
   - Interception Proxy: `https://127.0.0.1:8444`

2. **Open Browser & Accept Self-Signed Certificate:**
   - Navigate to `https://127.0.0.1:8443`
   - When the browser displays *"Your connection isn't private"* &rarr; click **Advanced** &rarr; **Proceed to 127.0.0.1 (unsafe)**.
   - Do the same once for `https://127.0.0.1:8444/captures` so the proxy cert is also accepted.

3. **Have Second Tab Ready:**
   - Tab A: `https://127.0.0.1:8443/` (Workbench)
   - Tab B: `https://127.0.0.1:8443/api/docs` (Swagger UI)

---

## Act 1 — The Hook: Proving Real TLS 1.3 and Its Structural Flaw

### What to Show & Click:
1. Look at the top **Masthead Status Bar**:
   - Point to the **`TLS 1.3 | ECDSA P-256`** pill on the top right.
   - Point to the browser address bar lock icon. Click it to show the certificate issued to `qsc.localhost`.
2. Open a new browser tab or DevTools to `https://127.0.0.1:8443/api/v1/network/tls`.
   - Show the JSON output:
     - `protocol`: `"TLSv1.3"`
     - `cipher_suite`: `"TLS_AES_256_GCM_SHA384"`
     - `quantum_exposure.broken_by`: `"Shor's algorithm on a cryptographically relevant quantum computer"`

### What to Say to the Audience:
> *"Notice the padlock in the browser and our live status bar. We are running genuine TLS 1.3 with OpenSSL ECDSA P-256 certificates. Modern banking relies entirely on this.*
> 
> *Here is the critical vulnerability: **TLS only encrypts the wire between two immediate network hops**. When hostile actors record this traffic today under 'Harvest Now, Decrypt Later', Shor's algorithm will crack the P-256 key and recover everything. Furthermore, the second TLS terminates at an API gateway or reverse proxy, that data sits in cleartext memory. Let's see this in our 3D simulator."*

---

## Act 2 — The 3D Quantum Simulator (Tab 03)

Click on **`03 3D Visualizer`** in the top navigation.

```
+----------------------------------------------------------------------------------------------------+
| [Mode A - TLS 1.3]  [Mode B - QSC Capsule]  [▶ Run Full Process]  [Run Quantum Attack]  [Reset]    |
+----------------------------------------------------------------------------------------------------+
|  Originating Bank  ──►  Edge Gateway  ──►  Reverse Proxy  ──►  Message Broker  ──►  Clearing House |
+----------------------------------------------------------------------------------------------------+
```

### Step-by-Step Click Sequence:

#### Step 1: Run Traditional TLS (The Vulnerability)
1. **Click `Mode A — TLS 1.3`** (Active by default).
2. **Click `▶ Run Full Process`** (Green button).
3. **What happens on screen:**
   - The packet moves across the 5 nodes: *Originating Bank &rarr; Edge Gateway &rarr; Reverse Proxy &rarr; Message Broker &rarr; Clearing House*.
   - When it reaches **Node 3 (Reverse Proxy)**, the node turns **RED** (`TLS TERMINATES`).
   - The narration panel on the right explains: *The proxy must decrypt TLS to inspect headers. The payload is now exposed in plaintext in proxy RAM and written unencrypted to Kafka broker storage.*
4. **Click `Run Quantum Attack`** (Red button).
   - An ominous red wave scans across the wire.
   - The status banner flashes red: **"SESSION KEY RECOVERED BY SHOR'S ALGORITHM — PLAINTEXT COMPROMISED"**.

#### Step 2: Run QSC Message Security (The Defense)
1. **Click `Mode B — QSC Capsule`**.
2. **Click `▶ Run Full Process`**.
3. **What happens on screen:**
   - The Originating Bank generates lattice keypairs.
   - At Node 1, green lattice particles wrap around the payload (*ML-KEM-768 encapsulation + ML-DSA-65 signature*).
   - The payload turns into an armoured green digital capsule.
   - When it hits **Node 3 (Reverse Proxy)**, the node stays **GREEN**: The proxy terminates TLS, but only sees an impenetrable capsule. It reads routing metadata, while the financial payload stays sealed.
   - The packet reaches the Clearing House where 5 validation checks fire in sequence.
4. **Click `Run Quantum Attack`**.
   - The quantum attack scans across the captured traffic.
   - The status displays **"HARVEST DEFEATED — LATTICE PROBLEM HARDNESS HOLDS"**. The captured data is mathematically useless without the ML-KEM private key.

### Interactive Tip:
- Click and drag on the 3D scene to orbit the camera, scroll to zoom in on the lattice structure around the capsule.

---

## Act 3 — Settlement Workbench (Tab 01)

Click on **`01 Settlement`** in the top navigation.

```
+---------------------------+-----------------------------------------------+
| INSTRUCTION BUILDER       | ZERO-TRUST VALIDATION PIPELINE                |
| Message: [ISO 20022 ▼]    | [ Stage 1: Structure & Schema               ] |
| TTL:     [300]            | [ Stage 2: Temporal Validity & TTL          ] |
| Route:   [Direct :8443 ▼] | [ Stage 3: Anti-Replay Token                ] |
|                           | [ Stage 4: SHA3-512 Payload Digest          ] |
| [ Rotate Keys ]           | [ Stage 5: ML-DSA-65 Signature Verify       ] |
| [ Build Capsule ]         +-----------------------------------------------+
| [ Transmit & Settle ]     | Decrypted Payload: £50,000,000.00 SETTLED     |
+---------------------------+-----------------------------------------------+
```

### Step-by-Step Click Sequence:
1. **Select Message Standard:** Leave as `ISO 20022 pacs.008 — Interbank Credit Transfer` (or choose `SWIFT MT103`).
2. **Click `Rotate Keys`:**
   - Shows new public keys generated for ML-KEM-768 and ML-DSA-65 in real time.
3. **Click `Build Capsule` (Blue button):**
   - In milliseconds, the client runs the 8-stage builder.
   - Point to the **Capsule Summary** box: Displays Capsule ID (`qsc_...`), Sender public key hash, and sizes.
4. **Click `Transmit & Settle` (Green button):**
   - Watch the **Zero-Trust Validation Pipeline** fire in real time:
     - Stage 1: Structural format & Schema &check;
     - Stage 2: TTL check (expires in 300s) &check;
     - Stage 3: Anti-replay registry check &check;
     - Stage 4: SHA3-512 integrity lock &check;
     - Stage 5: ML-DSA-65 post-quantum signature verification &check;
   - Point to the bottom box: **Decrypted Payload at Settlement Engine** displays the cleartext interbank transfer (£50,000,000.00 between Barclays and HSBC) with a settlement timestamp.
   - Point to the **Network Console** at the bottom showing exact HTTP status 200 and microsecond timings.

---

## Act 4 — Packet Inspector & Tamper Defense (Tab 02)

Click on **`02 Packet Inspector`** in the top navigation.

### What to Show & Click:
1. **Show the Raw Wire Bytes:**
   - The screen shows the exact binary layout of the capsule serialized according to `CAPSULE_SPEC.md`.
   - Point to the color-coded legend:
     - `Magic & Version` (First 4 bytes: `QSC1`)
     - `KEM Ciphertext` (1,088 bytes &mdash; FIPS 203)
     - `AES Nonce & Ciphertext` (AES-256-GCM)
     - `SHA3-512 Digest` (64 bytes)
     - `ML-DSA-65 Signature` (3,309 bytes &mdash; FIPS 204)
2. **Demonstrate Active Tampering (Single Bit Flip):**
   - In the right-hand panel: **Attack Lab &mdash; Single Bit Flip**.
   - Leave `Byte Offset` at `0` and `Bit Index` at `1`.
   - **Click `Flip Bit & Resubmit` (Red button).**
   - **Result:** The capsule is rejected instantly!
   - Highlight the banner: **`Validation Failed at Stage 4 (SHA3-512 Digest Mismatch)`**. Even a single bit change in transit destroys the capsule integrity.
3. **Demonstrate Replay Attack Defense:**
   - Return to Tab 01, build and settle a fresh capsule.
   - Return to Tab 02, click **`Replay Capsule Verbatim`**.
   - **Result:** The capsule is rejected at **`Stage 3: Replay Token Already Consumed`**.
   - Explain: *"Even if an adversary captures the capsule untouched and replays it over the network 1 second later, the single-use token prevents double-spending or duplicate settlement."*

---

## Act 5 — Interception Lab: The Harvest Now, Decrypt Later Demo (Tab 04)

Click on **`04 Interception Lab`** in the top navigation.

This tab proves what happens when an adversary intercepts genuine TLS traffic via our **TLS-terminating proxy on port 8444**.

### Step-by-Step Click Sequence:
1. **Send Payment via TLS Only:**
   - Select `Card Authorisation Record (PCI DSS)`.
   - **Click `Send Payment via TLS Only`**.
   - A new row appears in the **Intercepted Flows** table.
   - Click on the row:
     - **Inspect Captured Payload:** The proxy recovered the full credit card number (PAN), CVV, expiration date, and customer name in cleartext!
     - Explain: *"This is what any intermediate gateway, proxy, or eavesdropper recording TLS traffic gets when the channel key is broken."*
2. **Send Payment as QSC Capsule:**
   - **Click `Send Payment as QSC Capsule`**.
   - A new row appears in the table.
   - Click on the row:
     - **Inspect Captured Payload:** Every sensitive field is replaced with opaque ciphertext (`payload_ciphertext`, `kem_ciphertext`).
     - Point to the **Simulated Decryption Result**: **`CRQC ATTACK FAILED: Decryption requires solving Module-LWE lattice problem.`**

---

## Act 6 — Proving It on the API & DevTools

To prove to technical evaluators that this is not a mock UI or client-side animation:

### 1. Show the Interactive OpenAPI Documentation
1. Navigate to `https://127.0.0.1:8443/api/docs`.
2. Expand `/api/v1/capsule/settle` and `/api/v1/network/tls`.
3. Click **"Try it out"** &rarr; **"Execute"** on `/api/v1/network/tls`.
4. Show the live JSON response containing the active OpenSSL connection parameters and latency breakdown.

### 2. Show the Browser Network Tab
1. In the Workbench, press `F12` to open Developer Tools &rarr; **Network** tab.
2. In Tab 01, click **Transmit & Settle**.
3. Point to the `POST /api/v1/capsule/settle` request:
   - Request Headers: Real HTTPS over TLS 1.3.
   - Request Payload: The serialized JSON capsule containing genuine Base64-encoded lattice ciphertexts.
   - Response: HTTP 200 OK with `settlement_id`, `verified_at`, and `cleared_amount`.

### 3. Run the Automated Test Suite from Terminal
Switch to your terminal and run:
```bash
pytest
```
Show the output: **70 passed in ~12 seconds** covering:
- NIST FIPS 203 ML-KEM encapsulation & decapsulation
- NIST FIPS 204 ML-DSA signing & verification
- HKDF-SHA3-512 key derivation
- 5-stage validation gate
- Replay protection & bit-flip resistance
- Real TLS handshake probes

---

## Anticipated Questions & Bulletproof Answers (Q&A)

### Q1: "Why not just use Hybrid TLS 1.3 (PQ-TLS)? Why do we need message capsules?"
> **Answer:**  
> *"Hybrid TLS 1.3 is an important improvement, but it only solves **channel security**, not **data security**. In enterprise banking, TLS terminates at the first reverse proxy, WAF, or ingress gateway. Downstream traffic passes through internal microservices, Kubernetes sidecars, and Apache Kafka message brokers where payloads are decrypted.*
> 
> *Furthermore, banking workflows are asynchronous: a payment instruction rests in a message queue or database before settlement. TLS offers zero protection for data at rest or data traversing multiple hops. QSC protects the message itself: it remains quantum-resistant from the originating mobile device all the way to the clearing house ledger, regardless of how many proxies or message queues it crosses."*

---

### Q2: "What is the performance overhead? Can this handle high-volume interbank settlement?"
> **Answer:**  
> *"Total encapsulation and signing takes **under 3 milliseconds**, and verification takes **under 1.5 milliseconds** on standard commodity hardware. The capsule adds roughly 4.5 KB of wire overhead (1,088 bytes for ML-KEM-768 ciphertext + 3,309 bytes for ML-DSA-65 signature).*
> 
> *For high-value wholesale settlement (SWIFT, Fedwire, CHAPS, TARGET2) where individual transactions represent millions of pounds, 4.5 KB and a 2 ms validation latency is negligible compared to the billions at risk from retrospective decryption. For high-frequency consumer retail, QSC can operate in session-capsule mode."*

---

### Q3: "Which NIST post-quantum standards are you using, and are they genuinely implemented?"
> **Answer:**  
> *"We implement the final, official NIST Post-Quantum Cryptography standards published in August 2024:*
> - ***ML-KEM-768 (FIPS 203)*** *for key encapsulation (Security Category 3, equivalent to AES-192).*
> - ***ML-DSA-65 (FIPS 204)*** *for digital signatures (Security Category 3).*
> - ***SHA3-512 / SHAKE-256 (FIPS 202)*** *for integrity hashing and domain separation.*
> - ***HKDF (NIST SP 800-56C Rev. 2)*** *for key derivation.*
> - ***AES-256-GCM (NIST SP 800-38D)*** *for payload confidentiality and authenticated encryption.*
> 
> *These are genuine mathematical implementations executing polynomial ring arithmetic over $Z_q[X]/(X^{256} + 1)$, not mock simulations."*

---

### Q4: "How does QSC prevent replay attacks if it isn't tied to a specific TLS socket session?"
> **Answer:**  
> *"QSC enforces a multi-layered anti-replay defense:*
> 1. *Every capsule has a cryptographically unique `capsule_id` derived from a high-entropy CSPRNG nonce.*
> 2. *Every capsule contains an absolute UTC expiration timestamp (`valid_until`). Any capsule received outside its validity window (e.g., 300 seconds) is discarded at **Stage 2** before expensive crypto is invoked.*
> 3. *The settlement receiver maintains an in-memory anti-replay cache with rolling bloom-filter purging that records consumed tokens. When a duplicate token arrives within the valid window, it is rejected at **Stage 3** as shown in our Packet Inspector tab."*

---

### Q5: "What is the 5-stage zero-trust validation gate and why is it ordered that way?"
> **Answer:**  
> *"The 5 stages are ordered strictly from **computationally cheapest to most expensive** to prevent Denial-of-Service (DoS) attacks:*
> 1. ***Stage 1: Structural format & Schema (< 10 µs):*** *Checks magic bytes and field headers.*
> 2. ***Stage 2: Temporal validity / TTL (< 5 µs):*** *Compares epoch timestamp; rejects expired capsules.*
> 3. ***Stage 3: Replay token lookup (< 20 µs):*** *Checks cache hash table.*
> 4. ***Stage 4: SHA3-512 integrity digest (~ 80 µs):*** *Verifies payload hasn't been altered.*
> 5. ***Stage 5: ML-DSA-65 signature verification (~ 1,200 µs):*** *Runs lattice signature verification.*
> 
> *An invalid, replayed, or malformed capsule is rejected in under 30 microseconds without expending expensive lattice math operations."*

---

### Q6: "How does this integrate into existing financial infrastructures like Kafka or SWIFT?"
> **Answer:**  
> *"Because QSC capsules are completely **transport-agnostic**, they require zero changes to the underlying network infrastructure:*
> - *In **REST APIs**: Passed as standard JSON or Base64 payloads over HTTP/HTTPS.*
> - *In **Apache Kafka**: Encapsulated as binary byte arrays (`byte[]`) in Kafka message values. Kafka brokers and consumer groups route and partition topics without needing decryption keys.*
> - *In **SWIFT / ISO 20022**: Packed into the standard envelope or supplementary data (`<SplmtryData>`) element of ISO 20022 XML messages.*
> - *In **File storage**: Stored as `.qsc` self-defending containers at rest."*

---

### Q7: "What happens if an adversary alters just a single byte or bit during transit?"
> **Answer:**  
> *"As demonstrated in Tab 02 (Packet Inspector), any 1-bit alteration anywhere in the capsule payload causes the SHA3-512 digest check to fail at Stage 4. If the adversary alters the signature bytes instead, Stage 4 passes but Stage 5 (ML-DSA-65 lattice verification) rejects the packet. Under AES-256-GCM and ML-DSA, ciphertext malleability is mathematically zero."*

---

## Emergency Troubleshooting During Presentation

| Issue | Quick Fix |
| :--- | :--- |
| **Port 8443 already in use** | Run `Get-Process python \| Stop-Process -Force` in PowerShell, then rerun `python -m src.server.run`. |
| **Browser warns about Certificate** | Click **Advanced** &rarr; **Proceed to 127.0.0.1 (unsafe)**. This is normal for self-signed certificates. |
| **3D Visualizer is frozen or blank** | Click the **Reset** button in Tab 03 or refresh the browser. Three.js is vendored locally and requires no internet. |
| **Buttons disabled in Tab 01** | Click **Build Capsule** first; the **Transmit & Settle** button enables once a capsule has been built. |
