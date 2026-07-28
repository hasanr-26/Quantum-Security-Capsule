# Document 06s

---

## 1. Compliance with Final August 2024 NIST PQC Standards

The QSC architecture adheres strictly to NIST's finalized Post-Quantum Cryptography standards:

1. **FIPS 203 (ML-KEM):** Module-Lattice-Based Key-Encapsulation Mechanism Standard. Used for establishing 256-bit ephemeral shared keys per capsule without vulnerable Diffie-Hellman key exchanges.
2. **FIPS 204 (ML-DSA):** Module-Lattice-Based Digital Signature Standard. Used for capsule authenticity, integrity verification, and non-repudiation.
3. **FIPS 202 (SHA-3):** Permutation-Based Hash and Extendable-Output Functions (SHA3-512). Used for computing canonical integrity hashes and binding replay tokens.
4. **NIST SP 800-38D:** Recommendation for Block Cipher Modes of Operation: Galois/Counter Mode (AES-256-GCM). Used for authenticated symmetric payload encryption.

---

## 2. Barclays 3-Phase Deployment Strategy

```
Phase 1: Pilot & Peripheral APIs (Months 1-6)
  ├─ Deploy QSC SDK ([`src/capsule`](file:///c:/Users/hasan/antigravity/QSC/src/capsule)) for high-value inter-service microservices.
  └─ Establish Hardware Security Module (HSM) PQC key management infrastructure.

Phase 2: High-Value Messaging & Queue Integration (Months 6-18)
  ├─ Integrate QSC wrappers into IBM MQ / Kafka financial event streams.
  └─ Deploy QSC capsule protection for outbound SWIFT payment instructions.

Phase 3: Core Banking & Mobile App Rollout (Months 18-36)
  ├─ Enable QSC SDK in Barclays Mobile Banking App for high-value transfers.
  └─ Transition corporate B2B payment APIs to mandatory QSC capsules.
```

---

## 3. Real-World Banking Use Cases

### Use Case 1: High-Value Interbank Payments & SWIFT Messaging
- **Scenario:** Processing a £50,000,000 corporate payment instruction across international banking corridors ([`banking_transfer.py`](file:///c:/Users/hasan/antigravity/QSC/src/demo/banking_transfer.py)).
- **QSC Benefit:** Encapsulates transaction instructions at origin. If intermediate correspondent networks are intercepted by state actors, payload confidentiality and integrity remain unbroken.

### Use Case 2: Enterprise Event-Driven Microservices (Kafka / MQ)
- **Scenario:** Core ledger events published across multi-region Kafka topics.
- **QSC Benefit:** Events are written to Kafka topics inside Quantum Security Capsules. Even if an attacker gains unauthorized access to Kafka topic logs or storage backups, historical records cannot be decrypted.

### Use Case 3: Barclays Mobile Banking & Open Banking APIs
- **Scenario:** Customer executing payment on smartphone via public 5G/Wi-Fi networks.
- **QSC Benefit:** Protects against untrusted local networks, rogue Wi-Fi access points, and compromised transport proxies by encrypting and signing the transaction capsule on the client device itself.

### Use Case 4: Confidential File & Document Storage (`.qsc`)
- **Scenario:** Storing sensitive treasury reports, legal contracts, or customer identity files ([`file_encrypt_demo.py`](file:///c:/Users/hasan/antigravity/QSC/src/demo/file_encrypt_demo.py)).
- **QSC Benefit:** Packages raw files into self-contained encrypted `.qsc` disk files. Protects data at rest against host compromise or storage bucket leaks.
