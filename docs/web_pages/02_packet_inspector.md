# Tab 02 &mdash; Packet Inspector and Attack Lab Specification

[![NIST PQC](https://img.shields.io/badge/NIST-FIPS%20203%20%7C%20FIPS%20204-green.svg)](https://csrc.nist.gov/projects/post-quantum-cryptography)
[![Tab](https://img.shields.io/badge/Workbench-Tab%2002%20Packet%20Inspector-blue.svg)](https://127.0.0.1:8443)
[![Status](https://img.shields.io/badge/Status-Operational-brightgreen.svg)]()

---

## 1. Overview & Operational Purpose

The **Packet Inspector and Attack Lab** (Tab 02) provides complete byte-level transparency into the Quantum Security Capsule wire format. While high-level graphical summaries can be simulated or approximated, a Wireshark-style interactive hex dump mapped to exact server-side byte offsets proves authenticity.

### Operational Capabilities
1. **Raw Wire Hex Dump:** Inspect the exact UTF-8 byte stream transmitted across the network, partitioned into byte offsets, 16 hexadecimal columns, and ASCII text translations.
2. **Interactive Field Highlighting:** Click any field chip (e.g., `kem_ciphertext`, `signature`, `replay_token`) to highlight and scroll to its exact byte span.
3. **Byte-Level Forensics:** Click any individual byte in the hex matrix to inspect its numeric offset, owning field, hexadecimal value, binary bit pattern, and plain-English role explanation.
4. **Live Single-Bit Tampering Lab:** Flip a single bit (out of ~76,000 bits) in any byte of the wire payload and observe in real time which validation stage catches the corruption.
5. **Verbatim Replay Attack Simulator:** Re-submit an unmodified, previously settled capsule and observe immediate rejection at Stage 3 in ~2 µs.

---

## 2. Interface Layout

```
┌────────────────────────────────────────────────────────┬────────────────────────────────────────┐
│ CAPSULE WIRE FORMAT — RAW BYTES (Left Panel)           │ BYTE SELECTION & ATTACK LAB (Right)    │
├────────────────────────────────────────────────────────┼────────────────────────────────────────┤
│ • Offset (Hex) | 16 Hex Columns | ASCII Representation │ • Byte Selection Inspector             │
│ • Interactive Field Chips Legend:                      │   - Offset: 0x00000092 (146)           │
│   [capsule_id: 38B] [version: 17B] [issued_at: 34B]    │   - Field: kem_ciphertext             │
│   [kem_ciphertext: 1454B] [nonce: 24B]                 │   - Value: 0x5a (01011010) 'Z'         │
│   [payload_ciphertext: 2856B] [payload_tag: 32B]       │   - Role: ML-KEM-768 ciphertext byte   │
│   [integrity_hash: 147B] [signature: 4414B]            ├────────────────────────────────────────┤
│                                                        │ ATTACK LAB — SINGLE BIT FLIP           │
│                                                        │ • Byte Offset: [ 146 ]                 │
│                                                        │ • Bit Index (0-7): [ 2 ]               │
│                                                        │ • [Flip Bit & Resubmit]                │
│                                                        │ • [Replay Capsule Verbatim]            │
│                                                        │ • Attack Diagnostics & Stage Trace     │
└────────────────────────────────────────────────────────┴────────────────────────────────────────┘
```

---

## 3. Left Panel: Wire Format Hex Inspector

### 3.1 Server-Side Canonical Byte Mapping
- **Implementation:** [`src/capsule/wire.py`](../../src/capsule/wire.py) and [`src/frontend/js/hex_inspector.js`](../../src/frontend/js/hex_inspector.js).
- **Endpoint:** `GET /api/v1/capsule/{capsule_id}/hexdump`
- **What it does:** Fetches the serialized canonical wire representation of the capsule loaded from Tab 01.
- **What it shows:** 
  - Left column: Hexadecimal offset (`00000000`, `00000010`, `00000020`, ...).
  - Center columns: 16 hex bytes separated by a mid-row divider for readability.
  - Right column: Printable ASCII characters (`.` for non-printable bytes).
- **Theory behind it:** **True Canonical Serialization.** The wire bytes displayed are the exact bytes hashed by SHA3-512 and signed by ML-DSA-65 &mdash; not a pretty-printed approximation. The transition from readable ASCII JSON keys (`{"capsule_id":"qsc_...`) into base64 ciphertext noise visually demonstrates where encryption takes effect.

---

### 3.2 Interactive Field Legend (Colored Chips)
- **DOM Element:** `<div id="hex-legend">`
- **What it does:** Renders a color-coded chip for every field in the capsule, displaying its field name and exact byte size on the wire.
- **What it shows:**
  - `capsule_id`: ~38 B (Unique UUID v4 tracking token)
  - `version`: ~17 B (`"version":"QSC-1.0"`)
  - `issued_at` / `expires_at`: ~34 B each (ISO-8601 UTC timestamps)
  - `kem_ciphertext`: ~1,454 B (Base64-encoded ML-KEM-768 ciphertext; 1088 bytes raw)
  - `nonce`: ~24 B (Base64-encoded 12-byte AES-GCM IV)
  - `payload_ciphertext`: Variable (~2,800 B for ISO 20022; ~400 B for Card)
  - `payload_tag`: ~32 B (Base64-encoded 16-byte GCM authentication tag)
  - `policy`: ~150 B (Classification, jurisdiction, max hops)
  - `replay_token`: ~147 B (128-char SHA3-512 hex string)
  - `integrity_hash`: ~147 B (128-char canonical SHA3-512 hex digest)
  - `signature`: ~4,414 B (Base64-encoded ML-DSA-65 lattice signature; 3309 bytes raw)
- **Interactive Action:** Clicking any chip highlights the corresponding byte range across the entire hex table, auto-scrolls the view, and pre-populates the Attack Lab offset input.
- **Theory behind it:** **Wire Space Accounting.** Evaluators can visually verify that the largest component by far is the ML-DSA-65 signature (~4.4 KB encoded), demonstrating the honest cryptographic overhead required for post-quantum unforgeability.

---

## 4. Right Panel: Byte Selection & Forensics

### 4.1 Byte Selection Inspector
- **DOM Element:** `<div id="byte-detail">`
- **What it shows:**
  - `Offset`: Decimal and hexadecimal byte position (e.g., `146 (0x0092)`).
  - `Field`: The owning field within the capsule schema.
  - `Value`: Hex byte (`0x5a`), binary representation (`01011010`), and ASCII character.
  - `Description`: Plain-English explanation of the field's security purpose.
- **Theory behind it:** Demystifies the binary structure. Evaluators can pinpoint individual characters in the header, individual bits in the ciphertext, or specific bytes in the lattice signature.

---

## 5. Attack Lab & Adversarial Simulations

### 5.1 Single-Bit Flip Tampering Lab
- **DOM Controls:**
  - `<input id="flip-offset">` (Target byte offset)
  - `<input id="flip-bit">` (Bit index from 0 to 7)
  - `<button id="btn-flip" class="btn btn--danger">` ("Flip Bit & Resubmit")
- **Endpoint:** `POST /api/v1/attack/tamper`
- **What it does:** Flips exactly one bit in the serialized wire bytes ($b' = b \oplus (1 \ll \text{bit})$), re-parses the modified byte sequence, and dispatches it to `/api/v1/capsule/settle`.
- **What it shows:**
  - Mutated byte before and after in hex (e.g., `0x4d` $\rightarrow$ `0x4f`).
  - Affected field name and bit index.
  - Full 5-stage zero-trust validation trace indicating **REJECTED**.

#### Theoretical Behavior Across Fields:
1. **Tampering with `payload_ciphertext`, `kem_ciphertext`, `policy`, or `issued_at`:**
   - **Result:** Caught at **Stage 4 (Integrity Lock)** in ~60 µs.
   - **Theory:** The SHA3-512 integrity lock covers all canonical fields. By the **Avalanche Effect** of the Keccak-f[1600] permutation, flipping a single bit causes ~50% of the 512 digest bits to change randomly, immediately mismatching `integrity_hash`.
2. **Tampering with `signature` bytes:**
   - **Result:** **Passes Stage 4** and is caught at **Stage 5 (Origin Signature)** in ~17 ms.
   - **Theory:** This is a crucial design property. The digital signature signs the integrity hash; it **cannot sign itself** without creating an impossible circular dependency. Therefore, the signature field is excluded from `get_canonical_fields()`. Tampering with the signature leaves the integrity lock intact, but causes the ML-DSA-65 lattice verification equation ($\|\mathbf{z}\|_\infty < \gamma_1 - \beta$ and $\mathbf{A}\mathbf{z} - c\mathbf{t}$) to fail.
   - **Demonstration Value:** Proves to security auditors that Stage 4 and Stage 5 provide orthogonal, non-overlapping coverage with zero security gaps.

---

### 5.2 Verbatim Capsule Replay Attack
- **DOM Control:** `<button id="btn-replay">` ("Replay Capsule Verbatim")
- **Endpoint:** `POST /api/v1/attack/replay`
- **What it does:** Resubmits an authentic, previously settled capsule without modifying a single bit &mdash; mimicking an eavesdropper replaying a captured financial payment.
- **What it shows:**
  - Status: **REJECTED** in red phosphor.
  - Reason: `Replay token already consumed: <token>`.
  - Diagnostics: Stage 1 PASS, Stage 2 PASS, **Stage 3 FAIL**, Stages 4&ndash;5 **SKIPPED**.
  - Execution Time: **~2.1 microseconds**.
- **Theory behind it:** **Stateful Single-Use Token Defense.** Replaying an unmodified capsule bypasses Stage 1 (valid version) and Stage 2 (freshness window is still open). However, the unique `replay_token` was committed to the validator's registry during the initial settlement. Stage 3 catches the duplicate token instantly and terminates execution &mdash; saving ~17 ms of CPU cycles that would otherwise be wasted on redundant lattice signature verification.
