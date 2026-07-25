# Document 02: Architecture and Component Specifications

**Barclays Innovation Lab Proposal**  
**Author**: Principal Security Architect, Barclays Innovation Lab  

---

## 4. Existing Communication Architecture

### Legacy Transport-Centric Model
In today's banking infrastructure, security is tied directly to network connections:

```
+------------------+         Encrypted TLS Tunnel         +------------------+
|  Client / App    | ===================================> |  API Gateway     |
+------------------+     (Secures connection pipe)        +--------+---------+
                                                                   | Decrypts
                                                                   v
+------------------+       Internal Plaintext / MQ        +------------------+
| Internal Service | <----------------------------------- | Core Backend     |
+------------------+                                      +------------------+
```

### Critical Deficiencies
1. **Single Point of Compromise:** Decryption happens at the edge gateway. Internal networks remain vulnerable to insider threats and lateral movement.
2. **Loss of Non-Repudiation at Storage:** Once data is written to databases or queues, transport security expires, leaving stored data unencrypted unless secondary encryption is manually bolted on.

---

## 5. Proposed Quantum Security Capsule Architecture

### Message-Centric Post-Quantum Paradigm
The Quantum Security Capsule (QSC) architecture shifts security directly into the payload data payload itself. Each message becomes an autonomous, self-describing, post-quantum encrypted, signed, and time-bound digital container.

```
                  Client Application
                          │
             ┌────────────┴────────────┐
             ▼                         ▼
      Message Payload            Policy Metadata
             │                         │
             └────────────┬────────────┘
                          │
               Quantum Capsule Builder
     ┌────────────────────┼────────────────────┐
     │                    │                    │
 Encrypt (AES-GCM)   Sign (ML-DSA)      Key Encapsulation (ML-KEM)
     │                    │                    │
     └────────────────────┼────────────────────┘
                          │
               Quantum Security Capsule
                          │
     ┌────────────────────┴────────────────────┐
     │  Transmitted via REST / Kafka / MQ / TLS│
     └────────────────────┬────────────────────┘
                          │
               Capsule Validator & Receiver
     ┌────────────────────┼────────────────────┐
  Verify Sig          Verify Hash          Decapsulate & Decrypt
     └────────────────────┼────────────────────┘
                          │
                    Core Backend
```

---

## 6. End-to-End Communication Workflow

```
[ Sender Client ]                   [ Network Layer ]                  [ Target Receiver ]
        │                                   │                                    │
        ├─ 1. Assembles Transaction Payload  │                                    │
        ├─ 2. Encapsulates Secret (ML-KEM)  │                                    │
        ├─ 3. Encrypts Payload (AES-256-GCM)│                                    │
        ├─ 4. Binds Timestamp & Replay Token│                                    │
        ├─ 5. Signs Hash (ML-DSA-65)        │                                    │
        │                                   │                                    │
        ├──────────── Transmit QSC Container ───────────────────────────────────►│
        │             (over HTTPS/MQ/Kafka) │                                    │
        │                                   │                                    │
        │                                   │  ┌─ 6. Validate Version & Lifetime │
        │                                   │  ├─ 7. Check Replay Registry       │
        │                                   │  ├─ 8. Re-compute SHA3-512 Hash    │
        │                                   │  ├─ 9. Verify ML-DSA Signature     │
        │                                   │  ├─ 10. Decapsulate ML-KEM Key     │
        │                                   │  └─ 11. Decrypt AES-256-GCM        │
        │                                   │                                    │
```

---

## 7. Detailed Component Descriptions

The QSC architecture consists of **exactly 5 core components**:

### Component 1: Capsule Builder
- **Role:** Assembles raw message payloads into post-quantum capsules.
- **Functions:** Generates UUIDs, fetches receiver ML-KEM public key, invokes ML-KEM encapsulation, encrypts payload via AES-256-GCM, generates SHA3-512 replay token, builds canonical JSON, and signs with ML-DSA-65 private key.

### Component 2: PQC Key Encapsulation Engine (ML-KEM)
- **Role:** Implements NIST FIPS 203 (ML-KEM-768 / ML-KEM-1024).
- **Functions:** Establishes a 256-bit symmetric shared secret between sender and recipient per message without requiring interactive key exchange handshakes.

### Component 3: PQC Digital Signature Engine (ML-DSA)
- **Role:** Implements NIST FIPS 204 (ML-DSA-65 / ML-DSA-87).
- **Functions:** Computes lattice-based digital signatures over the capsule's canonical SHA3-512 integrity hash using the sender's private key, guaranteeing non-repudiation and authenticity.

### Component 4: Capsule Validator
- **Role:** Enforces mandatory zero-trust validation before granting access to ciphertext.
- **Functions:** Inspects schema version, checks timestamp freshness against wall clock, queries distributed replay cache, re-calculates SHA3-512 digest, and verifies ML-DSA signature.

### Component 5: Secure Receiver
- **Role:** Decrypts validated capsules and dispatches payload to internal application logic.
- **Functions:** Executes ML-KEM decapsulation to recover AES-256-GCM key, decrypts ciphertext, validates GCM authentication tag, and forwards plaintext.

---

## 8. Internal Structure of a Quantum Security Capsule

Each QSC object is formatted as a structured cryptographic payload (JSON over wire, CBOR for micro-latency binary queues):

```
+-----------------------------------------------------------------------+
|                         HEADER & METADATA                             |
|  - Version: QSC-1.0                                                   |
|  - Capsule ID: qsc_99a81f3b7c2a41d0                                   |
|  - Issued At: 2026-07-26T01:19:12Z                                    |
|  - Expires At: 2026-07-26T01:24:12Z                                   |
|  - Sender ID: barclays-mobile-0091                                    |
|  - Recipient ID: barclays-swift-gateway                               |
|  - Policy: { Classification: RESTRICTED, Max Hops: 2 }                |
+-----------------------------------------------------------------------+
|                    REPLAY & INTEGRITY LOCK                             |
|  - Replay Token: SHA3-512(CapsuleID + Timestamp + Sender + Nonce)     |
|  - Integrity Hash: SHA3-512(Canonical Header + Payload + Policy)       |
+-----------------------------------------------------------------------+
|                    POST-QUANTUM CRYPTOGRAPHIC BODY                    |
|  - ML-KEM Ciphertext: Encapsulated Shared Key Payload (FIPS 203)      |
|  - AES-256-GCM Nonce: 12-byte initialization vector                   |
|  - Payload Ciphertext: Encrypted financial message                    |
|  - GCM Auth Tag: 16-byte authentication tag                           |
|  - ML-DSA Signature: Post-quantum lattice signature (FIPS 204)         |
+-----------------------------------------------------------------------+
```
