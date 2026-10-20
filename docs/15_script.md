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

During the pitch defense and live demonstration, evaluators, venture judges, and academic examiners frequently ask these technical questions. Use these simplified, spoken-ready responses:

---

### Q1: "Why not simply upgrade all proxies and gateways to Post-Quantum TLS 1.3 (e.g. X25519 + ML-KEM-768)?"

Because upgrading the proxy's TLS connection only protects the wire between two immediate computers—it does not protect the data once it arrives. In modern enterprise banking, intermediate proxies, load balancers, and API gateways *must* terminate TLS so they can inspect HTTP headers, evaluate routing rules, and balance traffic. The instant TLS terminates at the proxy, the post-quantum TLS encryption is completely stripped away. The financial transaction sits unencrypted in the proxy's volatile memory (RAM) and on intermediate message brokers like Apache Kafka.

If an attacker compromises that proxy, dumps server memory, or intercepts internal network traffic, they capture the raw, plaintext ISO 20022 payment without ever needing to break quantum cryptography. QSC solves this by putting post-quantum armor directly on the message itself. Even when the proxy terminates TLS to read routing headers, the financial payload remains locked in an encrypted safe until it reaches the final settlement engine.

---

### Q2: "What is the network bandwidth overhead and MTU packet fragmentation risk of ML-KEM-768 and ML-DSA-65?"

The entire capsule wire size is approximately 8.9 kilobytes for an ISO 20022 credit transfer—about 1.1 KB for the ML-KEM ciphertext, 3.3 KB for the ML-DSA signature, and the rest for routing metadata. In wholesale banking where a single interbank transfer moves millions of pounds, an 8.9 KB envelope is completely negligible.

More importantly, QSC actually *avoids* the network headaches of Pure Post-Quantum TLS handshakes. In pure PQ-TLS, oversized 18 KB certificate chains overflow standard TCP initial congestion windows, forcing an extra round-trip delay that doubles connection times on cross-border links (from 76 ms to 154 ms). With QSC, the transport connection stays fast and lightweight, while the post-quantum payload streams across the open socket in less than a tenth of a millisecond.

---

### Q3: "How does the anti-replay mechanism scale across a distributed cluster of clearing nodes?"

We don't need to store every transaction in memory forever. Every capsule has a strict 5-minute validity window (300 seconds). If an attacker replays a transaction that is older than 5 minutes, Stage 2 rejects it immediately based on timestamp alone—before memory is even checked.

Because of this rolling window, clearing nodes only need to remember tokens used in the last 5 minutes, after which expired tokens are automatically purged from cache. Even under heavy banking volume of 10,000 transactions per second, 5 minutes of tokens takes less than 200 megabytes of RAM. That easily fits in an in-memory Redis cluster shared across all clearing nodes.

---

### Q4: "In Tab 02's Attack Lab, why does flipping ciphertext bits fail at Stage 4 while tampering with the signature fails at Stage 5?"

Our validation pipeline is designed to fail closed using the cheapest checks first. Stage 4 checks the SHA3-512 integrity lock over the payload and headers, which runs in just 60 microseconds. The signature bytes are excluded from this hash because a signature cannot sign itself without an impossible circular loop.

So if an attacker alters the payment or metadata, the hash changes completely and fails at Stage 4 in 60 microseconds—discarding the bad packet instantly without wasting expensive CPU time on signature math. But if an attacker alters the signature bytes, the payload hash still matches, so it passes Stage 4 and gets caught at Stage 5 when post-quantum lattice verification fails. Every byte on the wire is defended by layered, non-overlapping controls.

---

### Q5: "What is the latency impact on high-throughput settlement engines, and does 17 ms meet bank SLAs?"

On Tab 01, full settlement takes approximately 17 milliseconds in our pure-Python reference engine, with 95% of that time spent verifying the ML-DSA-65 lattice signature. In wholesale interbank settlement (like CHAPS or Fedwire), volume is hundreds of transactions per second—not retail millions—and bank SLAs allow several seconds per transfer. Seventeen milliseconds easily satisfies those SLAs.

Furthermore, in production using compiled C and CPU hardware acceleration (AVX2), signature verification drops from 17 milliseconds down to 0.25 milliseconds. That allows a single 8-core settlement server to process over 4,000 transactions per second.

---

### Q6: "Why adopt a Hybrid Construction (ML-KEM-768 + AES-256-GCM) rather than pure asymmetric post-quantum encryption for the whole payload?"

NIST ML-KEM is a Key Encapsulation Mechanism—it is designed to securely agree on a shared secret key, not to bulk-encrypt application data. If you tried to encrypt megabytes of banking data directly with lattice polynomials, message size would explode and memory usage would skyrocket.

Instead, we use ML-KEM-768 to securely exchange a 256-bit key in a compact 1 KB ciphertext, and then use AES-256-GCM to encrypt the payload. AES-256-GCM runs in hardware via CPU instructions in just 5 microseconds. It is completely immune to Shor's algorithm, and Grover's quantum search still requires $2^{128}$ operations to brute-force, providing military-grade post-quantum security at line-rate speed.

---

### Q7: "How do intermediate middleboxes (Reverse Proxies, WAFs, Message Brokers) route transactions without decrypting the capsule?"

We use a decoupled envelope design. The outer header contains normal, non-confidential routing tags—such as the destination bank identifier (BIC), ISO 20022 message type (`pacs.008`), priority, and timestamp. Proxies and Kafka brokers read these outer tags to route and prioritize traffic, while the sensitive payment details—account numbers, names, and amounts—remain locked in the encrypted safe.

Crucially, all routing headers are cryptographically locked into the SHA3-512 digest and covered by the digital signature. A proxy can read where the message needs to go, but if it tries to tamper with any routing tag to misdirect funds, the signature breaks and the clearing house drops the transaction.

---

### Q8: "How does QSC integrate with existing Public Key Infrastructure (PKI) and handle Key Rotation?"

QSC drops directly into standard institutional PKI without replacing existing network rails. Banks exchange post-quantum public keys using standard X.509 certificates with post-quantum identifiers, and store private keys securely inside Hardware Security Modules (HSMs).

On Tab 01, we demonstrate live, zero-downtime key rotation. Clicking 'Rotate Keys' generates fresh NIST keypairs instantly. Each capsule includes a key identifier in its header, allowing clearing houses to accept both old and new keys during rollover periods so settlement never has to stop for key updates.

---

### Q9: "Why is the demonstration implemented in Pure Python, and what is the exact path to production?"

We deliberately used pure Python for this showcase so that professors, judges, and security evaluators can inspect every line of lattice math directly, rather than trusting opaque, pre-compiled C binaries. Every algorithm was tested and validated against official NIST ACVP test vectors.

In our code, all cryptography is cleanly isolated behind standard wrappers. In production, swapping pure Python for compiled C libraries (like `liboqs` or AWS-LC) takes zero architectural changes and speeds up verification by 70 times—dropping latency to 0.25 ms and eliminating side-channel timing risks.

---

### Q10: "If an insider attacker has root access to the Reverse Proxy, why can't they intercept or forge the transaction?"

Because QSC enforces strict Zero Trust: the reverse proxy never holds the private keys. It doesn't have the clearing house's ML-KEM private key to decrypt, nor the originating bank's ML-DSA private key to sign. Even if a rogue admin dumps the proxy's RAM or tampers with the proxy code, they only see ciphertext.

If they try to change the recipient or amount, Stage 4 catches the hash mismatch; if they try to re-sign it, Stage 5 rejects their rogue signature; and if they try to replay the original transaction, Stage 3 rejects it in 2 microseconds because the single-use token was already burned. The insider gets nothing.

---

### Q11: "What happens when the package or message size increases (e.g. from 1 KB up to 100 KB or multi-megabyte bulk payment batches)?"

The heavy post-quantum lattice overhead is completely fixed regardless of file size. The ML-KEM ciphertext is always exactly 1,088 bytes, and the ML-DSA signature is always exactly 3,309 bytes—whether you are sending a 1 KB wire transfer or a 100 MB bulk payment batch.

Bulk encryption is handled by AES-256-GCM, which runs in hardware at line speed (~5 microseconds per kilobyte). Scaling from 1 KB to 10 KB adds only a fraction of a millisecond in compiled environments. This means banks can pack an entire day's worth of transactions into one large batch capsule with the exact same 4.4 KB cryptographic overhead as a single transfer.

---

### Q12: "What happens to network infrastructure when post-quantum certificate sizes increase, and how does QSC avoid certificate bloat?"

Post-quantum X.509 certificate chains swell from 2.5 KB in classical crypto to over 18 KB in hybrid schemes. This breaks standard TCP limits: the initial TCP window only allows ~14.6 KB, so pure post-quantum handshakes are forced to pause and wait for an extra round-trip acknowledgment. On cross-border links (like London to New York), that extra wait doubles connection time from 76 ms to over 154 ms, while some legacy corporate firewalls drop oversized handshakes completely.

QSC avoids this entirely by separating transport from payload security. The transport connection uses lightweight certificates that connect instantly in one round trip. The post-quantum keys and signatures travel inside the payload of the open stream, where multi-kilobyte data flows smoothly at full network speed without stalling handshakes or confusing firewalls.

---

### Q13: "In the future, as NIST PQC standards evolve or security levels increase (e.g., migrating to ML-KEM-1024, ML-DSA-87, or stateful hash signatures), how will QSC integrate them?"

QSC is built for complete crypto-agility. The wire format includes explicit version and algorithm tags (`version: QSC-1.0` and algorithm IDs) that keep application logic completely decoupled from specific mathematical ciphers.

All cryptographic algorithms live in modular wrappers in `src/crypto/`. Upgrading from ML-KEM-768 and ML-DSA-65 to higher-security Level 5 variants (like ML-KEM-1024 or ML-DSA-87), or adding hash-based signatures like SLH-DSA, requires zero changes to the builder, validator, or API contracts. Clearing houses can support multiple algorithms simultaneously, allowing tier-1 banks to upgrade immediately while other institutions transition at their own pace without hard forks.

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
