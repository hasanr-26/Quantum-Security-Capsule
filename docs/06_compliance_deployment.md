# Document 06: Compliance, Deployment Strategy & Banking Use Cases

**Barclays Innovation Lab Proposal**  
**Author**: Principal Security Architect, Barclays Innovation Lab  

---

## 16. Compliance with NIST PQC Standards

The QSC architecture adheres strictly to August 2024 final NIST Post-Quantum Cryptography standards:

1. **FIPS 203 (ML-KEM):** Module-Lattice-Based Key-Encapsulation Mechanism Standard. Used for establishing ephemeral symmetric keys per capsule.
2. **FIPS 204 (ML-DSA):** Module-Lattice-Based Digital Signature Standard. Used for capsule authenticity and non-repudiation.
3. **FIPS 202 (SHA-3):** Permutation-Based Hash and Extendable-Output Functions (SHA3-512). Used for integrity hash computation and replay token binding.
4. **NIST SP 800-38D:** Recommendation for Block Cipher Modes of Operation: Galois/Counter Mode (AES-256-GCM). Used for symmetric payload encryption.

---

## 17. Barclays Deployment Strategy

### 3-Phase Migration Roadmap

```
Phase 1: Pilot & Peripheral APIs (Months 1-6)
  ├─ Deploy QSC SDK for internal high-value inter-service microservices.
  └─ Establish Hardware Security Module (HSM) PQC key management infrastructure.

Phase 2: High-Value Messaging & Queue Integration (Months 6-18)
  ├─ Integrate QSC wrappers into IBM MQ / Kafka financial event streams.
  └─ Deploy QSC capsule protection for SWIFT gateway outbound requests.

Phase 3: Core Banking & Mobile App Rollout (Months 18-36)
  ├─ Enable QSC SDK in Barclays Mobile Banking App for high-value transfers.
  └─ Transition corporate B2B payment APIs to mandatory QSC capsules.
```

---

## 18. Real-World Banking Use Cases

### Use Case 1: High-Value Interbank Payments & SWIFT Messaging
- **Scenario:** Processing a £50,000,000 corporate payment instruction across international banking corridors.
- **QSC Benefit:** Encapsulates transaction instruction at source. If intermediate correspondent banking networks are intercepted or compromised by state-backed quantum systems, payload confidentiality and integrity remain unbroken.

### Use Case 2: Enterprise Event-Driven Microservices (Kafka / MQ)
- **Scenario:** Core ledger events published across multi-region Kafka topics.
- **QSC Benefit:** Events are written to Kafka topics inside Quantum Security Capsules. Even if an attacker gains unauthorized access to Kafka topic logs or storage backups, historical records cannot be decrypted.

### Use Case 3: Barclays Mobile Banking & Open Banking APIs
- **Scenario:** Customer executing payment on smartphone via public 5G/Wi-Fi networks.
- **QSC Benefit:** Protects against untrusted local networks, rogue Wi-Fi access points, and compromised transport proxies by encrypting and signing the transaction capsule on the client device itself.
