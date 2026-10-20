# 16 — 1-Minute 3-Slide Pitch Script

```

> "Financial wire transfers like ISO 20022 and SWIFT carry thirty-year liabilities. Today, adversaries harvest encrypted traffic to decrypt later with Shor's algorithm, while intermediate network proxies terminate TLS and expose that financial data in cleartext memory."

*(Transition smoothly: "To solve this without replacing the network...")*



> "We built the Quantum Security Capsule to provide message-centric post-quantum armor. We encapsulate payloads with NIST ML-KEM-768, sign with ML-DSA-65, and encrypt with AES-256-GCM—turning every transaction into a tamper-evident digital safe that traverses untrusted intermediaries completely sealed."

*(Transition smoothly: "Looking at our empirical benchmarks...")*



> "Benchmarking across one hundred runs shows our hybrid model adds modest overhead—an 89-millisecond handshake and ~138-millisecond end-to-end latency compared to classical TLS. In high-value wholesale settlement where transactions represent millions, this overhead is negligible. Crucially, QSC delivers mathematically proven post-quantum protection today across legacy middleboxes, with a clear path to sub-millisecond speeds via hardware acceleration."


---

## 3. Slide Visual Anchors & Speaker Cue Sheet

Use these quick visual references so your eyes and gestures align with the slides:

### Slide 1: The Problem (`01 / WHY`)
- **Visual Cue:** Bottom network diagram showing the attacker and quantum computer.
- **Gesture:** Point to the red **"RISK: Harvest Now, Decrypt Later"** box and the middle **"Network (Proxies, ISPs)"** cloud.
- **Mental Anchor:** 30-year liability + cleartext memory exposure at proxies.

### Slide 2: Our Solution (`02 / WHAT`)
- **Visual Cue:** Architecture flow showing `Forward Proxy / Interception Layer` in yellow.
- **Gesture:** Point to the proxy box text: *"Forwards encrypted QSC capsule without accessing plaintext"*.
- **Mental Anchor:** Message-level safe; no need to re-explain crypto pipeline (saved for Tab 01 live demo).

### Slide 3: Benchmarking & Performance (`03 / VALUE`)
- **Visual Cue:** Performance Comparison Table and right-hand **"Key Insights"** card.
- **Gesture:** Glance at row 1 (`Handshake: 89.1 ms`) and row 5 (`End-to-End Latency: 138.7 ms`), then gesture toward the **"Acceptable Performance"** and **"Hybrid Approach"** insights on the right.
- **Mental Anchor:** ~89 ms / ~138 ms is completely acceptable for wholesale settlement, dropping to sub-millisecond with hardware acceleration.

---

*Companion document to [15_script.md](15_script.md) (Live Pitch & Demonstration Script).*
