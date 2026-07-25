# Document 03: Architectural & Sequence Diagrams

**Barclays Innovation Lab Proposal**  
**Author**: Principal Security Architect, Barclays Innovation Lab  

---

## 9. Architecture Diagram (Text & ASCII)

```
===================================================================================
                       BARCLAYS QUANTUM SECURITY CAPSULE (QSC)
                               ARCHITECTURE OVERVIEW
===================================================================================

[ CLIENT / ORIGINATOR ]
  │
  ├──► [ 1. Payload Creation ] (Raw Banking Instruction / SWIFT / REST API Request)
  │
  ├──► [ 2. Capsule Builder ]
  │      │
  │      ├──► ML-KEM-768 Engine (FIPS 203) ──► Encapsulate Symmetric Key (K)
  │      ├──► AES-256-GCM Engine          ──► Encrypt Payload with K
  │      ├──► SHA3-512 Engine             ──► Generate Integrity Hash & Replay Token
  │      └──► ML-DSA-65 Engine (FIPS 204)  ──► Sign Hash with Sender Private Key
  │
  └──► [ 3. Transmitted QSC Container ]
         │
         │  ( Can travel across ANY Transport: HTTPS, Kafka, MQ, VPN, SWIFT )
         │
         ▼
[ UNTRUSTED NETWORK / HARVEST NOW DECRYPT LATER (HNDL) ADVERSARY ]
  │  - Encrypted Payload: Unreadable without Recipient ML-KEM Private Key
  │  - Signature: Unforgeable without Sender ML-DSA Private Key
  │  - Replay Token: Locked to specific timestamp & unique ID
  │
  ▼
[ SERVER / RECEIVER ]
  │
  ├──► [ 4. Capsule Validator ]
  │      │
  │      ├──► 1. Check Lifetime (Current Time <= ExpiresAt)
  │      ├──► 2. Check Replay Registry (Redis / Cache)
  │      ├──► 3. Re-compute SHA3-512 Canonical Integrity Digest
  │      └──► 4. Verify ML-DSA-65 Signature using Sender Public Key
  │
  ├──► [ 5. Decryption Execution ] (Executed ONLY if ALL Validation checks PASS)
  │      │
  │      ├──► ML-KEM-768 Decapsulate ─────► Recover Symmetric Key (K)
  │      └──► AES-256-GCM Decrypt ────────► Recover Plaintext Payload
  │
  └──► [ 6. Core Banking Engine ] (Executes Wire Transfer / Payment Processing)

===================================================================================
```

---

## 10. Sequence Diagram

```mermaid
sequenceDiagram
    autonumber
    actor Client as Barclays Client / App
    participant Builder as Capsule Builder
    participant Network as Transport (Kafka/MQ/HTTPS)
    participant Validator as Capsule Validator
    participant Receiver as Secure Receiver
    actor Core as Core Banking Server

    Client->>Builder: Send Message Payload + Recipient ID
    Note over Builder: 1. Generate UUID & Fresh Timestamps
    Note over Builder: 2. ML-KEM-768 Shared Key Encapsulation
    Note over Builder: 3. AES-256-GCM Encrypt Payload
    Note over Builder: 4. Compute SHA3-512 Integrity Hash & Replay Token
    Note over Builder: 5. ML-DSA-65 Sign Hash with Sender Key
    Builder-->>Client: Return Quantum Security Capsule (QSC)

    Client->>Network: Transmit QSC Package

    Note over Network: Attacker captures network stream<br/>(Harvest Now, Decrypt Later)

    Network->>Validator: Deliver QSC Package
    Note over Validator: Check 1: Expiry & Timestamp Bounds
    Note over Validator: Check 2: Replay Cache Token Search
    Note over Validator: Check 3: Canonical SHA3-512 Hash Match
    Note over Validator: Check 4: ML-DSA Signature Verification

    alt Validation Fails
        Validator-->>Network: Reject Capsule (Alert Security Operations)
    else Validation Passes
        Validator->>Receiver: Forward Validated Capsule
        Note over Receiver: 1. ML-KEM Decapsulate Shared Key
        Note over Receiver: 2. AES-256-GCM Decrypt Payload
        Receiver->>Core: Dispatch Plaintext Banking Instruction
        Core-->>Client: Confirm Transaction Execution
    end
```
