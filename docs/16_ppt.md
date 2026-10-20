# 16 — 1-Minute 3-Slide Pitch Script

[![Target Duration](https://img.shields.io/badge/Duration-1%3A00%20(60s)-blue.svg)]()
[![Pacing](https://img.shields.io/badge/Pacing-~130%20WPM-brightgreen.svg)]()
[![Word Count](https://img.shields.io/badge/Word%20Count-~130%20Words-orange.svg)]()
[![Slides](https://img.shields.io/badge/Slides-3%20Slides-purple.svg)]()

> **Executive Context:**  
> This script is calibrated for a **strict 60-second executive presentation** covering the 3 core pitch slides before transitioning to the live workbench demonstration ([15_script.md](15_script.md)):
> - **Slide 1 (01 / WHY — The Problem):** ~15 seconds — Fast setup on Harvest Now, Decrypt Later and middlebox cleartext exposure.
> - **Slide 2 (02 / WHAT — Our Solution):** ~17 seconds — High-level message-centric concept (ML-KEM + ML-DSA + AES-GCM) without redundant deep-dive.
> - **Slide 3 (03 / VALUE — Benchmarking & Evaluation):** ~28 seconds — Concrete benchmark numbers (handshake, latency, throughput) proving institutional feasibility.

---

## 1. Quick Reference: 60-Second Timing Matrix

| Slide | Visual / Title | Duration | Elapsed | Key Focus | What to Highlight on Screen |
| :--- | :--- | :---: | :---: | :--- | :--- |
| **Slide 1** | `01 / WHY`<br>**The Problem** | **15s** | 00:00 - 00:15 | HNDL + Proxy TLS Termination | Red banner: *"Harvest Now, Decrypt Later"* & attacker recording network traffic. |
| **Slide 2** | `02 / WHAT`<br>**Our Solution** | **17s** | 00:15 - 00:32 | Message-Level Armoring | Center proxy node: forwards encrypted capsule without accessing plaintext. |
| **Slide 3** | `03 / VALUE`<br>**Benchmarking** | **28s** | 00:32 - 01:00 | Empirical Feasibility & Overhead | Benchmark table: 89 ms handshake, 138 ms latency; Key insights box on the right. |

---

## 2. Word-for-Word 1-Minute Pitch Script

```
========================================================================================
SLIDE 1 | 01 / WHY: The Problem
TARGET TIME: 00:00 - 00:15 (15 Seconds | Word Count: ~33 words)
========================================================================================
```

> "Financial wire transfers like ISO 20022 and SWIFT carry thirty-year liabilities. Today, adversaries harvest encrypted traffic to decrypt later with Shor's algorithm, while intermediate network proxies terminate TLS and expose that financial data in cleartext memory."

*(Transition smoothly: "To solve this without replacing the network...")*

```
========================================================================================
SLIDE 2 | 02 / WHAT: Our Solution — Quantum Security Capsule
TARGET TIME: 00:15 - 00:32 (17 Seconds | Word Count: ~37 words)
========================================================================================
```

> "We built the Quantum Security Capsule to provide message-centric post-quantum armor. We encapsulate payloads with NIST ML-KEM-768, sign with ML-DSA-65, and encrypt with AES-256-GCM—turning every transaction into a tamper-evident digital safe that traverses untrusted intermediaries completely sealed."

*(Transition smoothly: "Looking at our empirical benchmarks...")*

```
========================================================================================
SLIDE 3 | 03 / VALUE: Benchmarking & Performance Evaluation
TARGET TIME: 00:32 - 01:00 (28 Seconds | Word Count: ~60 words)
========================================================================================
```

> "Benchmarking across one hundred runs shows our hybrid model adds modest overhead—an 89-millisecond handshake and ~138-millisecond end-to-end latency compared to classical TLS. In high-value wholesale settlement where transactions represent millions, this overhead is negligible. Crucially, QSC delivers mathematically proven post-quantum protection today across legacy middleboxes, with a clear path to sub-millisecond speeds via hardware acceleration."

```
========================================================================================
TOTAL DURATION: EXACTLY 60 SECONDS (1:00)
TOTAL SPOKEN WORDS: ~130 WORDS (IDEAL SPEAKING PACE: 130 WPM)
HANDOFF: "Now let's see this in action on our live institutional workbench..." -> (Launch Tab 01)
========================================================================================
```

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
