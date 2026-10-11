# 06 — Compliance, Regulatory Alignment and Enterprise Deployment

[![NIST PQC](https://img.shields.io/badge/NIST-FIPS%20203%20%7C%20FIPS%20204-green.svg)](https://csrc.nist.gov/projects/post-quantum-cryptography)
[![Tests](https://img.shields.io/badge/tests-69%20passed%20%7C%20100%25-brightgreen.svg)](../tests/)
[![Compliance](https://img.shields.io/badge/Compliance-PRA%20%7C%20FCA%20%7C%20G7%20PQC-blue.svg)]()

---

## 1. Compliance with August 2024 Final NIST PQC Standards

The Quantum Security Capsule (QSC) architecture adheres strictly to the definitive cryptographic standards released by the National Institute of Standards and Technology (NIST):

| Standard | Specification | Implementation in QSC | Role in Architecture |
| :--- | :--- | :--- | :--- |
| **NIST FIPS 203** | Module-Lattice-Based Key-Encapsulation Mechanism | [`src/crypto/kem.py`](../src/crypto/kem.py) (`MLKEM768`) | Per-message ephemeral shared secret establishment |
| **NIST FIPS 204** | Module-Lattice-Based Digital Signature Standard | [`src/crypto/dsa.py`](../src/crypto/dsa.py) (`MLDSA65`) | Non-repudiable origin authentication over canonical digest |
| **NIST SP 800-56C Rev. 2** | Recommendation for Key-Derivation Methods in Key-Establishment | [`src/crypto/kdf.py`](../src/crypto/kdf.py) (`derive_payload_key`) | HKDF-SHA3-512 content key derivation with domain separation |
| **NIST SP 800-38D** | Recommendation for Block Cipher Modes of Operation: Galois/Counter Mode | [`src/crypto/symmetric.py`](../src/crypto/symmetric.py) (`encrypt_aes_256_gcm`) | Authenticated symmetric encryption (AEAD) with `capsule_id` binding |
| **NIST FIPS 202** | Permutation-Based Hash and Extendable-Output Functions (SHA-3) | [`src/crypto/hashing.py`](../src/crypto/hashing.py) (`compute_sha3_512`) | 512-bit canonical integrity locking and single-use replay tokens |
| **RFC 8446** | The Transport Layer Security (TLS) Protocol Version 1.3 | [`src/server/tls_config.py`](../src/server/tls_config.py) | Outer transport security for settlement node and proxy |

---

## 2. Global Regulatory and Financial Compliance Alignment

International financial regulators are actively mandating timelines for post-quantum cryptographic transitions. QSC positions institutions for early compliance ahead of enforcement deadlines:

### 2.1 Bank of England & Prudential Regulation Authority (PRA)
- **Supervisory Statement on Operational Resilience (SS1/21):** Mandates that financial market infrastructure firms prevent systemic disruption to critical economic functions. QSC guarantees that CHAPS payment instructions and interbank liquidity streams cannot be compromised retroactively via HNDL.
- **Dear CEO Letter on Post-Quantum Preparedness:** Directs banks to inventory classical cryptographic dependencies and initiate quantum-safe migration roadmaps.

### 2.2 Financial Conduct Authority (FCA) & G7 Cyber Expert Group (CEG)
- **G7 CEG Statement on Quantum Computing Risks:** Emphasizes that "Harvest Now, Decrypt Later" constitutes an active, present threat to global financial stability. Recommends hybrid and application-layer defenses for high-value financial transactions.
- **FCA Handbook (SYSC 13.9 - Information Security):** Requires regulated firms to maintain technical measures ensuring the confidentiality, integrity, and authenticity of customer data and payment mandates.

### 2.3 US National Security Memorandum 10 (NSM-10) & OMB M-23-02
- Sets mandatory milestones for federal agencies and regulated financial entities to complete migration to post-quantum cryptography by 2035, with critical systems migrating by 2030. QSC's use of final FIPS 203/204 primitives directly fulfills NSM-10 requirements.

### 2.4 CPMI-IOSCO Principles for Financial Market Infrastructures (PFMI)
- **Principle 17 (Operational Risk):** Requires FMIs to implement robust cryptographic architectures capable of adapting to emerging threats without service interruption.

---

## 3. Enterprise Integration Blueprints

QSC is engineered as a drop-in message layer that operates seamlessly inside existing enterprise networks without requiring network re-cabling or firewall overhauls:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       ENTERPRISE DEPLOYMENT TOPOLOGY                        │
└─────────────────────────────────────────────────────────────────────────────┘

 [ Client Application / Banking Portal ]
                   │
                   ▼ (1. Encapsulate via QSC SDK)
 [ Autonomous Quantum Security Capsule ]
                   │
                   ▼ (2. Transmit over Existing Infrastructure)
  ┌─────────────────────────────────────────────────────────┐
  │  • HTTPS / REST API via API Gateway / WAF               │
  │  • Apache Kafka Partition / Topic (Data At Rest)        │
  │  • IBM MQ Enterprise Queue                              │
  │  • SWIFT Interbank Messaging Network                    │
  │  • Encrypted Treasury File Archive (.qsc)               │
  └────────────────────────┬────────────────────────────────┘
                           │
                           ▼ (3. Deliver to Core Settlement Engine)
 [ 5-Stage Zero-Trust Validator & Secure Receiver ]
                   │
                   ▼ (4. Decapsulate & Commit to Core Ledger)
 [ Barclays Core Banking Engine / High-Value Settlement ]
```

### Blueprint 1: High-Value Interbank Payments & SWIFT Messaging
- **Scenario:** Originating and clearing high-value corporate wires (£50,000,000+).
- **Format:** ISO 20022 `pacs.008.001.08` (Financial Institutional Customer Credit Transfer) and SWIFT MT103.
- **Implementation:** Demonstrated in [`src/demo/banking_transfer.py`](../src/demo/banking_transfer.py) and Tab 01 of the Security Workbench.
- **Operational Reality:** The payload is armored at the originating branch before being dispatched across international correspondent networks. Intermediary SWIFT FIN or clearing hops cannot inspect or manipulate account data.

### Blueprint 2: Enterprise Event Streams (Apache Kafka / IBM MQ)
- **Scenario:** Asynchronous event streaming between microservices and distributed ledger topics.
- **The Problem:** Traditional TLS protects data only while traversing the TCP socket. The moment data enters Kafka, messages reside in plaintext inside broker topic logs and disk partitions.
- **QSC Solution:** Microservices publish pre-encapsulated QSC objects directly into Kafka topics. Messages remain encrypted in queue memory and on storage volumes until consumed by the designated receiver microservice.

### Blueprint 3: Confidential Treasury File Storage (`.qsc`)
- **Scenario:** Storing sensitive treasury asset reports, customer KYC dossiers, or syndicated credit agreements.
- **Implementation:** Demonstrated in [`src/demo/file_encrypt_demo.py`](../src/demo/file_encrypt_demo.py).
- **Operational Reality:** Packages raw binary documents into self-contained `.qsc` disk containers, combining ML-KEM-768 key encapsulation, ML-DSA-65 signatures, and AES-256-GCM encryption. Files remain secure even under complete cloud storage bucket compromise.

### Blueprint 4: Hardware Security Module (HSM) Integration
- **Architecture:** In enterprise production, recipient ML-KEM private keys and sender ML-DSA signing keys reside within tamper-responsive Hardware Security Modules (e.g., Thales payShield, AWS CloudHSM, or nCipher).
- **Boundary Separation:** The `MLKEM768` and `MLDSA65` wrappers in [`src/crypto/`](../src/crypto/) expose clean decoupled interfaces designed for drop-in delegation to PKCS#11 or KMIP cryptographic hardware accelerators without modifying upstream application code.

---

## 4. Institutional 3-Phase Migration Strategy

```
Phase 1: Pilot & Peripheral APIs (Months 1-6)
  ├─ Deploy QSC SDK (src/capsule) for high-value inter-service microservices.
  ├─ Provision Hardware Security Module (HSM) PQC key management infrastructure.
  └─ Implement live settlement workbench (:8443) and interception testing (:8444).

Phase 2: High-Value Messaging & Queue Integration (Months 6-18)
  ├─ Integrate QSC serialisation into Apache Kafka and IBM MQ event streams.
  ├─ Deploy QSC capsule protection for outbound SWIFT payment instructions.
  └─ Establish distributed Redis replay token caching for horizontal scaling.

Phase 3: Core Banking & Mobile App Rollout (Months 18-36)
  ├─ Embed QSC SDK into Barclays Mobile Banking App for high-value transfers.
  ├─ Transition B2B open banking partner APIs to mandatory QSC capsules.
  └─ Transition treasury file storage archives to automated .qsc encryption.
```
