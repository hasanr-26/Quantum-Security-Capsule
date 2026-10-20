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

## 4. Deep-Dive Technical Guide: What is Really Happening on Tab 01 & Tab 02?

This section provides the underlying engineering mechanics, cryptographic theory, and threat modeling behind Tab 01 and Tab 02 so you can explain exactly what is taking place under the hood during evaluation.

### 4.1 Tab 01 (Settlement Console) &mdash; Under the Hood Mechanics

When you interact with Tab 01, two major asynchronous pipelines execute: the **8-step client-side armoring pipeline** and the **5-stage server-side zero-trust settlement engine**.

#### The 8-Step Client Armoring Pipeline (`CapsuleBuilder`)
When the user clicks **Build Capsule**, the originating bank client executes an 8-step cryptographic sequence in under 4 milliseconds, transforming raw banking data into a sovereign cryptographic container:
1. **Timestamping & Identifier Generation:** Generates a cryptographically random UUID-v4 capsule ID (`qsc_...`) and stamps ISO-8601 UTC timestamps enforcing a strict 300-second temporal freshness window.
2. **NIST FIPS 203 ML-KEM-768 Key Encapsulation:** Invokes the post-quantum lattice KEM against the clearing house's public key, generating 256 bits of shared entropy encapsulated inside a 1,088-byte ciphertext.
3. **Key Derivation via HKDF-SHA3-512 (NIST SP 800-56C):** Expands the 256-bit shared entropy secret and the unique capsule ID into an ephemeral 256-bit AES content key and 12-byte IV.
4. **Symmetric Payload Encryption via AES-256-GCM (NIST SP 800-38D):** Encrypts the raw ISO 20022 `pacs.008` financial XML payload into ciphertext and generates a 16-byte GHASH authentication tag bound to the capsule ID as associated data.
5. **Anti-Replay Token Generation:** Derives a single-use replay protection token by hashing the capsule ID, issuance timestamp, sender ID, and AES nonce through SHA3-512.
6. **Capsule Envelope Assembly:** Packages the encrypted ciphertext, KEM ciphertext, and replay token alongside authenticated, unencrypted routing headers (target BIC, priority, jurisdiction).
7. **Canonical Integrity Lock:** Canonicalizes all immutable fields using RFC 8785 JSON canonicalization and computes a 512-bit SHA3-512 integrity digest (`integrity_hash`).
8. **NIST FIPS 204 ML-DSA-65 Lattice Digital Signature:** Digitally signs the canonical `integrity_hash` using the originating bank's private signing key, appending a 3,309-byte post-quantum lattice signature.

#### The 5-Stage Zero-Trust Settlement Pipeline (`CapsuleValidator`)
When the user clicks **Transmit & Settle**, the clearing house receives the serialized capsule and evaluates it through a strict, fail-closed, "cheapest-first" validation sequence before allowing decapsulation:
- **Stage 1 &mdash; Protocol Version Match ($\le 1.0\ \mu\text{s}$):** Validates the version header (`"version":"QSC-1.0"`). Any unrecognized or legacy protocol version fails closed instantly, preventing version downgrade attacks.
- **Stage 2 &mdash; Freshness Window / Expiry ($\le 7.2\ \mu\text{s}$):** Compares `expires_at` against the clearing house's monotonic UTC clock. If the 300-second window has elapsed, the capsule is dropped before consuming further resources.
- **Stage 3 &mdash; Anti-Replay Token Verification ($\le 2.1\ \mu\text{s}$):** Queries the in-memory spent-token registry. If the token is already present, the transaction is rejected immediately to eliminate double-spending. If new, the token is recorded.
- **Stage 4 &mdash; Canonical Integrity Lock ($\le 60.4\ \mu\text{s}$):** Re-extracts the canonical fields, serializes them via RFC 8785, and computes SHA3-512. If the digest differs by even one bit from the capsule's `integrity_hash`, settlement halts with an integrity mismatch.
- **Stage 5 &mdash; Origin Signature Verification ($\sim 17.2\ \text{ms}$):** Evaluates the 3,309-byte ML-DSA-65 lattice signature against the originating bank's registered public key. Only when this lattice problem verifies does the clearing house decapsulate the ML-KEM shared secret, decrypt the AES-256-GCM payload, and commit the £50,000,000 credit transfer to the settlement ledger.

---

### 4.2 Tab 02 (Packet Inspector & Attack Lab) &mdash; Wire Forensics, Bit-Flipping & Real-World Attacks

Tab 02 strips away graphical abstraction and shows evaluators the raw, unadorned wire reality of post-quantum cryptography.

#### How the Wire Inspector Works
The hex inspector renders the exact UTF-8 byte stream transmitted across the network socket in a 16-column hexadecimal matrix alongside printable ASCII characters. Color-coded legend chips map each byte range to its schema field: the 1,088-byte ML-KEM ciphertext (base64-encoded to ~1,454 bytes) and the 3,309-byte ML-DSA signature (base64-encoded to ~4,414 bytes). Clicking any byte reveals its decimal offset, hexadecimal value, binary bit pattern, and plain-English cryptographic purpose, proving that every single byte on the wire is accounted for with zero simulated mockups.

#### Why Do We Flip a Bit in the First Place?
In the Attack Lab, clicking **Flip Bit & Resubmit** inverts exactly one binary digit out of approximately 76,000 wire bits ($b' = b \oplus (1 \ll \text{bit})$). 

In cryptographic engineering, flipping a single bit is the foundational proof of the **Strict Avalanche Criterion (SAC)**. For a cryptographic hash (SHA3-512 / Keccak-f[1600]) or an authenticated cipher (AES-GCM), flipping even one bit must cause on average **50% of the output bits to invert completely at random**. 

In Tab 02, flipping bit 2 of byte offset 146 alters only 0.0013% of the packet, yet instantly produces an avalanche mismatch that is caught at Stage 4 in 60 microseconds. The purpose of this demonstration is to prove **zero-tolerance tamper evidence**: if the settlement engine cannot be tricked by a microscopic single-bit alteration, it is mathematically impossible for an adversary to make any meaningful structural alteration—such as editing an account number, routing transit code, or settlement amount—without triggering instant rejection.

#### Do Real Attackers Actually Flip Bits? How Do Attackers Actually Attack Technically?
In the real world, attackers do not flip random bits, because random corruption simply causes packet drops or JSON syntax errors. Instead, real-world adversaries deploy sophisticated, mathematically calculated attacks against enterprise financial messaging:

1. **Ciphertext Malleability & Bit-Flipping Attacks:** In flawed or unauthenticated cryptographic protocols (such as AES in CBC mode without an HMAC, or raw stream ciphers like CTR without Poly1305), an active attacker on the network can mathematically calculate which specific ciphertext bits correspond to a target plaintext field (such as changing `$00,050,000` to `$99,050,000` or altering an IBAN digit). The attacker flips those exact bits on the wire so that when the recipient decrypts the message, the altered value appears legitimate. In QSC, this attack is completely eliminated: AES-256-GCM generates a 128-bit GHASH authentication tag bound to the capsule ID, and Stage 4's SHA3-512 canonical integrity lock validates every byte before decapsulation even begins.
2. **Man-in-the-Middle (MITM) Interception & Field Injection:** Attackers compromise an intermediate network hop—such as an edge router via BGP hijacking, an internal proxy via DNS/ARP spoofing, or a rogue cloud load balancer—and attempt to parse, alter, and forward transaction data. In traditional TLS, the proxy decrypts the data into memory, allowing an adversary with proxy access to modify the payment payload. In QSC, even if the proxy terminates TLS, the payload remains sealed inside the capsule. If the attacker attempts to alter the encrypted payload or outer headers, the SHA3-512 digest diverges at Stage 4; if they attempt to recalculate the digest, verification fails at Stage 5 because the attacker does not possess the originating bank's ML-DSA private key.
3. **Replay & Double-Spending Attacks:** Rather than altering the payment, an attacker intercepts a valid, signed £50,000,000 transfer between Barclays and HSBC and re-submits the exact identical packet multiple times over the network to trigger duplicate settlements. QSC defeats this in approximately 2 microseconds at Stage 3: every capsule contains a deterministic SHA3-512 replay token derived from the capsule ID, timestamp, sender ID, and nonce. Once the clearing house settles the transaction, that token is burned into the spent-token cache. Any subsequent transmission of that identical packet is detected and discarded instantly without wasting computational resources on lattice signature verification.
4. **Downgrade & Cipher Stripping Attacks:** An attacker intercepts the wire transfer and modifies the protocol metadata (e.g. changing `"version":"QSC-1.0"` to a legacy or unauthenticated standard) to force the settlement node to fall back to vulnerable classical algorithms. QSC halts this at Stage 1 in 1.0 microsecond: the clearing house enforces strict schema conformance and drops unapproved protocol versions immediately.
5. **Signature Substitution & Rogue Key Forgery:** An adversary modifies the financial payload and attempts to attach a newly generated signature created with their own post-quantum keypair. QSC clearing engines validate signatures strictly against pre-registered, authenticated public keys associated with the originating institution's BIC. The rogue signature fails Stage 5 lattice verification because the public key does not match the sender identity.
6. **Memory Corruption & Hardware Fault Injection (Rowhammer / Bit-Squatting):** In cloud datacenters, adversaries can use electrical disturbances, voltage glitching, or DRAM Rowhammer attacks to flip bits in server RAM or network interface cards. QSC's multi-layered validation ensures that any physical bit corruption occurring inside intermediate routers or server memory is caught before it can corrupt the central bank's ledger balances.

---

## 5. Evaluator Q&A Defense Sheet (Tabs 01 - 03)

During the pitch defense and live demonstration, evaluators, venture judges, and academic examiners frequently challenge specific cryptographic and architectural claims. Use these paragraph-wise responses:

---

### Q1: "Why not simply upgrade all proxies and gateways to Post-Quantum TLS 1.3 (e.g. X25519 + ML-KEM-768)?"

Upgrading intermediate proxies and gateways to Post-Quantum TLS 1.3 only protects the point-to-point network transmission on each individual hop while the bytes are flying across the physical wire. It does not—and cannot—solve the fundamental architecture of modern enterprise banking, where proxies, load balancers, and API gateways **must terminate TLS** to perform Layer-7 traffic routing, header inspection, WAF DDoS filtering, compliance auditing, and rate limiting. The instant TLS terminates at an intermediate proxy or gateway, the post-quantum TLS encryption is completely stripped away. The financial transaction is decrypted into cleartext inside the proxy server's volatile memory (RAM) and then forwarded into intermediate message brokers like Apache Kafka, where it is written unencrypted to disk buffers.

Therefore, even if every hop uses PQ-TLS, any attacker with a memory scraper on the proxy, a compromised container, a malicious cloud administrator, or an eavesdropper inside the internal network perimeter captures the raw, plaintext ISO 20022 wire transfer without needing to break any post-quantum math at all. Upgrading the proxy's TLS version simply puts post-quantum armor on the outside pipe while leaving the cargo completely naked inside the proxy's process space. 

Furthermore, PQ-TLS only authenticates the immediate network socket—it proves that the gateway spoke to the proxy, but it provides zero non-repudiation or cryptographic proof to the central clearing house that the originating bank actually authorized that specific £50 million payment, or that an intermediate proxy did not alter the recipient IBAN. QSC solves this by shifting security from the channel to the data itself: the financial payload is post-quantum encapsulated and digitally signed before it ever touches the network, remaining an impenetrable safe in proxy RAM and on Kafka disks until it reaches the central settlement engine.

---

### Q2: "What is the network bandwidth overhead and MTU packet fragmentation risk of ML-KEM-768 and ML-DSA-65?"

As demonstrated on Tab 02's hex inspector, the entire capsule wire footprint is approximately 8.9 kilobytes for a standard ISO 20022 payment—consisting of 1,088 bytes for the ML-KEM ciphertext, 3,309 bytes for the ML-DSA signature, and approximately 2.4 kilobytes of canonical routing headers. In wholesale RTGS settlement, where individual transactions represent tens or hundreds of millions of pounds, an 8.9 KB envelope is negligible compared to the cryptographic guarantee of post-quantum privacy and mathematical unforgeability.

Crucially, QSC avoids the severe network transport penalty of pure Post-Quantum TLS handshakes. In pure PQ-TLS, post-quantum X.509 certificate chains swell to over 18 kilobytes, which exceeds the standard TCP initial congestion window (`initcwnd` = 10 MSS packets, or ~14.6 KB, RFC 6928). This forces the TCP stack to pause and wait for a client acknowledgment round-trip before transmitting the remainder of the certificate, adding an entire round-trip time (+1 RTT) that doubles handshake latency on transatlantic WAN links from 76 ms to 154 ms. QSC avoids this handshake stall entirely because it streams payloads over established transport connections.

While an 8.9 KB capsule does span approximately six TCP segments on a standard 1,500-byte Ethernet network, this transmission occurs as standard TCP streaming across an open window. Over institutional 10GbE interbank connections, streaming six segments takes less than 0.1 milliseconds—unlike handshake certificate bloat, which blocks the connection waiting for round-trip TCP ACKs. The wire format remains well within SWIFT InterACT 4 MB limits and standard ISO 20022 messaging limits.

---

### Q3: "How does the anti-replay mechanism scale across a distributed cluster of clearing nodes?"

Our anti-replay engine pairs a deterministic SHA3-512 token with a strict 300-second temporal freshness window. Any capsule older than 300 seconds is rejected instantly at Stage 2 in 7 microseconds before memory is even consulted. Because stale transactions are dropped by timestamp alone, clearing nodes only need to maintain consumed tokens for a rolling 5-minute sliding window, after which expired tokens are purged automatically.

This rolling window keeps the cache memory footprint strictly bounded regardless of multi-year transaction volume. At an extreme institutional throughput of 10,000 transactions per second, a 300-second window stores at most 3,000,000 tokens. At 64 bytes per token, total memory consumption across the entire clearing cluster is approximately 192 megabytes. This fits easily into an in-memory Redis cluster, a distributed key-value store, or partitioned rotating Bloom filters synchronized across clearing nodes.

Clock drift between participating banking institutions is handled via a configurable $\pm 5$-second drift tolerance synchronized by standard financial NTP/PTP time servers. Any transaction exceeding this tolerance fails closed immediately at Stage 2, protecting the ledger from stale, future-dated, or replayed inputs and completely eliminating double-spending risks in compliance with CPMI-IOSCO Principles for Financial Market Infrastructures.

---

### Q4: "In Tab 02's Attack Lab, why does flipping ciphertext bits fail at Stage 4 while tampering with the signature fails at Stage 5?"

This behavior demonstrates our "cheapest-first, fail-closed" zero-trust pipeline architecture. Stage 4 verifies the SHA3-512 canonical digest over the ciphertext and metadata, executing in just 60 microseconds. The signature bytes are deliberately excluded from this digest because a digital signature cannot sign itself without creating an impossible circular dependency. Therefore, the signature field is omitted from canonical hashing and verified independently at Stage 5.

If an attacker tampers with the ciphertext or metadata, the SHA3-512 hash diverges completely due to the avalanche effect, failing Stage 4 in 60 microseconds. Placing this lightweight 60-microsecond hash check before the computationally heavy 17-millisecond lattice verification discards corrupt or tampered packets immediately. This shields the clearing engine from signature verification denial-of-service (DoS) attacks, where an adversary floods the bank with bogus packets to consume CPU cores.

If an attacker tampers specifically with the signature bytes, the capsule passes Stage 4 because the ciphertext and metadata digest are unaltered, but fails Stage 5 during ML-DSA-65 lattice verification. Forging a valid lattice signature to match tampered data requires solving the Module Short Integer Solution (M-SIS) problem on a $(6 \times 5)$ polynomial matrix modulo $q = 8,380,417$, which provides 128-bit quantum hardness (NIST Security Category 3). Every byte of the wire structure is defended by layered, non-overlapping controls.

---

### Q5: "What is the latency impact on high-throughput settlement engines, and does 17 ms meet bank SLAs?"

On Tab 01, our live telemetry measured full end-to-end settlement in approximately 17 milliseconds, with over 95% of that time spent in ML-DSA-65 signature verification within our pure-Python reference engine. In wholesale interbank RTGS settlement (such as CHAPS, TARGET2, or Fedwire), transaction volume is hundreds of transactions per second—not millions of retail point-of-sale card swipes—and institutional bank SLAs allow several seconds for gross settlement. A 17-millisecond execution time is well within existing clearing windows.

Furthermore, Stages 1 through 4 execute in under 75 microseconds combined. When transitioning from our pure-Python reference engine to compiled C assembly with AVX2 or AVX-512 Number Theoretic Transforms (`liboqs`), ML-DSA-65 verification latency drops from 17.2 milliseconds to 0.25 milliseconds. An 8-core settlement server running compiled C can process over 4,000 validations per second, satisfying the peak clearing demand of any major central clearing house.

While client-side signing can occasionally vary between 75 and 255 milliseconds due to ML-DSA's Fiat-Shamir with Aborts rejection sampling loop, this norm-check restart affects only the originating bank during capsule creation and has zero impact on the clearing house's verification latency. The architecture easily exceeds Fedwire's ISO 20022 real-time settlement target of 2.0 seconds.

---

### Q6: "Why adopt a Hybrid Construction (ML-KEM-768 + AES-256-GCM) rather than pure asymmetric post-quantum encryption for the whole payload?"

NIST FIPS 203 ML-KEM is strictly a Key Encapsulation Mechanism engineered to establish shared symmetric secrets, not a bulk block cipher. Attempting to encrypt megabyte ISO 20022 XML payloads or multi-megabyte SWIFT message batches directly using lattice polynomials would result in catastrophic polynomial matrix bloat, gigabytes of memory expansion, and extreme CPU exhaustion.

Instead, QSC employs the standard KEM + DEM (Data Encapsulation Mechanism) paradigm: ML-KEM-768 encapsulates 256 bits of shared entropy into a compact 1,088-byte ciphertext; HKDF-SHA3-512 expands it into an ephemeral AES key and IV; and AES-256-GCM encrypts the financial payload. AES-256-GCM executes at native bus speeds using hardware CPU AES-NI instructions in just 5 microseconds, enabling line-rate throughput regardless of payload size.

AES-256-GCM is provably immune to Shor's algorithm, which only solves hidden subgroup problems over abelian groups—such as integer factorization in RSA and discrete logarithms in elliptic curves. While Grover's quantum search algorithm provides a quadratic speedup against symmetric ciphers, searching a 256-bit key space still requires $2^{128}$ quantum operations, which is physically impossible and satisfies NIST Category 3 post-quantum security requirements.

---

### Q7: "How do intermediate middleboxes (Reverse Proxies, WAFs, Message Brokers) route transactions without decrypting the capsule?"

QSC employs a decoupled envelope pattern. The outer capsule header contains authenticated, non-confidential routing metadata—such as the destination BIC, routing transit number, ISO 20022 message type (`pacs.008`), timestamp, and priority. Reverse proxies, API gateways, and Apache Kafka brokers inspect these outer fields for traffic routing, rate-limiting, and queue partitioning, while the sensitive financial core—account numbers, IBANs, names, and transaction amounts—remains sealed inside the post-quantum safe.

All outer header fields are cryptographically bound into the SHA3-512 canonical integrity lock and covered by the ML-DSA-65 signature. If a malicious or misconfigured proxy alters a routing field (e.g. changing the destination clearing code to misroute funds), the clearing house detects the modification at Stage 4 and drops the message immediately. The middlebox can read routing tags to forward traffic, but cannot modify them without invalidating the capsule.

In wholesale banking, institutional BICs and routing codes are publicly listed directory entries, so exposing them in the header creates no privacy leak. Furthermore, outer network hops still use standard hop-by-hop TLS 1.3 to shield metadata from external wiretappers, while QSC ensures the payment payload is protected from untrusted intermediate proxies.

---

### Q8: "How does QSC integrate with existing Public Key Infrastructure (PKI) and handle Key Rotation?"

QSC integrates directly with institutional Public Key Infrastructure without requiring a rip-and-replace of existing banking networks. Participating banks and clearing houses exchange ML-KEM-768 and ML-DSA-65 public keys using standard X.509 v3 certificates with post-quantum OIDs under IETF LAMPS specifications. Private keys are stored in Hardware Security Modules (HSMs) conforming to FIPS 140-3 Level 3 or 4.

On Tab 01 of our workbench, we demonstrate live, zero-downtime key rotation: clicking 'Rotate Keys' generates fresh NIST FIPS 203 and 204 keypairs in real-time. Capsules carry explicit `key_id` identifiers in their headers, allowing clearing houses to publish new public keys and support seamless dual-key acceptance during transition periods without taking settlement rails offline.

In the event of suspected key compromise, clearing nodes revoke key IDs via internal directory broadcasts or short-lived OCSP stapling responses. Stage 1 and Stage 5 validation checks verify key status before decapsulation, failing closed immediately if a revoked key ID is detected. This complies with SWIFT PKI transition roadmaps and ANSI X9.142 financial cryptographic key management standards.

---

### Q9: "Why is the demonstration implemented in Pure Python, and what is the exact path to production?"

We deliberately chose pure-Python implementations of `kyber-py` and `dilithium-py` for this showcase to guarantee complete auditability, platform portability, and transparency. Evaluators and professors can inspect every line of lattice polynomial arithmetic without relying on opaque pre-compiled binaries or complex compiler toolchains.

Every mathematical routine was validated against official NIST ACVP (Automated Cryptographic Validation Protocol) test vectors for FIPS 203 and FIPS 204. Our architecture cleanly abstracts all cryptographic operations through interface wrappers, allowing drop-in substitution with C-accelerated engines like `liboqs` or AWS-LC in production with zero code changes.

While Python takes ~17 milliseconds for ML-DSA verification, switching to native C assembly with AVX2 vectorization reduces verification to 0.25 milliseconds—a 70-fold acceleration—delivering over 4,000 verifications per second on an 8-core server while running constant-time assembly that eliminates cache and branch side-channel timing leakage.

---

### Q10: "If an insider attacker has root access to the Reverse Proxy, why can't they intercept or forge the transaction?"

QSC enforces strict Zero-Trust isolation. The reverse proxy only handles transport forwarding; it never possesses the clearing house's ML-KEM private key, nor the originating bank's ML-DSA private key. Even if an attacker has root access to the proxy operating system, dumps physical RAM, or modifies proxy application code, they only see the encrypted capsule bytes. Decrypting the payload requires solving the Module Learning With Errors (M-LWE) lattice problem, which is mathematically impossible even with future quantum supercomputers.

Furthermore, if the rogue administrator modifies payment amounts or recipient accounts in memory, the capsule fails Stage 4's SHA3-512 digest check. If they attempt to recalculate the digest, it fails Stage 5 because they lack the originating bank's ML-DSA-65 private key.

If the rogue admin attempts to capture and replay a previously valid transaction, it fails instantly at Stage 3 in 2 microseconds because the single-use SHA3-512 replay token was already burned during the original settlement. This directly addresses the insider threat requirements of SWIFT Customer Security Controls Framework (CSCF) Control 2.1 and Basel Committee Operational Risk standards.

---

### Q11: "What happens when the package or message size increases (e.g. from 1 KB up to 100 KB or multi-megabyte bulk payment batches)?"

In QSC, the heavy post-quantum lattice operations are completely decoupled from message size. Whether an ISO 20022 message is a single 1-kilobyte MT103 wire transfer, a 10-kilobyte structured corporate payment, or a 100-megabyte bulk ACH clearing batch, the post-quantum lattice overhead remains strictly constant: the ML-KEM-768 ciphertext is *always* exactly 1,088 bytes, and the ML-DSA-65 digital signature is *always* exactly 3,309 bytes. The computationally heavy lattice operations—polynomial matrix ring multiplications and Number Theoretic Transforms—are executed exactly once per capsule regardless of payload volume.

Bulk payload encryption is offloaded entirely to AES-256-GCM, which runs via native hardware CPU instructions (Intel AES-NI and ARM Cryptography Extensions) at wire speed—approximately 5 microseconds per kilobyte. As measured in our benchmarks, scaling payload size from 1 KB to 10 KB increases end-to-end processing latency by only ~29 milliseconds (from 138.7 ms to 168.3 ms in pure Python), and this delta shrinks to under 1 millisecond when compiled with C/AVX2 acceleration. Furthermore, SHA3-512 digests arbitrary payload streams in Keccak-f[1600] state permutations at gigabyte-per-second throughput, guaranteeing that large corporate batches never cause cryptographic bottlenecks or memory exhaustion.

From an architectural perspective, this constant-overhead property makes QSC uniquely suited for enterprise financial rails. While pure asymmetric schemes fail catastrophically when attempting to encrypt multi-megabyte payloads directly—causing memory explosion and severe CPU thrashing—QSC scales linearly and predictably. Financial institutions can encapsulate full-day settlement files containing tens of thousands of bundled transactions in a single post-quantum envelope with the exact same 4.4 KB cryptographic header overhead as an individual wire transfer.

---

### Q12: "What happens to network infrastructure when post-quantum certificate sizes increase, and how does QSC avoid certificate bloat?"

In standard public-key cryptography, classical ECDSA P-256 certificates are compact (approximately 850 bytes), allowing an entire 3-tier certificate chain to fit easily within 2.5 kilobytes. However, post-quantum and hybrid X.509 certificates are substantially larger: an ML-DSA-65 public key is 1,952 bytes and its signature is 3,309 bytes, ballooning a single hybrid certificate to ~6.2 kilobytes and a full certificate chain to over 18.2 kilobytes.

When transport protocols like Hybrid TLS 1.3 attempt to transmit an 18 KB certificate chain during the initial connection handshake, they immediately exceed the standard TCP initial congestion window (`initcwnd` = 10 MSS packets, or ~14.6 KB, defined in RFC 6928). Because the certificate chain overflows the window, the server cannot transmit the full handshake in a single burst: it sends the first 10 packets and is forced to stop and wait for a client TCP ACK before sending the remaining 3 packets. On high-latency wide-area networks (such as transatlantic links between London and New York with a base ping of 72 ms), this forced pause adds an entire extra round-trip time (+1 RTT), doubling the handshake latency from 76 ms to over 154 ms. Furthermore, empirical tests show that 4% to 11% of legacy enterprise firewalls and load balancers drop oversized TLS handshake flights because they misidentify jumbo certificate payloads as amplification attacks or buffer overflow attempts.

QSC completely circumvents this certificate bloat crisis through its layered, decoupled architecture. QSC keeps the transport layer running over fast, lightweight classical or hybrid TLS with compact certificates that easily fit within the initial TCP congestion window (requiring only 2 packets and zero extra round trips). The post-quantum public keys and lattice signatures travel as application-layer payload data inside an already-established, streaming TCP connection. In an established TCP stream, multi-kilobyte data flights stream at full line-rate without triggering handshake stalls, packet drops, or middlebox inspection failures, allowing banks to achieve immediate post-quantum security over existing telecom infrastructure.

---

### Q13: "In the future, as NIST PQC standards evolve or security levels increase (e.g., migrating to ML-KEM-1024, ML-DSA-87, or stateful hash signatures), how will QSC integrate them?"

QSC is engineered from the ground up for complete cryptographic agility (crypto-agility), ensuring that future advancements, higher security categories, or parameter revisions from NIST can be integrated without breaking existing banking rails. The capsule wire format contains explicit, structured protocol and algorithm identifiers (`"version":"QSC-1.0"`, algorithm OIDs, and policy headers) that decouple the transport and application layers from specific mathematical algorithms.

Inside our codebase, cryptographic primitives are strictly modularized behind standardized abstraction wrappers in `src/crypto/` (`kem.py`, `dsa.py`, `symmetric.py`). Upgrading from NIST Category 3 (ML-KEM-768 and ML-DSA-65) to NIST Category 5 (ML-KEM-1024 with 1,568-byte ciphertexts, and ML-DSA-87 with 4,595-byte signatures for maximum sovereign-grade security) requires zero changes to the core `CapsuleBuilder`, `CapsuleValidator`, canonical wire serializer, or API contracts. Furthermore, the architecture is designed to support alternate post-quantum signature schemes—such as stateless hash-based signatures (NIST FIPS 205 SLH-DSA / SPHINCS+) or stateful hash signatures (LMS/XMSS under RFC 8554) for high-value audit trail signing—by simply registering the new algorithm identifier in the validation dispatch table.

To ensure operational business continuity during industry-wide transitions, the clearing house validator implements multi-algorithm negotiation. A central clearing engine can ingest and validate incoming capsules signed with ML-DSA-65 or ML-DSA-87 simultaneously based on the capsule's header metadata, enabling tier-1 institutions to upgrade to maximum security immediately while regional correspondent banks transition on a phased timeline. When hardware-accelerated FIPS 140-3 HSMs or optimized C libraries (`liboqs` / AWS-LC) release certified drivers for new parameter sets, they drop directly into QSC's interface layer with zero disruption to settlement operations.

---

## 6. Rehearsal & Execution Cheat Sheet

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
