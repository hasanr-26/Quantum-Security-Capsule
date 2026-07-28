# Document 04

---

## 1. Post-Quantum Cryptographic Guarantees

The Quantum Security Capsule (QSC) architecture provides Indistinguishability under Adaptive Chosen-Ciphertext Attack (**IND-CCA2**) and Strong Unforgeability under Chosen-Message Attack (**SUF-CMA**) in post-quantum environments.

---

## 2. Mathematical Foundations of the Cryptographic Stack

### 2.1 Key Encapsulation: ML-KEM-768 (NIST FIPS 203)
- **Mathematical Basis:** Module Learning With Errors (M-LWE) over polynomial rings $\mathcal{R}_q = \mathbb{Z}_q[X]/(X^n + 1)$ with degree $n=256$ and modulus $q=3329$.
- **Hardness Assumption:** Finding a secret vector $s$ given $A \cdot s + e = b \pmod q$, where $A$ is a uniformly random matrix, $s$ is the secret vector, and $e$ is a small error polynomial.
- **Quantum Security Level:** **Category 3 security** (~192-bit quantum security level), equivalent to AES-192 against quantum search algorithms.
- **Implementation:** [`src/crypto/kem.py`](file:///c:/Users/hasan/antigravity/QSC/src/crypto/kem.py)

---

### 2.2 Digital Signatures: ML-DSA-65 (NIST FIPS 204)
- **Mathematical Basis:** Module Learning With Errors (M-LWE) and Module Short Integer Solution (M-SIS).
- **Hardness Assumption:** Finding short non-zero vectors $z$ such that $A \cdot z = 0 \pmod q$.
- **Quantum Security Level:** **Category 3 security** (~192-bit quantum security level). Unlike RSA and ECDSA, which are vulnerable to polynomial-time period finding on quantum computers via Shor's algorithm, ML-DSA lattice signatures remain unforgeable.
- **Implementation:** [`src/crypto/dsa.py`](file:///c:/Users/hasan/antigravity/QSC/src/crypto/dsa.py)

---

### 2.3 Symmetric Payload Encryption: AES-256-GCM (NIST SP 800-38D)
- **Mathematical Basis:** Galois Counter Mode over the finite field $GF(2^{128})$.
- **Quantum Hardness:** AES-256 requires $2^{128}$ quantum operations to break using Grover's quantum search algorithm, guaranteeing long-term confidentiality against HNDL attacks.
- **AEAD Binding:** Associated Data binds the unique `capsule_id` into the GCM tag computation, preventing ciphertext detachment or substitution.
- **Implementation:** [`src/crypto/symmetric.py`](file:///c:/Users/hasan/antigravity/QSC/src/crypto/symmetric.py)

---

### 2.4 Integrity Locking & Replay Binding: SHA3-512 (NIST FIPS 202)
- **Mathematical Basis:** Keccak-f[1600] permutation using a sponge construction.
- **Quantum Hardness:** Provides 256 bits of collision resistance against quantum Birthday attacks (BHT algorithm) and 512 bits of preimage resistance.
- **Canonical Binding:** All header fields, timestamps, recipient IDs, nonces, and ciphertexts are canonicalized into a deterministic JSON object and hashed into a 512-bit digest.
- **Implementation:** [`src/crypto/hashing.py`](file:///c:/Users/hasan/antigravity/QSC/src/crypto/hashing.py)

---

## 3. Comprehensive Threat Model & Mitigation Matrix

| Threat Vector | Attack Description | Legacy TLS 1.3 Mitigation | QSC Architectural Defense ([`src/capsule`](file:///c:/Users/hasan/antigravity/QSC/src/capsule)) |
| :--- | :--- | :--- | :--- |
| **Harvest Now, Decrypt Later (HNDL)** | Adversary records encrypted traffic today and decrypts in 5-10 years using a CRQC. | **FAILED.** RSA/ECDHE session keys cracked retroactively by Shor's Algorithm. | **IMMUNE.** Payload encrypted with ML-KEM-768 + AES-256-GCM remains secure indefinitely. |
| **Replay Attack** | Adversary intercepts valid payload capsule and re-transmits it to execute duplicate payout. | **PARTIAL.** Protected only during active TLS socket. Replay possible across sessions at application/queue level. | **IMMUNE.** [`validator.py`](file:///c:/Users/hasan/antigravity/QSC/src/capsule/validator.py) checks SHA3-512 `replay_token` in distributed registry within TTL window (300s). Re-transmission rejected instantly. |
| **Payload Tampering in Transit** | Adversary alters payment amount, recipient account number, or ciphertext bits. | **PARTIAL.** Protected inside TLS pipe; exposed if edge proxy/middlebox is compromised. | **IMMUNE.** AES-256-GCM auth tag + SHA3-512 integrity lock + ML-DSA signature fail instantly if 1 bit changes. |
| **Rogue Key / Signature Forgery** | Adversary attempts to forge payment authorization from a corporate client or executive. | **FAILED.** RSA/ECDSA signatures forgeable by quantum computers via Shor's algorithm. | **IMMUNE.** ML-DSA-65 lattice signatures are unforgeable against quantum adversaries. Verification requires registered sender public key. |
| **Expired Timestamp Re-play** | Adversary holds a captured capsule and transmits it hours or days later. | **FAILED.** TLS socket does not validate message-level application expiration timestamps. | **IMMUNE.** [`timestamp.py`](file:///c:/Users/hasan/antigravity/QSC/src/utils/timestamp.py) enforces wall-clock window (`current_time <= expires_at`). Expired capsules are rejected at Gate 2. |
| **Transport Boundary Exposure** | Internal insider captures unencrypted payloads at message queue or API gateway termination. | **FAILED.** TLS terminates at edge proxy; payload exposed in internal plaintext queues/brokers. | **IMMUNE.** Payload remains encapsulated inside QSC until reaching destination microservice receiver. |
