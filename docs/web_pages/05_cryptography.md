# Tab 05 &mdash; Cryptographic Parameters and Handshake Telemetry Specification

[![NIST PQC](https://img.shields.io/badge/NIST-FIPS%20203%20%7C%20FIPS%20204-green.svg)](https://csrc.nist.gov/projects/post-quantum-cryptography)
[![TLS 1.3](https://img.shields.io/badge/Transport-RFC%208446%20TLS%201.3-green.svg)](https://datatracker.ietf.org/doc/html/rfc8446)
[![Tab](https://img.shields.io/badge/Workbench-Tab%2005%20Cryptography-blue.svg)](https://127.0.0.1:8443)

---

## 1. Overview & Operational Purpose

The **Cryptography and Telemetry Console** (Tab 05) exposes the underlying mathematical parameters and active cryptographic runtime telemetry of the running settlement node.

Rather than quoting theoretical numbers from research literature, this page queries the active Python runtime and OpenSSL session objects to verify:
1. Exact NIST FIPS 203 and FIPS 204 module-lattice parameter sets in force.
2. Exact byte lengths of all public keys, private keys, ciphertexts, and signatures.
3. Real-time TLS 1.3 handshake telemetry obtained by dialing a live loopback socket probe.
4. Active X.509 server certificate properties (fingerprints, validity, Subject Alternative Names).

---

## 2. Interface Layout

```
┌───────────────────────────────────────────────────┬───────────────────────────────────────────────────┐
│ POST-QUANTUM PARAMETER SETS (Left Panel)          │ LIVE TLS SESSION (Right Panel)                    │
├───────────────────────────────────────────────────┼───────────────────────────────────────────────────┤
│ • ML-KEM-768 (NIST FIPS 203) Parameter Set:       │ • [Re-probe Handshake] Button                     │
│   - Ring: Zq[X]/(X^256 + 1), q = 3329, k = 3      │ • Protocol: TLSv1.3 (RFC 8446)                    │
│   - PubKey: 1,184 B | PrivKey: 2,400 B | CT: 1,088 B│ • Negotiated Cipher: TLS_AES_256_GCM_SHA384       │
│ • ML-DSA-65 (NIST FIPS 204) Parameter Set:        │ • Handshake Duration: ~4.1 ms                     │
│   - Matrix: (k=6, l=5), q = 8380417               │ • OpenSSL Engine: OpenSSL 3.0+ FIPS               │
│   - PubKey: 1,952 B | PrivKey: 4,032 B | Sig: 3,309 B├───────────────────────────────────────────────────┤
│ • Symmetric & KDF Parameter Sets:                 │ ACTIVE SERVER CERTIFICATE (X.509)                 │
│   - AES-256-GCM (NIST SP 800-38D, 96b IV, 128b Tag│ • Common Name (CN): 127.0.0.1                     │
│   - HKDF-SHA3-512 (NIST SP 800-56C Rev. 2)        │ • Issuer: QSC Development Authority               │
│   - SHA3-512 (NIST FIPS 202, Keccak-f[1600])      │ • Validity Window: Valid until 2027 (365 days)    │
│                                                   │ • SHA-256 Fingerprint: b4:12:ef:90:...            │
│                                                   │ • SANs: DNS:localhost, IP:127.0.0.1               │
└───────────────────────────────────────────────────┴───────────────────────────────────────────────────┘
```

---

## 3. Left Panel: Post-Quantum Parameter Sets

- **Endpoint:** `GET /api/v1/pqc/parameters`
- **Controller Implementation:** [`src/server/api.py`](../../src/server/api.py) and [`src/frontend/js/workbench.js`](../../src/frontend/js/workbench.js).
- **What it does:** Returns the official NIST mathematical configuration currently enforced by the server's cryptographic engines.

### 3.1 ML-KEM-768 (NIST FIPS 203)
| Parameter | Value | Mathematical / NIST Significance |
| :--- | :--- | :--- |
| **Algorithm** | `ML-KEM-768` | Module-Lattice Key Encapsulation Mechanism (formerly Crystals-Kyber) |
| **Polynomial Ring** | $\mathcal{R}_q = \mathbb{Z}_q[X]/(X^{256} + 1)$ | Standard cyclotomic polynomial ring with $n=256$ coefficients |
| **Modulus ($q$)** | `3329` | Prime modulus chosen for efficient Number Theoretic Transform (NTT) |
| **Module Rank ($k$)** | `3` | Vector dimension of the matrix $\mathbf{A} \in \mathcal{R}_q^{3 \times 3}$ |
| **Error Distribution ($\eta_1, \eta_2$)** | $(2, 2)$ | Centered binomial distribution parameters for noise polynomials |
| **Quantum Security Level** | **Category 3** | ~192 bits of classical security; equivalent to AES-192 brute force |
| **Public Key Size** | `1,184 bytes` | Transmitted to sender for encapsulation |
| **Private Key Size** | `2,400 bytes` | Retained exclusively by recipient settlement node |
| **Ciphertext Size** | `1,088 bytes` | Fixed-size output produced during Step 2 of capsule construction |
| **Shared Secret Size** | `32 bytes (256 bits)` | High-entropy raw seed passed into HKDF-SHA3-512 |

---

### 3.2 ML-DSA-65 (NIST FIPS 204)
| Parameter | Value | Mathematical / NIST Significance |
| :--- | :--- | :--- |
| **Algorithm** | `ML-DSA-65` | Module-Lattice Digital Signature Algorithm (formerly Crystals-Dilithium) |
| **Modulus ($q$)** | `8,380,417` | Prime modulus satisfying $q \equiv 1 \pmod{2n}$ for NTT multiplication |
| **Matrix Dimensions $(k, \ell)$** | $(6, 5)$ | Matrix dimensions defining the Module-SIS hardness bound |
| **Quantum Security Level** | **Category 3** | Unforgeable under chosen-message attacks (SUF-CMA) |
| **Public Key Size** | `1,952 bytes` | Registered public key of originating client |
| **Private Key Size** | `4,032 bytes` | Originating client signing key |
| **Signature Size** | `3,309 bytes` | Fixed-size output signed over the SHA3-512 canonical digest |

---

### 3.3 Symmetric, KDF, and Integrity Primitives
- **AES-256-GCM (NIST SP 800-38D):** 256-bit symmetric key, 96-bit random initialization vector (`nonce`), 128-bit authentication tag (`payload_tag`).
- **HKDF-SHA3-512 (NIST SP 800-56C Rev. 2):** Extract-and-expand key derivation using the Keccak sponge. Salts derivation with `capsule_id` and binds domain separation string `QSC-1.0/AES-256-GCM`.
- **SHA3-512 (NIST FIPS 202):** Permutation-based hash utilizing the Keccak-f[1600] sponge with capacity $c=1024$ and bitrate $r=576$, yielding a 512-bit digest.

---

## 4. Right Panel: Live TLS Session & Handshake Telemetry

- **Endpoint:** `GET /api/v1/network/tls`
- **Implementation:** [`src/server/tls_config.py`](../../src/server/tls_config.py).
- **What it does:** Performs an active, on-demand loopback connection against the settlement node to measure real transport parameters.

### 4.1 "Re-probe Handshake" Button
- **DOM Element:** `<button id="btn-probe">`
- **What happens when clicked:** The server opens a loopback TCP socket to `127.0.0.1:8443`, wraps the socket with an `SSLContext`, completes a full TLS 1.3 handshake, measures execution duration with a performance counter, extracts session telemetry, and closes the socket.
- **What it shows:**
  - `Protocol`: `TLSv1.3`
  - `Cipher Suite`: `TLS_AES_256_GCM_SHA384`
  - `Handshake Latency`: Microsecond-accurate timing (typically `3.5 ms` to `6.0 ms`)
  - `OpenSSL Engine`: Active runtime library version

---

### 4.2 X.509 Certificate Chain Inspection
The panel displays full cryptographic metadata extracted from the server's active X.509 certificate:
- **Common Name (CN):** `127.0.0.1`
- **Issuer:** `QSC Local Development Authority`
- **Validity Dates:** ISO-8601 validity period (365 days from initial provisioning).
- **Subject Alternative Names (SANs):** `DNS:localhost`, `IP:127.0.0.1`
- **SHA-256 Fingerprint:** Hexadecimal digest verifying certificate authenticity.

---

## 5. Theoretical Summary: The Trust Boundary

Tab 05 visually embodies the boundary between **transport security** and **message security**:
- The **Right Panel (TLS 1.3)** proves that the transport connection is genuine, encrypted, and compliant with modern networking standards.
- The **Left Panel (PQC Parameters)** proves that even if an adversary records the Right Panel's TLS session today and cracks it in 2035 using Shor's algorithm, the Left Panel's lattice mathematics protect the underlying financial transaction permanently.
