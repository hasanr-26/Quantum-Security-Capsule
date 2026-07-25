# Document 07: Comparison with Hybrid TLS & Future Roadmap

**Barclays Innovation Lab Proposal**  
**Author**: Principal Security Architect, Barclays Innovation Lab  

---

## 19. Comprehensive Comparison: Hybrid TLS vs. Quantum Security Capsule (QSC)

| Feature / Dimension | Hybrid TLS 1.3 (NIST PQC + Classical TLS) | Quantum Security Capsule (QSC) Architecture |
| :--- | :--- | :--- |
| **Security Philosophy** | Secures the transport channel pipe | Secures every individual message payload |
| **Protection Scope** | Ephemeral while packet travels through pipe | End-to-end payload protection across rest, motion, & queue storage |
| **Middlebox Exposure** | Payload decrypted at WAF / API Gateway proxies | Payload remains 100% encrypted through middleboxes |
| **Harvest Now Decrypt Later Defense** | Effective *only* if connection established via PQC TLS | Effective permanently regardless of transport mechanism |
| **Replay Defense** | Handled per session socket | Cryptographically bound per capsule via SHA3-512 & lifetime window |
| **Transport Protocol Dependence** | Strictly tied to TCP/TLS socket session | Completely transport-agnostic (HTTPS, Kafka, MQ, SWIFT, File) |
| **Non-Repudiation** | Endpoint identity authenticated | Individual message non-repudiation via per-capsule ML-DSA signature |

---

## 20. Future Roadmap (Mention Only, Not Core Solution)

Future iterations of the Barclays Quantum Security Capsule architecture may explore:

1. **Crypto-Agility Engine:** Modular runtime abstraction allowing seamless rotation from ML-KEM/ML-DSA to future NIST PQC round candidates without API breaking changes.
2. **AI-Assisted Risk Classification:** Machine learning models inspecting capsule header policy metadata to dynamically adjust lifetime validation windows based on fraud risk scores.
3. **Hardware Security Module (HSM) & Secure Enclave Integration:** Direct hardware-backed ML-KEM key decapsulation inside AWS Nitro Enclaves or Thales PayShield HSMs.
