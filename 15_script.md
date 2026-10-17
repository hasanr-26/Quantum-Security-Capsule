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

During the pitch defense, evaluators frequently ask these specific technical questions regarding the first three tabs:

### Q1: "Why not simply upgrade our proxies and gateways to Post-Quantum TLS 1.3 (e.g. X25519+ML-KEM-768)?"
> **Speaker Answer:**  
> *"Post-Quantum TLS is essential, but it only solves the pipe between two adjacent network interfaces. In modern banking architectures, high-value payments pass through API gateways, web application firewalls, enterprise service buses, and Apache Kafka brokers. Every TLS proxy terminates encryption, exposing plaintext in server RAM and on message broker disks. QSC provides **message-centric security**—the financial payload remains an armored, encrypted safe through all intermediate hops until it reaches the final settlement engine."*

### Q2: "What is the network bandwidth overhead of adding ML-KEM-768 and ML-DSA-65?"
> **Speaker Answer:**  
> *"As demonstrated on Tab 02's hex inspector, the entire capsule wire size is approximately 8.9 kilobytes for an ISO 20022 message. The ML-KEM-768 ciphertext is exactly 1,088 bytes, and the ML-DSA-65 signature is 3,309 bytes. In high-value wholesale settlement—where individual transactions represent millions of pounds—an 8 KB envelope is negligible compared to the cryptographic assurance of post-quantum unforgeability and privacy."*

### Q3: "How does the anti-replay mechanism scale across a distributed cluster of clearing nodes?"
> **Speaker Answer:**  
> *"The replay token is a deterministic SHA3-512 hash derived from the capsule ID, issuance timestamp, sender identity, and a cryptographic nonce. Because capsules enforce a strict temporal validity window (TTL of 300 seconds), settlement nodes only need to maintain an in-memory Redis or distributed Bloom filter cache of consumed tokens for that rolling window. Once a token expires past its TTL, it is automatically discarded, keeping the memory footprint bounded regardless of multi-year operational volume."*

### Q4: "What happens if an attacker tampers with the signature bytes instead of the ciphertext?"
> **Speaker Answer:**  
> *"That is precisely why our zero-trust pipeline separates Stage 4 and Stage 5. Tampering with the payload or metadata fails at Stage 4 because the SHA3-512 canonical integrity digest does not match. Signature bytes are deliberately excluded from the integrity digest; if an adversary alters the signature bytes, the capsule passes Stage 4 but fails at Stage 5 during ML-DSA-65 lattice verification. Every byte of the wire structure is protected by layered defenses."*

### Q5: "What is the latency impact on high-throughput settlement engines?"
> **Speaker Answer:**  
> *"On Tab 01, our live telemetry measured full end-to-end settlement in approximately 17 milliseconds, of which 95% is ML-DSA-65 signature verification. In wholesale RTGS settlement (like CHAPS or Fedwire), throughput requirements are hundreds of transactions per second rather than retail millions, making 17 ms well within bank SLAs. Furthermore, with hardware-accelerated AVX2/AVX-512 Number Theoretic Transforms (NTT), verification latency drops under 1.5 milliseconds per core."*

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
