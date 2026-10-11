# Tab 03 &mdash; Interactive 3D Visualizer Specification

[![Three.js](https://img.shields.io/badge/Three.js-WebGL%203D-black.svg)](https://threejs.org)
[![NIST PQC](https://img.shields.io/badge/NIST-FIPS%20203%20%7C%20FIPS%20204-green.svg)](https://csrc.nist.gov/projects/post-quantum-cryptography)
[![Tab](https://img.shields.io/badge/Workbench-Tab%2003%203D%20Visualizer-blue.svg)](https://127.0.0.1:8443)

---

## 1. Overview & Operational Purpose

The **Interactive 3D Visualizer** (Tab 03) is a WebGL simulation engineered in Three.js ([`src/frontend/js/visualizer_3d.js`](../../src/frontend/js/visualizer_3d.js)). Its primary role is to communicate the core architectural thesis of the project &mdash; **Channel Security vs. Message-Centric Security** &mdash; to non-cryptographers, enterprise architects, and executive evaluators who need to see *why* TLS 1.3 fails under "Harvest Now, Decrypt Later" and how QSC solves it.

### What the 3D Scene Represents
The 3D environment models a realistic multi-hop banking route connecting an Originating Bank to a Core Clearing House across intermediary network hops, monitored by an airborne adversary:

```
[ NODE 1: Originating Bank ]
             │
             ▼ (Transit Hop 1: External Network)
[ NODE 2: Edge CDN / WAF Gateway ]
             │
             ▼ (Transit Hop 2: Ingress Boundary)
[ NODE 3: Reverse Proxy / API Gateway ]  ◄── [TLS TERMINATES HERE]
             │
             ▼ (Transit Hop 3: Internal Bus)
[ NODE 4: Apache Kafka Message Broker ]  ◄── [DATA AT REST ON DISK]
             │
             ▼ (Transit Hop 4: Core Interconnect)
[ NODE 5: Core Settlement Clearing House ]

       ▲ (High Orbit)
[ THE ADVERSARY: Quantum Surveillance Drone / HNDL Archive ]
```

---

## 2. Interactive Viewport & Scene HUDs

### 2.1 Viewport Camera Navigation
- **Orbit Navigation:** Left-click and drag anywhere on the canvas to rotate the camera around the 3D nodal grid.
- **Zoom:** Mouse scroll wheel to zoom smoothly in and out.
- **Pan:** Right-click and drag to translate the viewpoint horizontally and vertically.
- **Auto-Framing:** Triggering process runs automatically animates the camera to track in-flight payloads across network nodes.

---

### 2.2 Heads-Up Displays (HUDs)

#### Scene Status HUD (Top Left)
- **DOM Elements:** `#hud-mode`, `#hud-phase`, `#hud-payload`
- **What it shows:** Active protection mode (`TLS 1.3 Transport` vs. `QSC Capsule`), current step phase (`idle`, `Key Generation`, `Transit`, `Settled`), and payload protection state (`plaintext in tunnel` vs. `sealed lattice crystal`).

#### Module-Lattice Parameter HUD (Top Right)
- **What it shows:** Live NIST FIPS 203 parameters for ML-KEM-768:
  - **Ring:** $\mathcal{R}_q = \mathbb{Z}_q[X]/(X^{256} + 1)$
  - **Modulus $q$:** `3329`
  - **Module Rank $k$:** `3`
  - **Shared Secret:** `256 bit`

| Line in HUD | Plain-English Meaning | Why It Is Chosen by NIST |
| :--- | :--- | :--- |
| **Ring $\mathbb{Z}_q[X]/(X^{256}+1)$** | **The Math Playground:** Instead of multiplying huge single numbers (like RSA), math is done on polynomials with 256 terms. When powers reach $X^{256}$, they wrap around ($X^{256} = -1$) like hands on a clock. | Keeps all keys and calculations strictly bounded to a compact, predictable memory size. |
| **Modulus $q = 3329$** | **The Number Clock:** All numbers and coefficients wrap around when they hit `3329` (numbers always stay integers between `0` and `3328`). | `3329` is a prime number specifically chosen because it enables Number Theoretic Transform (NTT), running polynomial math in microseconds. |
| **Module Rank $k = 3$** | **The Security Level (Dimensions):** Polynomials are bundled into a $3 \times 3$ grid. $k=2$ is ML-KEM-512, **$k=3$ is ML-KEM-768**, and $k=4$ is ML-KEM-1024. | Provides NIST Security Category 3 (equivalent to AES-192), giving optimal quantum hardness with minimal bandwidth overhead. |
| **Shared Secret: 256 bit** | **The Encryption Prize:** The final 32-byte (256-bit) secret key derived safely by both parties through the lattice exchange. | Fed directly into HKDF-SHA3-512 to generate the AES-256-GCM symmetric key that encrypts the financial payload. |


#### Status Banner (Bottom Left)
- **DOM Element:** `#hud-status-text`
- **What it shows:** Single-line plain-language summary of what is happening in the current simulation frame.

---

## 3. Dual-Mode Comparison Engine

Operators can toggle between two operational paradigms using the mode buttons:

| Control | Mode A &mdash; Legacy TLS 1.3 Transport | Mode B &mdash; Quantum Security Capsule (QSC) |
| :--- | :--- | :--- |
| **DOM Trigger** | `<button id="btn-mode-tls">` | `<button id="btn-mode-qsc">` |
| **Visual Geometry** | Translucent glowing cylindrical conduit connecting hops. Payload is a raw glowing amber orb. | Payload encased inside a multi-faceted 3D emerald crystalline lattice safe. Conduit is non-load-bearing. |
| **Security Scope** | Secures the transient network socket pipe between nodes. | Secures the financial data payload itself end-to-end. |
| **At Proxies (Node 3)**| **Tunnel collapses.** Payload appears as glowing red cleartext in proxy process memory. | Tunnel terminates, but **capsule remains impenetrable**. Proxy forwards without reading. |
| **At Broker (Node 4)** | Payload sits unencrypted on disk in Kafka topic partitions. | Capsule remains sealed in broker topic storage (encryption at rest). |

---

## 4. "Run Full Process" Demonstration Cycle

Clicking `<button id="btn-run">` executes a 22-second choreographed sequence advancing through five distinct operational phases, narrated in real time in the right-hand **Narration Log** (`#viz-log`):

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ 1. KEY GENERATION                                                           │
│ Mode A: Generates ECDHE P-256 keys (vulnerable to discrete log period-finding)│
│ Mode B: Generates ML-KEM-768 (1184B pub) & ML-DSA-65 (1952B pub) lattice keys│
├─────────────────────────────────────────────────────────────────────────────┤
│ 2. ENCAPSULATION                                                            │
│ Mode A: Serialises ISO 20022 wire as plaintext JSON (zero message defense)   │
│ Mode B: 8-step pipeline seals payload in AES-GCM + ML-KEM + ML-DSA armor    │
├─────────────────────────────────────────────────────────────────────────────┤
│ 3. WIRE TRANSIT                                                             │
│ Payload travels across the external network conduit to the Edge Gateway.    │
├─────────────────────────────────────────────────────────────────────────────┤
│ 4. PROXY HOP (THE CRITICAL MOMENT)                                          │
│ Mode A: TLS terminates. Payload turns bright red (cleartext in proxy memory)│
│ Mode B: TLS terminates. Capsule stays sealed green (zero memory exposure)   │
├─────────────────────────────────────────────────────────────────────────────┤
│ 5. SETTLEMENT                                                               │
│ Mode A: Engine accepts wire blindly because TLS delivered it.                │
│ Mode B: Engine executes 5-stage zero-trust gate, decapsulates, and settles. │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 5. "Run Quantum Attack" (HNDL Simulation)

Clicking `<button id="btn-attack">` simulates the Harvest Now, Decrypt Later attack lifecycle across four distinct visual phases:

### Phase 1: The Harvest (Present Day)
- **Visual:** Red duplicated data packets peel off the wire during transit and fly up into the eavesdropper drone.
- **Theory:** Passive eavesdropping. The adversary does not tamper with traffic or alert security monitoring; they silently archive raw encrypted TLS sessions to mass storage.

### Phase 2: The Archive Waits (Timeline Interlude)
- **Visual:** Scene holds while the camera pans across the archived packets.
- **Theory:** Years pass (2026 $\rightarrow$ 2035). Hostile actors warehouse the encrypted financial data, waiting for quantum hardware to achieve fault tolerance.

### Phase 3: Shor's Algorithm (The Quantum Era)
- **Visual:** A vibrant quantum wave shockwave expands from the eavesdropper. Energy beams target the captured tunnels. **Every TLS conduit segment collapses and vanishes from the scene.**
- **Theory:** Shor's algorithm calculates discrete logarithms in polynomial time, recovering the archived ECDHE session keys. The outer TLS tunnel is completely stripped away.

### Phase 4: The Outcome Divergence
- **In Mode A (Legacy TLS):**
  - **Visual:** The payload orb turns bright red and pulses. The narration declares:  
    `"BREACH CONFIRMED: Shor's algorithm recovered the session key. Adversary reads cleartext ISO 20022 wire (Account Numbers, BICs, £50,000,000 wire details exposed)."`
- **In Mode B (QSC Defense):**
  - **Visual:** The outer TLS tunnel collapses identically, but the **emerald crystalline lattice capsule holds firm**. Attack beams deflect harmlessly off the lattice faces. The narration declares:  
    `"ATTACK DEFLECTED: Tunnel collapsed, but inner QSC capsule resists Shor's algorithm. Module-LWE lattice structure yields 0 data leakage. The payment remains sealed."`

---

## 6. Scrubbable Timeline & Narration

### 6.1 Step Timeline Scrubber
- **DOM Element:** `<div id="timeline">`
- **Steps:** `1. Key Generation`, `2. Encapsulation`, `3. Wire Transit`, `4. Proxy Hop`, `5. Settlement`.
- **Interactive Action:** Operators can click any step to jump immediately to that point in the simulation &mdash; enabling presenters to replay the proxy hop or settlement stage on demand.

### 6.2 Synchronized Narration Stream
- **DOM Element:** `<div id="viz-log">`
- **What it does:** Displays an automated play-by-play narrative with timestamps, cryptographic parameters, and plain-English explanations.
- **Clear Button (`#btn-clear-viz-log`):** Empties the narration log for fresh demonstration runs.

---

## 7. Plain-English Presenter Cheatsheet (Easy Read-Aloud Script)

> **Presenter Tip:** Use this section during your live demonstration or showcase. You can read or reference these simple step-by-step explanations directly while clicking the buttons on the screen.

---

### Part 1: ONLY TLS (Mode A &mdash; Standard Flow)

#### Step 1: Key Generation 🔑
Both systems create the same secret key to communicate securely. The server proves its identity using a digital certificate. A powerful future quantum computer could potentially break this cryptography.

#### Step 2: Serialisation 📦
The payment is converted into readable JSON containing account numbers and the amount. There is no additional protection on the payment itself.

#### Step 3: Wire Transit 🌐
The payment travels through the internet in encrypted form. Outsiders cannot easily read it while it is travelling.

#### Step 4: Reverse Proxy ⚠️
**This is the most important step.** The proxy decrypts the payment to inspect and forward it. Now the payment is readable in the server's memory. If an attacker compromises the proxy, they could access the payment.

#### Step 5: Message Broker 💾
The broker stores the payment for processing and recovery. In this simulation, it saves the payment as plaintext, meaning someone with access to the stored data could read it.

#### Step 6: Settlement 🏦
The final system receives the payment but does not independently verify its authenticity or integrity. If an intermediary altered the payment, the system might not detect the change.

> **What's the main problem?**  
> TLS protects data while travelling, but doesn't automatically protect it at every system that processes it.  
> A quantum attack threatens the cryptography. The proxy and broker weaknesses exist even without quantum computers.

---

### Part 2: Quantum Attack OVER TLS (Mode A &mdash; Attack Flow)

#### 1. Harvest 📥
An attacker secretly records all encrypted payment data travelling over the network. They cannot read it now, but they save it for later.

#### 2. Wait for the Future ⏳
The attacker stores the data for years, waiting for powerful quantum computers to become available. This is called **“Harvest Now, Decrypt Later.”**

#### 3. Shor’s Algorithm ⚛️
A sufficiently powerful quantum computer uses Shor’s algorithm to break the elliptic-curve cryptography used in the recorded TLS handshakes and potentially recover the session keys.

#### 4. Total Compromise 💥
If the attack succeeds, the attacker can decrypt the recorded traffic and read sensitive payment details, such as account numbers and transaction amounts.

> **Main Takeaway:**  
> Data encrypted today could be stolen now and decrypted in the future. This is why systems handling highly confidential, long-term data need protection against future quantum attacks.  
> *(Note: This attack requires a sufficiently capable quantum computer; it is not something today's ordinary computers can do.)*

---

### Part 3: QSC Capsule (Mode B &mdash; Standard Flow)

#### Step 1: Key Generation 🔑
The bank and clearing house create special post-quantum cryptographic keys. Their private keys stay secret, helping protect against future quantum attacks.

#### Step 2: Encapsulation 🔒
The payment is encrypted and digitally signed before being sent. Its contents cannot be read without the correct key, and the signature helps detect tampering.

#### Step 3: Wire Transit 🌐
The encrypted payment travels through the network. Even if TLS is broken, the payment itself remains encrypted.

#### Step 4: Reverse Proxy 🛡️
The proxy decrypts the TLS connection but sees only the sealed payment capsule. It can forward the payment but cannot read the amount or account numbers.

#### Step 5: Message Broker 💾
The broker saves the encrypted capsule to disk instead of storing readable payment details.

#### Step 6: Settlement 🏦
The receiving system checks the protocol version, expiry, replay protection, message integrity, and digital signature. Only after these checks pass does it decrypt the payment.

> **Main Takeaway:**  
> Unlike the TLS-only mode, QSC Capsule protects the payment itself, even when it passes through untrusted systems.  
> *Now run the quantum attack: The attacker may capture the traffic, but breaking the TLS tunnel alone won't reveal the payment because the message has its own post-quantum encryption.*

---

### Part 4: Quantum Attack on QSC Capsule &mdash; Simple Explanation

#### 1. Harvest 📥
The attacker records all encrypted network traffic and saves it. They cannot read the payment yet.

#### 2. Wait for the Future ⏳
The attacker waits until a powerful quantum computer becomes available. This is called **“Harvest Now, Decrypt Later.”**

#### 3. Shor’s Algorithm ⚛️
The quantum computer breaks the TLS elliptic-curve cryptography and potentially recovers the session keys. The outer security tunnel is compromised.

#### 4. Attack Deflected 🛡️
The attacker discovers that the payment is still inside an encrypted capsule.  
To open it, they would need to break **ML-KEM-768**, a post-quantum encryption algorithm based on a mathematical problem called **Module Learning With Errors (M-LWE)**.  
Shor’s algorithm does **not** directly solve this problem. The payment remains protected, assuming the implementation and keys are secure.

> **Main Takeaway:**  
> TLS gets broken, but the payment stays encrypted. QSC Capsule adds another layer of protection, designed to withstand known quantum attacks, even if the outer TLS connection is compromised.

---

### Part 5: Explaining the "LATTICE PARAMETERS" Box (When Asked by Judges)

When evaluating committees or judges point to the top-right box on the 3D screen:

```
LATTICE PARAMETERS
Ring Z_q[X]/(X^256+1)
Modulus q 3329
Module rank k 3
Shared secret 256 bit
```

**Here is what to say in simple English:**

1. **"What is this box?"**  
   *"This box displays the official NIST FIPS 203 parameters for our post-quantum algorithm, ML-KEM-768. It proves that our 3D visualizer is backed by real mathematical equations, not random mock numbers."*

2. **Ring $\mathbb{Z}_q[X]/(X^{256}+1)$ (The Math Playground):**  
   *"In classical crypto like RSA, math is done on huge single numbers. In post-quantum lattice cryptography, we do math on polynomials (equations with powers of $X$). The $X^{256}+1$ part means every polynomial has exactly 256 coefficients. Whenever powers reach 256, they wrap back around like a clock, keeping memory usage ultra-small and fast."*

3. **Modulus $q = 3329$ (The Number Clock):**  
   *"Just like an ordinary clock resets after 12, all numbers in ML-KEM wrap around when they reach 3329. NIST specifically chose 3329 because it's a prime number that allows computers to use the Number Theoretic Transform (NTT), which calculates multiplication in microseconds."*

4. **Module rank $k = 3$ (The Security Dimension):**  
   *"This is the security level knob. It means our polynomials are grouped into a $3 \times 3$ grid. $k=2$ is ML-KEM-512, $k=3$ is ML-KEM-768 (AES-192 equivalent), and $k=4$ is ML-KEM-1024. Rank 3 is NIST's recommended sweet spot for enterprise banking."*

5. **Shared secret 256 bit (The Encryption Key):**  
   *"This is the final 32-byte secret key agreed upon by both sides through the lattice exchange. Once both banks agree on this 256-bit secret, they feed it into AES-256-GCM to seal the financial transaction."*


