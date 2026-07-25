# Document 04: Security Analysis & Threat Model

**Barclays Innovation Lab Proposal**  
**Author**: Principal Security Architect, Barclays Innovation Lab  

---

## 11. Security Analysis

### 11.1 Post-Quantum Cryptographic Guarantees
The QSC architecture achieves Indistinguishability under Adaptive Chosen-Ciphertext Attack (**IND-CCA2**) and Strong Unforgeability under Chosen-Message Attack (**SUF-CMA**) in post-quantum environments.

1. **Confidentiality (ML-KEM-768 + AES-256-GCM):**
   - ML-KEM-768 provides **Category 3 security** (~192-bit quantum security level), equivalent to AES-192 against quantum attacks (Shor's and Grover's algorithms).
   - AES-256-GCM symmetric payload encryption requires $2^{128}$ quantum operations to attack using Grover's algorithm, guaranteeing long-term confidentiality against HNDL attacks.

2. **Authenticity & Non-Repudiation (ML-DSA-65):**
   - ML-DSA-65 provides lattice-based digital signatures with **Category 3 security**.
   - Unlike RSA and ECDSA, which are vulnerable to polynomial-time period finding on quantum computers via Shor's algorithm, ML-DSA relies on the hardness of Finding Short Vectors in Module Lattices (Module Learning With Errors / MLWE).

3. **Integrity & Binding (SHA3-512):**
   - SHA3-512 provides 256 bits of collision resistance against quantum Birthday attacks (BHT algorithm) and 512 bits of preimage resistance.
   - All fields (header, timestamps, policy, ciphertexts) are cryptographically bound into the integrity digest. Any modification invalidates the signature.

---

## 12. Threat Model

| Threat Vector | Attack Description | Legacy TLS Mitigation | QSC Architectural Mitigation |
| :--- | :--- | :--- | :--- |
| **Harvest Now, Decrypt Later (HNDL)** | Adversary records encrypted traffic today and decrypts in 5-10 years using a quantum computer. | **FAILED.** RSA/ECDHE key exchanges cracked retroactively. | **IMMUNE.** Payload encrypted with ML-KEM-768 + AES-256-GCM remains secure indefinitely. |
| **Replay Attack** | Adversary intercepts valid wire transfer capsule and re-transmits it to execute duplicate payout. | **PARTIAL.** Protected only during active TLS session. Replay across sessions possible at application/queue level. | **IMMUNE.** SHA3-512 replay token registered in distributed cache; lifetime strictly bounded (e.g. 300s). Re-transmission rejected instantly. |
| **Payload Tampering in Transit** | Adversary alters payment recipient account number or currency amount. | **PARTIAL.** Protected inside TLS pipe, exposed if proxy/middlebox compromised. | **IMMUNE.** AES-256-GCM auth tag + SHA3-512 integrity lock + ML-DSA signature fail instantly if 1 bit changes. |
| **Signature Forgery** | Adversary attempts to forge payment authorization from a corporate executive or client. | **FAILED.** RSA/ECDSA signatures forgeable by quantum computers via Shor's algorithm. | **IMMUNE.** ML-DSA-65 signatures remain unforgeable against quantum adversaries. |
| **Transport Boundary Exposure** | Internal rogue employee captures unencrypted payloads at message queue / API gateway termination point. | **FAILED.** TLS terminates at edge proxy; payload exposed in internal network queues. | **IMMUNE.** Payload remains encapsulated in QSC until reaching destination microservice. |
