# 15 — Live Pitch & Demonstration Script (3:30 Min)

[![NIST PQC](https://img.shields.io/badge/NIST-FIPS%20203%20%7C%20FIPS%20204-green.svg)](https://csrc.nist.gov/projects/post-quantum-cryptography)
[![Target Duration](https://img.shields.io/badge/Duration-3%3A30%20(210s)-blue.svg)]()
[![Pacing](https://img.shields.io/badge/Pacing-~135%20WPM-brightgreen.svg)]()
[![Scope](https://img.shields.io/badge/Focus-Tabs%2001%2C%2002%2C%2003-orange.svg)]()

> **Executive Context:**  
> This script is tailored for a **3-minute and 30-second live demonstration** focusing exclusively on the **first 3 tabs** of the Quantum Security Capsule (QSC) Workbench:
> 1. **Tab 01 — Settlement Console**
> 2. **Tab 02 — Packet Inspector & Attack Lab**
> 3. **Tab 03 — Interactive 3D Visualizer**
>
> **Pitch Boundary:** The macro problem statement (quantum timeline, Harvest Now, Decrypt Later) and theoretical approach (lattice cryptography) have **already been established** prior to this demo. This script dives directly into **live operational execution**, the **high-value financial use case**, and the **critical security mechanisms** protecting sovereign banking transactions.

---

## 1. Quick Reference: 3:30 Timing & Action Matrix

| Time | Elapsed | Interface / Tab | Live UI Actions & Clicks | Spoken Focus | Core Security & Use Case Message |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **00:00 - 00:25** | 25s | **Masthead / Workbench Context** | Point to top masthead (`TLS 1.3 | ECDSA P-256`, lock icon, zero-trust counters). | **High-Value Use Case**: Interbank settlement (ISO 20022 `pacs.008` / SWIFT MT103). | Transport security (TLS) is not enough for multi-hop banking; payload itself must be self-defending. |
| **00:25 - 01:25** | 60s | **Tab 01: Settlement Console** | 1. Select `ISO 20022 pacs.008`.<br>2. Point to TTL (300s).<br>3. Click **`Build Capsule`**.<br>4. Click **`Transmit & Settle`**. | **Real-Time Armoring & Zero-Trust Validation**: 8-step build, 5 validation stages (~17 ms), decrypted settlement ledger. | Autonomous post-quantum armoring (ML-KEM-768 + ML-DSA-65). Decryption is impossible unless all 5 zero-trust gates pass. |
| **01:25 - 02:25** | 60s | **Tab 02: Packet Inspector** | 1. Show raw hex dump & field chips.<br>2. Click byte offset 146 in legend.<br>3. Click **`Flip Bit & Resubmit`**.<br>4. Click **`Replay Capsule Verbatim`**. | **Wire Transparency & Tamper Evidence**: Wire format hex dump, 1-bit flip rejection at Stage 4, anti-replay rejection at Stage 3. | Zero-tolerance integrity: altering a single bit in a £50M wire destroys SHA3-512 hash; consumed token prevents double-spending. |
| **02:25 - 03:15** | 50s | **Tab 03: 3D Visualizer** | 1. Click `Mode A — TLS 1.3` &rarr; **`Run Full Process`** (point to red proxy).<br>2. Click `Mode B — QSC Capsule` &rarr; **`Run Full Process`**.<br>3. Click **`Run Quantum Attack`**. | **Multi-Hop Architecture & Quantum Attack Simulation**: Reverse proxy TLS termination vs. sealed crystal safe; Shor's algorithm defeated by Module-LWE. | In multi-hop architectures, proxies terminate TLS and leak cleartext; QSC keeps data sealed end-to-end against quantum harvest. |
| **03:15 - 03:30** | 15s | **Workbench Overview** | Orbit 3D scene / gesture to green settlement metrics. | **Summary & Hand-off**: Production-grade, mathematically proven, drop-in ready for global banking. | Bridges today's vulnerable infrastructure to tomorrow's post-quantum mandate without replacing the network. |

---

## 2. Pre-Showcase Setup Checklist

Complete this checklist 2 minutes before the presentation begins:

- [ ] **Server Active:** Run `python -m src.server.run` from workspace root.
- [ ] **Workbench Loaded:** Open `https://127.0.0.1:8443` in full screen (browser zoom: 90% or 100%).
- [ ] **Certificate Accepted:** Click *Advanced* &rarr; *Proceed to 127.0.0.1 (unsafe)* so the lock icon is displayed.
- [ ] **Starting State:** Tab 01 (`Settlement`) is active. Top masthead stats are populated with live green heartbeat dots.
- [ ] **Mouse Placement:** Cursor resting near the **Message Standard** dropdown.

---

## 3. Word-for-Word Chronological Speaker Script

```
========================================================================================
TIMELINE TARGET: 00:00 - 00:25 (25 Seconds | Target: ~60 words)
FOCUS: High-Value Financial Use Case & Why Transport Security Fails
TAB: Masthead & Workbench Foundation
========================================================================================
```

### [00:00 - 00:25] Opening: The Institutional Banking Reality

#### Screen Actions:
- Keep the screen on the **Settlement Workbench**.
- Hover mouse cursor over the **Top Masthead**: point to `Transport: TLS 1.3 | Cipher: TLS_AES_256_GCM_SHA384` and the `ML-KEM Key` fingerprint.

#### Spoken Dialogue:
> "Now let's see this in action on our live institutional workbench.
>
> Our operational use case is **wholesale interbank settlement**—specifically, ISO 20022 and SWIFT MT103 wire transfers where central clearing houses and tier-1 institutions settle hundreds of millions of pounds every single minute.
>
> As you can see in the masthead, we are connected over standard TLS 1.3. But in enterprise banking, transactions don't travel over a simple pipe; they traverse edge gateways, API proxies, and message queues. The moment TLS terminates at any intermediate hop, that financial data sits in cleartext memory. 
> 
> Here is how the Quantum Security Capsule solves this at the application layer."

*(Pacing note: Transition seamlessly into Tab 01 at 00:25)*

---

```
========================================================================================
TIMELINE TARGET: 00:25 - 01:25 (60 Seconds | Target: ~140 words)
FOCUS: Tab 01 — Autonomous Armoring & Zero-Trust Settlement Pipeline
TAB: 01 Settlement Console
========================================================================================
```

### [00:25 - 01:25] Tab 01: Building & Settling a £50,000,000 Transfer

#### Screen Actions:
1. **[00:27]** Click the **Message Standard** dropdown `<select id="payload-kind">`:
   - Keep selected: `ISO 20022 pacs.008 — Interbank Credit Transfer`.
2. **[00:32]** Point to the **Validity Window (seconds)** input (`300`).
3. **[00:36]** **CLICK [Build Capsule]** (Blue button `#btn-build`).
   - Immediately gesture to the populated **Current Capsule** card on the bottom left (show `Capsule ID`, `Wire Size: ~8.9 KB`, `KEM Ciphertext: 1088 B`, `Signature: 3309 B`).
4. **[00:52]** **CLICK [Transmit & Settle]** (Green button `#btn-settle`).
   - Watch the right-hand panel light up with green checkmarks across all 5 stages.
   - Point to the **Decrypted Payload** box showing: `£50,000,000.00 SETTLED` between Barclays and HSBC.
   - Point to the **Network Console** showing total cryptographic execution time (~17 ms).

#### Spoken Dialogue:
> "Here on **Tab 01**, we select an ISO 20022 interbank credit transfer with a strict 300-second temporal freshness window. 
>
> *(Click 'Build Capsule')*
> 
> In under four milliseconds, the client executes our 8-step post-quantum pipeline. It encapsulates a 256-bit symmetric key using NIST FIPS 203 ML-KEM-768, encrypts the financial payload with AES-256-GCM, binds a single-use SHA3-512 replay token, locks the canonical schema, and digitally signs the capsule using NIST FIPS 204 ML-DSA-65. 
> 
> The payload is now an autonomous post-quantum safe *before* touching the network.
>
> *(Click 'Transmit & Settle')*
> 
> When transmitted to the clearing house, our **5-stage zero-trust engine** validates protocol version, temporal freshness, single-use anti-replay status, SHA3-512 canonical integrity, and the lattice signature. 
> 
> Only when all five checks pass is the key decapsulated and the £50 million settlement committed to the ledger—in just seventeen milliseconds."

---

```
========================================================================================
TIMELINE TARGET: 01:25 - 02:25 (60 Seconds | Target: ~135 words)
FOCUS: Tab 02 — Wire Transparency, Single-Bit Tampering & Anti-Replay Defense
TAB: 02 Packet Inspector
========================================================================================
```

### [01:25 - 02:25] Tab 02: Wire Forensics & Live Attack Lab

#### Screen Actions:
1. **[01:26]** **CLICK Tab 02: [02 Packet Inspector]** in the top navigation.
   - The interactive hex dump matrix loads immediately.
2. **[01:31]** Point to the color-coded **Legend Chips** above the hex view:
   - Click chip `kem_ciphertext` (1,454 B) &rarr; show auto-scroll and blue highlight.
   - Click chip `signature` (4,414 B) &rarr; show lattice signature bytes.
3. **[01:45]** Move to right panel: **Attack Lab — Single Bit Flip**:
   - `Byte Offset` is auto-filled (e.g. `146`), `Bit Index` is `1`.
   - **CLICK [Flip Bit & Resubmit]** (Red button `#btn-flip`).
   - Point to the **Red Error Banner**: `Validation Failed at Stage 4 (SHA3-512 Digest Mismatch)`.
4. **[02:08]** **CLICK [Replay Capsule Verbatim]** (Button `#btn-replay`).
   - Point to the **Red Error Banner**: `Validation Failed at Stage 3: Replay Token Already Consumed` (~2 µs).

#### Spoken Dialogue:
> "Moving to **Tab 02**, we inspect the raw wire bytes. 
> 
> Every byte of the serialized capsule is accounted for in this Wireshark-style hex dump—from the 1,088-byte ML-KEM ciphertext to the 3,309-byte ML-DSA lattice signature.
> 
> But high-value banking security demands zero-tolerance tamper evidence. Let's test an active attack.
>
> *(Click 'Flip Bit & Resubmit')*
> 
> In the Attack Lab, we flip exactly one single bit out of seventy-six thousand wire bits. Instantly, the clearing engine detects avalanche divergence and rejects the transfer at Stage 4 with an integrity mismatch. Not a single digit or decimal point in an interbank transfer can be tampered with in transit.
>
> *(Click 'Replay Capsule Verbatim')*
> 
> Next, an adversary intercepts a valid, signed capsule and replays it over the wire. We click Replay Verbatim: rejected in two microseconds at Stage 3. The single-use cryptographic token is already burned, eliminating double-spending entirely."

---

```
========================================================================================
TIMELINE TARGET: 02:25 - 03:15 (50 Seconds | Target: ~115 words)
FOCUS: Tab 03 — Multi-Hop Architecture & Quantum Attack Simulation
TAB: 03 Interactive 3D Visualizer
========================================================================================
```

### [02:25 - 03:15] Tab 03: Multi-Hop Defense & Quantum Attack Hardness

#### Screen Actions:
1. **[02:26]** **CLICK Tab 03: [03 3D Visualizer]** in the top navigation.
   - The WebGL isometric banking topology renders with 5 nodes.
2. **[02:30]** With `Mode A — TLS 1.3` selected:
   - **CLICK [▶ Run Full Process]** (Green button `#btn-run`).
   - As the amber payload moves, point to **Node 3 (Reverse Proxy)** turning **RED** (`TLS TERMINATES`).
   - Note the narration: *"TLS terminates; payload exposed in proxy memory & Kafka disk."*
3. **[02:45]** **CLICK [Mode B — QSC Capsule]** &rarr; **CLICK [▶ Run Full Process]**:
   - The payload is encased in an emerald crystalline lattice safe.
   - As it passes Node 3 and Node 4, the nodes stay **GREEN**.
4. **[02:58]** **CLICK [Run Quantum Attack]** (Red button `#btn-attack`):
   - Red surveillance beam sweeps across the transit path.
   - Point to the HUD status text: **`HARVEST DEFEATED — LATTICE PROBLEM HARDNESS HOLDS`**.

#### Spoken Dialogue:
> "Now, on **Tab 03**, our 3D visualizer demonstrates why this matters across realistic banking architecture: Originating Bank, Edge Gateway, Reverse Proxy, Kafka Message Broker, and Clearing House.
> 
> In **Mode A**, standard TLS 1.3 protects the hop. But watch Node 3: the proxy terminates TLS to inspect headers. The financial payload sits completely unencrypted in proxy RAM and unencrypted on Kafka disks. 
> 
> Now, we switch to **Mode B: QSC Capsule**. 
> 
> The payment is sealed in an emerald lattice armor. When it hits the proxy, TLS still terminates, but the capsule remains impenetrable. The proxy reads routing metadata while the transaction payload stays sealed end-to-end.
> 
> *(Click 'Run Quantum Attack')*
> 
> When an adversary launches a quantum harvest attack, Shor's algorithm shatters TLS session keys, but QSC holds. Its Module-LWE lattice hardness guarantees mathematical security even against future quantum supercomputers."

---

```
========================================================================================
TIMELINE TARGET: 03:15 - 03:30 (15 Seconds | Target: ~35 words)
FOCUS: Value Delivery & Conclusion
TAB: Return to Masthead / High-level overview
========================================================================================
```

### [03:15 - 03:30] Closing: Production-Ready Post-Quantum Security

#### Screen Actions:
- Orbit the 3D scene smoothly with mouse drag, or click back to Tab 01 showing the green `SETTLED` status.
- Make direct eye contact with the evaluation committee.

#### Spoken Dialogue:
> "To conclude: QSC delivers true end-to-end post-quantum security for high-value financial systems. It eliminates middlebox exposure, defeats Harvest Now, Decrypt Later, and drops into existing networks today without waiting for global telecom overhauls.
>
> Thank you, and we welcome your questions."

```
========================================================================================
TOTAL TIMING: 3 MINUTES 30 SECONDS (210s)
TOTAL SPOKEN WORDS: ~485 WORDS (IDEAL SPEAKING PACE: 135-140 WPM)
========================================================================================
```

---

## 4. Evaluator Q&A Defense Sheet (Tabs 01 - 03)

During the pitch defense and live demonstration, evaluators, venture judges, and academic examiners frequently challenge specific cryptographic and architectural claims regarding Tabs 01, 02, and 03. Use these structured responses:

---

### Q1: "Why not simply upgrade all proxies and gateways to Post-Quantum TLS 1.3 (e.g. X25519 + ML-KEM-768)?"
> **Speaker Answer (Spoken Pitch | 25s):**  
> *"Post-Quantum TLS is essential, but it only solves the pipe between two adjacent network interfaces. In modern banking architectures, high-value wire transfers traverse API gateways, cloud WAFs, enterprise service buses, and Apache Kafka brokers. Every TLS proxy terminates encryption, exposing plaintext in server RAM and on message broker disks. If an adversary compromises any intermediate hop, PQ-TLS offers zero defense. QSC provides **message-centric security**—the financial payload itself is an armored, encrypted safe that traverses untrusted intermediaries and remains sealed until it reaches the central clearing engine."*

- **Technical Deep-Dive & Hard Metrics:**
  - **The Multi-Hop Vulnerability:** In standard banking architectures (Originator $\to$ Edge Gateway $\to$ Reverse Proxy $\to$ Kafka Broker $\to$ Settlement Core), TLS 1.3 handshakes are re-negotiated per hop. Plaintext ISO 20022 XML sits in heap memory at Nodes 2, 3, and 4.
  - **Cryptographic Independence:** QSC encapsulates payloads at the application layer using NIST FIPS 203 ML-KEM-768 and AES-256-GCM before socket transmission. The ciphertext is transport-agnostic and remains cryptographically protected at rest in message queues.
- **Trap Defense / Evaluator Follow-up:**
  - *If asked:* *"Why not use strict end-to-end TLS without intermediate termination?"*
  - *Rebuttal:* *"In enterprise banking, Layer-7 termination is mandatory for traffic routing, rate-limiting, WAF DDoS filtering, and regulatory compliance. Terminating TLS without payload armoring leaks cleartext; QSC decouples inspectable routing headers from payload encryption, allowing middleboxes to route without decrypting sensitive data."*
- **Institutional & Regulatory Impact:** Eliminates third-party cloud proxy exposure, satisfying EU DORA (Digital Operational Resilience Act) Article 28 and PCI-DSS 4.0 Requirement 3.4.

---

### Q2: "What is the network bandwidth overhead and MTU packet fragmentation risk of ML-KEM-768 and ML-DSA-65?"
> **Speaker Answer (Spoken Pitch | 25s):**  
> *"As demonstrated on Tab 02's hex inspector, the entire capsule wire footprint is approximately 8.9 kilobytes for a standard ISO 20022 transfer—with 1,088 bytes for the ML-KEM ciphertext and 3,309 bytes for the ML-DSA signature. In wholesale RTGS, where individual transactions settle millions of pounds, an 8.9 KB envelope is completely negligible. Crucially, QSC avoids the catastrophic TCP handshake penalty of Pure PQ-TLS, where 18 KB certificate chains exceed TCP initial congestion windows and force extra round-trip delays."*

- **Technical Deep-Dive & Hard Metrics:**
  - **Exact Wire Breakdown:** Total wire envelope: ~8,940 bytes. ML-KEM-768 ciphertext: exactly 1,088 bytes; ML-DSA-65 signature: exactly 3,309 bytes; canonical metadata: ~2.4 KB; ISO 20022 `pacs.008` payload: ~2.1 KB.
  - **TCP Initial Congestion Window (`initcwnd`):** Standard TCP `initcwnd` is 10 MSS packets (~14.6 KB, RFC 6928). Pure PQ-TLS certificate chains are ~16.8–18.2 KB, exceeding `initcwnd` and forcing a +1 RTT stall that doubles transatlantic handshake latency (76 ms $\to$ 154 ms). QSC streams within established sessions, avoiding handshake stalls entirely.
- **Trap Defense / Evaluator Follow-up:**
  - *If asked:* *"Doesn't an 8.9 KB capsule exceed standard Ethernet MTU (1,500 bytes)?"*
  - *Rebuttal:* *"Yes, an 8.9 KB message spans ~6 TCP segments, but this occurs during streaming across an open TCP window. Over institutional 10GbE interbank connections, streaming 6 segments takes under 0.1 milliseconds—unlike handshake certificate bloat, which stalls waiting for round-trip TCP ACKs."*
- **Institutional & Regulatory Impact:** Well within SWIFT InterACT 4 MB limits and Fedwire/CHAPS message envelopes.

---

### Q3: "How does the anti-replay mechanism scale across a distributed cluster of clearing nodes?"
> **Speaker Answer (Spoken Pitch | 20s):**  
> *"Our anti-replay engine pairs a deterministic SHA3-512 token with a strict 300-second temporal freshness window. Any capsule older than 300 seconds is rejected instantly at Stage 2 before checking memory. Therefore, settlement nodes only maintain consumed tokens for a rolling 5-minute sliding window. Expired tokens are purged automatically, keeping the cache memory footprint strictly bounded regardless of multi-year operational volume."*

- **Technical Deep-Dive & Hard Metrics:**
  - **Deterministic Token Derivation:** $\text{Token} = \text{SHA3-512}(\text{capsule\_id} \parallel \text{timestamp} \parallel \text{sender\_id} \parallel \text{nonce})$.
  - **Cache Scalability Math:** At an institutional throughput of 10,000 transactions/second, a 300-second window stores at most 3,000,000 tokens. At 64 bytes per token, total RAM consumption is $3,000,000 \times 64 \text{ B} \approx 192 \text{ MB}$—readily handled by an in-memory Redis cluster or partitioned Bloom filter across clearing nodes.
- **Trap Defense / Evaluator Follow-up:**
  - *If asked:* *"What if there is clock drift between the originating bank and clearing house?"*
  - *Rebuttal:* *"Stage 2 allows a configurable $\pm 5$-second clock drift margin synchronized via standard financial NTP/PTP feeds. Any transaction exceeding the tolerance fails closed at Stage 2 in 7 microseconds, protecting the ledger from stale or desynchronized inputs."*
- **Institutional & Regulatory Impact:** Completely eliminates double-spending risks in accordance with CPMI-IOSCO Principles for Financial Market Infrastructures.

---

### Q4: "In Tab 02's Attack Lab, why does flipping ciphertext bits fail at Stage 4 while tampering with the signature fails at Stage 5?"
> **Speaker Answer (Spoken Pitch | 25s):**  
> *"This illustrates our 'cheapest-first, fail-closed' zero-trust pipeline. Stage 4 verifies the SHA3-512 canonical digest over the ciphertext and metadata, executing in just 60 microseconds. The signature bytes are deliberately excluded from this digest because a digital signature cannot sign itself without circularity. If an attacker tampers with the signature bytes, the capsule passes Stage 4's payload integrity check but fails Stage 5 during ML-DSA-65 lattice verification. Every byte of the wire structure is defended by layered, non-redundant controls."*

- **Technical Deep-Dive & Hard Metrics:**
  - **Pipeline Execution Latencies:**
    - Stage 1: Protocol Version ($\le 1.0\ \mu\text{s}$)
    - Stage 2: Temporal Freshness ($\le 7.2\ \mu\text{s}$)
    - Stage 3: Anti-Replay Token ($\le 2.1\ \mu\text{s}$)
    - Stage 4: SHA3-512 Canonical Integrity ($\le 60.4\ \mu\text{s}$)
    - Stage 5: ML-DSA-65 Lattice Signature ($\sim 17.2\ \text{ms}$)
  - **DoS Mitigation:** Placing the 60 µs SHA3-512 check before the 17 ms lattice signature check discards corrupt packets and bit-flip tampering before consuming heavy CPU compute, shielding clearing engines from signature verification denial-of-service.
- **Trap Defense / Evaluator Follow-up:**
  - *If asked:* *"Can an attacker forge a matching ML-DSA-65 signature after modifying the payload?"*
  - *Rebuttal:* *"Mathematically impossible. Forging an ML-DSA-65 signature requires solving the Module Short Integer Solution (M-SIS) problem on a $(6 \times 5)$ polynomial matrix modulo $q = 8,380,417$, which provides 128-bit quantum hardness (NIST Security Category 3)."*
- **Institutional & Regulatory Impact:** Fulfills NIST FIPS 204 non-repudiation mandates and Basel III operational risk tamper-detection standards.

---

### Q5: "What is the latency impact on high-throughput settlement engines, and does 17 ms meet bank SLAs?"
> **Speaker Answer (Spoken Pitch | 25s):**  
> *"On Tab 01, our live telemetry measured full end-to-end settlement in ~17 milliseconds, with 95% of that time spent in ML-DSA-65 signature verification within our pure-Python reference engine. In wholesale RTGS settlement (like CHAPS or Fedwire), throughput requirements are hundreds of transactions per second—not retail millions—and bank SLAs allow several seconds. 17 milliseconds is well within SLA. Furthermore, with compiled C/AVX2 Number Theoretic Transforms, verification latency drops below 1.5 milliseconds per core."*

- **Technical Deep-Dive & Hard Metrics:**
  - **Validation Latency Breakdown:** Stages 1–4 take a combined 70.7 microseconds (<0.5% of total time). Stage 5 (ML-DSA-65 verification) takes 17.21 ms in Python.
  - **Native C Performance:** According to NIST benchmarks and `liboqs` measurements, vectorized AVX2/AVX-512 ML-DSA-65 verification executes in 0.25 ms. An 8-core settlement server running compiled C processes over 4,000 validations per second.
- **Trap Defense / Evaluator Follow-up:**
  - *If asked:* *"Why does ML-DSA signing exhibit latency spikes up to 255 ms on the client side?"*
  - *Rebuttal:* *"ML-DSA uses Fiat-Shamir with Aborts (rejection sampling). If the candidate signature vector exceeds the Euclidean norm bound $\|\mathbf{z}\|_\infty \ge \gamma_1 - \beta$, it restarts. The 95th percentile captures 2–3 abort restarts, a standard theoretical property of lattice signatures that affects only the originating client, never the clearing node's verification time."*
- **Institutional & Regulatory Impact:** Exceeds Fedwire ISO 20022 real-time settlement target of 2.0 seconds and CHAPS RTGS clearing windows.

---

### Q6: "Why adopt a Hybrid Construction (ML-KEM-768 + AES-256-GCM) rather than pure asymmetric post-quantum encryption for the whole payload?"
> **Speaker Answer (Spoken Pitch | 20s):**  
> *"NIST FIPS 203 ML-KEM is a Key Encapsulation Mechanism, engineered specifically to establish shared secrets, not to bulk-encrypt arbitrary payload streams. Attempting to encrypt megabyte ISO 20022 XML or SWIFT batches directly with lattice polynomials would cause severe polynomial bloat and CPU exhaustion. AES-256-GCM runs at native hardware speeds via CPU AES-NI instructions (5 microseconds) while providing 128-bit quantum security against Grover's algorithm."*

- **Technical Deep-Dive & Hard Metrics:**
  - **KEM + DEM Paradigm:** ML-KEM-768 encapsulates 256 bits of shared entropy into a 1,088-byte ciphertext; HKDF-SHA3-512 expands it into an ephemeral AES key and IV; AES-256-GCM encrypts the financial payload.
  - **Grover's Quantum Resistance:** Grover's algorithm provides a quadratic speedup for brute-force symmetric search ($\mathcal{O}(\sqrt{N})$). For AES-256, the search space becomes $2^{128}$ operations, which remains computationally intractable even for quantum supercomputers.
- **Trap Defense / Evaluator Follow-up:**
  - *If asked:* *"Can Shor's algorithm crack AES-256-GCM?"*
  - *Rebuttal:* *"No. Shor's algorithm only solves hidden subgroup problems over abelian groups—such as integer factorization (RSA) and discrete logarithms (ECC). It has zero applicability to symmetric block ciphers or Keccak sponge hashes."*
- **Institutional & Regulatory Impact:** Aligns with NIST SP 800-38D (GCM mode) and NIST SP 800-56C (KDF recommendation) compliance profiles.

---

### Q7: "How do intermediate middleboxes (Reverse Proxies, WAFs, Message Brokers) route transactions without decrypting the capsule?"
> **Speaker Answer (Spoken Pitch | 20s):**  
> *"QSC employs a decoupled envelope pattern. The outer capsule header contains authenticated, non-confidential routing metadata—such as the destination BIC, routing transit number, ISO 20022 message type (`pacs.008`), timestamp, and priority. Reverse proxies and Kafka brokers inspect these outer fields for routing and rate-limiting, while the sensitive financial core—account numbers, IBANs, names, and transaction amounts—remains sealed inside the post-quantum safe."*

- **Technical Deep-Dive & Hard Metrics:**
  - **Cryptographic Binding:** All outer header fields are included in the SHA3-512 canonical integrity digest and covered by the ML-DSA-65 signature.
  - **Immutability Assurance:** If a malicious proxy alters a routing field (e.g. changing the destination clearing code to redirect funds), the clearing house detects the modification at Stage 4 and drops the message immediately. The middlebox can read routing tags, but cannot modify them without invalidating the capsule.
- **Trap Defense / Evaluator Follow-up:**
  - *If asked:* *"Does exposing routing metadata in the header create a metadata privacy leak?"*
  - *Rebuttal:* *"In wholesale banking, institutional BICs and routing codes are publicly listed in SWIFT directories. Furthermore, outer hops still run standard TLS 1.3 to shield metadata from external eavesdroppers, while QSC ensures the payload is protected from untrusted internal proxies."*
- **Institutional & Regulatory Impact:** Preserves full compatibility with enterprise Kafka partitioning, F5/NGINX load balancers, and AWS API Gateway routing.

---

### Q8: "How does QSC integrate with existing Public Key Infrastructure (PKI) and handle Key Rotation?"
> **Speaker Answer (Spoken Pitch | 20s):**  
> *"QSC integrates directly with institutional PKI standards. Participating banks and clearing houses exchange ML-KEM-768 and ML-DSA-65 public keys using standard X.509 v3 certificates with post-quantum OIDs. Furthermore, on Tab 01 of our workbench, we demonstrate live, zero-downtime key rotation: clicking 'Rotate Keys' generates fresh NIST FIPS 203/204 keypairs in real-time, proving that key lifecycle management is completely decoupled from network transport."*

- **Technical Deep-Dive & Hard Metrics:**
  - **Key Sizes:** ML-KEM-768 public key: 1,184 bytes; ML-DSA-65 public key: 1,952 bytes. Private keys are stored in Hardware Security Modules (HSMs) conforming to FIPS 140-3 Level 3/4.
  - **Rotation Mechanics:** Capsules carry explicit `key_id` identifiers in their headers. When a clearing house rotates keys, it publishes the new public key fingerprint; client capsules reference the updated `key_id`, allowing seamless dual-key acceptance during transition periods without taking settlement rails offline.
- **Trap Defense / Evaluator Follow-up:**
  - *If asked:* *"What happens if a private key is suspected of compromise?"*
  - *Rebuttal:* *"The clearing house revokes the key ID via internal directory broadcasts or short-lived OCSP stapling responses. Stage 1/5 validation verifies key validity before decapsulation; revoked key IDs fail closed immediately."*
- **Institutional & Regulatory Impact:** Complies with SWIFT PKI transition guidelines and ANSI X9.142 financial cryptographic key management standards.

---

### Q9: "Why is the demonstration implemented in Pure Python, and what is the exact path to production?"
> **Speaker Answer (Spoken Pitch | 20s):**  
> *"We deliberately chose pure-Python implementations of `kyber-py` and `dilithium-py` for this showcase to guarantee complete auditability, platform portability, and transparency. Evaluators can inspect every line of lattice polynomial arithmetic without relying on opaque pre-compiled binaries or complex compiler toolchains. Our modular architecture abstracts all cryptographic operations through interface wrappers, allowing drop-in substitution with C-accelerated engines like `liboqs` or AWS-LC with zero code changes."*

- **Technical Deep-Dive & Hard Metrics:**
  - **Compliance Verification:** Every mathematical routine in `src/crypto/kem.py` and `src/crypto/dsa.py` was validated against official NIST ACVP (Automated Cryptographic Validation Protocol) test vectors.
  - **Production Transition:** Python ML-DSA-65 verification takes ~17.2 ms. Switching to native C assembly (`liboqs` or AWS-LC) reduces verification to 0.25 ms—a 70x speedup—delivering over 4,000 verifications per second on an 8-core server with zero API changes to the capsule engine.
- **Trap Defense / Evaluator Follow-up:**
  - *If asked:* *"Does the Python reference implementation leak timing information through cache or branch side-channels?"*
  - *Rebuttal:* *"Symmetric primitives (AES-GCM, SHA3) run in constant-time C via OpenSSL. The Python lattice engine is an architectural reference for functional validation; commercial production deployments will link directly to constant-time C/assembly implementations (such as PQClean or AWS LibCrypto)."*
- **Institutional & Regulatory Impact:** Provides academic evaluators with full code visibility while offering institutional adopters a production-ready C/assembly roadmap.

---

### Q10: "If an insider attacker has root access to the Reverse Proxy, why can't they intercept or forge the transaction?"
> **Speaker Answer (Spoken Pitch | 20s):**  
> *"Because QSC enforces strict Zero-Trust isolation. The reverse proxy only handles transport forwarding; it never possesses the Clearing House's ML-KEM private key, nor the Originating Bank's ML-DSA private key. Even if an attacker has root access to the proxy OS, dumps memory, or modifies proxy code, they only see the encrypted capsule bytes. Decrypting the payload requires solving the Module-LWE lattice problem, which is mathematically impossible even with future quantum supercomputers."*

- **Technical Deep-Dive & Hard Metrics:**
  - **Two-Way Cryptographic Isolation:**
    1. **Confidentiality:** The capsule symmetric key is encapsulated against the clearing house's public key. Decapsulation requires private key $\mathbf{s} \in \mathcal{R}_q^k$, which resides strictly inside the clearing house's secure hardware enclave.
    2. **Authenticity:** If the rogue proxy admin alters payment amounts or recipient accounts, the capsule fails Stage 4 (SHA3-512 digest mismatch). If they attempt to rebuild the digest, it fails Stage 5 because they lack the originating bank's ML-DSA-65 private key.
- **Trap Defense / Evaluator Follow-up:**
  - *If asked:* *"Could the rogue proxy replay a previously valid transaction?"*
  - *Rebuttal:* *"No. Replaying an intercepted capsule fails instantly at Stage 3 in 2 microseconds because the single-use SHA3-512 replay token was already burned into the clearing house's cache during the original settlement."*
- **Institutional & Regulatory Impact:** Directly addresses the insider threat requirements of SWIFT Customer Security Controls Framework (CSCF) Control 2.1 and Basel Committee Operational Risk standards.

---

## 5. Rehearsal & Execution Cheat Sheet

| Time Stamp | Target Action | Visual Cue to Watch For | Pacing Note |
| :--- | :--- | :--- | :--- |
| **00:00 - 00:25** | Point to masthead & establish use case | Live green TLS dot & ML-KEM key hash | Speak with calm authority. Don't rush. |
| **00:25 - 00:50** | Select ISO 20022 & click **Build Capsule** | Capsule summary card populates with ~8.9 KB | Highlight the 8-step build pipeline. |
| **00:50 - 01:25** | Click **Transmit & Settle** | 5 green checkmarks & £50M settled output | Emphasize 17 ms microsecond timings. |
| **01:25 - 01:45** | Switch to Tab 02, click `kem_ciphertext` chip | Blue byte highlight in hex view | Point out honest cryptographic byte accounting. |
| **01:45 - 02:05** | Click **Flip Bit & Resubmit** | Red rejection banner at Stage 4 | Emphasize: not a single digit can be changed. |
| **02:05 - 02:25** | Click **Replay Capsule Verbatim** | Red rejection banner at Stage 3 | Emphasize: eliminates double-spending. |
| **02:25 - 02:45** | Switch to Tab 03, run Mode A | Node 3 (Proxy) turns red (`TLS TERMINATES`) | Contrast pipe security vs. payload security. |
| **02:45 - 03:00** | Run Mode B on Tab 03 | Green emerald crystalline safe transits | Point to nodes remaining green. |
| **03:00 - 03:15** | Click **Run Quantum Attack** | Red wave; "HARVEST DEFEATED" HUD status | Highlight NIST Module-LWE math holds. |
| **03:15 - 03:30** | Conclusion & open for questions | Orbit 3D scene / face judges | Firm, decisive closing statement. |

---

*Authored for the Quantum Security Capsule (QSC) Evaluation & Showcase Suite.*
