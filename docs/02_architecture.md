# Document 02



## 1. Existing Communication Architecture vs. QSC Architecture

### Legacy Transport-Centric Model
In traditional financial IT infrastructure, security relies on connection tunnels established at edge proxies:

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

### Proposed Quantum Security Capsule Paradigm
QSC shifts security directly into the payload. Each message becomes an autonomous, self-describing, post-quantum encrypted, digitally signed, and time-locked container:

```
                  Sender Application / Client
                              │
                 ┌────────────┴────────────┐
                 ▼                         ▼
          Message Payload            Policy Metadata
                 │                         │
                 └────────────┬────────────┘
                              │
                    Quantum Capsule Builder ([builder.py](file:///c:/Users/hasan/antigravity/QSC/src/capsule/builder.py))
         ┌────────────────────┼────────────────────┐
         │                    │                    │
     Encrypt (AES-GCM)   Sign (ML-DSA)      Key Encapsulation (ML-KEM)
  ([symmetric.py](file:///c:/Users/hasan/antigravity/QSC/src/crypto/symmetric.py))     ([dsa.py](file:///c:/Users/hasan/antigravity/QSC/src/crypto/dsa.py))       ([kem.py](file:///c:/Users/hasan/antigravity/QSC/src/crypto/kem.py))
         │                    │                    │
         └────────────────────┼────────────────────┘
                              │
                   Quantum Security Capsule ([models.py](file:///c:/Users/hasan/antigravity/QSC/src/capsule/models.py))
                              │
         ┌────────────────────┴────────────────────┐
         │  Transmitted via REST / Kafka / MQ / File│
         └────────────────────┬────────────────────┘
                              │
                   Capsule Validator & Receiver ([validator.py](file:///c:/Users/hasan/antigravity/QSC/src/capsule/validator.py))
         ┌────────────────────┼────────────────────┐
      Verify Sig          Verify Hash          Decapsulate & Decrypt
         └────────────────────┼────────────────────┘
                              │
                   Core Banking Backend / Receiver
```

---

## 2. The 5 Core Components

The QSC architecture consists of 5 modular components implemented in [`src/capsule`](file:///c:/Users/hasan/antigravity/QSC/src/capsule) and [`src/crypto`](file:///c:/Users/hasan/antigravity/QSC/src/crypto):

### 1. Capsule Builder ([`builder.py`](file:///c:/Users/hasan/antigravity/QSC/src/capsule/builder.py))
Assembles raw payment payloads or binary files into post-quantum capsules through a deterministic 7-step pipeline.

### 2. PQC Key Encapsulation Engine ([`kem.py`](file:///c:/Users/hasan/antigravity/QSC/src/crypto/kem.py))
Implements NIST FIPS 203 ([`ML-KEM-768`](file:///c:/Users/hasan/antigravity/QSC/src/crypto/kem.py)). Establishes a 256-bit symmetric shared secret between sender and receiver per message without interactive handshakes.

### 3. PQC Digital Signature Engine ([`dsa.py`](file:///c:/Users/hasan/antigravity/QSC/src/crypto/dsa.py))
Implements NIST FIPS 204 ([`ML-DSA-65`](file:///c:/Users/hasan/antigravity/QSC/src/crypto/dsa.py)). Computes lattice digital signatures over canonical SHA3-512 integrity hashes using the sender's private key, guaranteeing non-repudiation and origin authenticity.

### 4. Capsule Validator ([`validator.py`](file:///c:/Users/hasan/antigravity/QSC/src/capsule/validator.py))
Enforces mandatory zero-trust validation through a 5-stage pipeline before granting access to ciphertext.

### 5. Secure Receiver ([`receiver.py`](file:///c:/Users/hasan/antigravity/QSC/src/capsule/receiver.py))
Executes ML-KEM decapsulation to recover the symmetric encryption key, decrypts AES-256-GCM ciphertext, verifies tag validity, and forwards the plaintext payload.

---

## 3. The 7-Step Capsule Builder Pipeline

When creating a capsule, [`CapsuleBuilder.build_capsule()`](file:///c:/Users/hasan/antigravity/QSC/src/capsule/builder.py) executes the following sequence:

```
[ Step 1: ID & Timestamps ]  --->  Generate Unique Capsule ID & ISO-8601 Timestamps (TTL: 300s)
[ Step 2: ML-KEM-768 Key ]    --->  Encapsulate 256-bit Shared Secret (K) & Generate KEM Ciphertext
[ Step 3: AES-256-GCM ]       --->  Encrypt Payload with K; Generate Nonce & GCM Auth Tag
[ Step 4: Replay Token ]      --->  Compute SHA3-512 Replay Token (CapsuleID + Timestamp + Nonce)
[ Step 5: Canonicalization ]  --->  Build Deterministic JSON Schema for Integrity Lock
[ Step 6: SHA3-512 Digest ]   --->  Compute 512-bit Canonical Integrity Hash
[ Step 7: ML-DSA-65 Sign ]    --->  Sign Integrity Hash with Sender Private Key
```

---

## 4. The 5-Stage Zero-Trust Validation Pipeline

Before decapsulating ciphertexts, [`CapsuleValidator.validate()`](file:///c:/Users/hasan/antigravity/QSC/src/capsule/validator.py) enforces 5 sequential security gates:

1. **Stage 1: Version & Schema Check:** Confirms `version == "QSC-1.0"`.
2. **Stage 2: Timestamp & Expiry Check:** Verifies current time $\le$ `expires_at` using wall-clock validation ([`timestamp.py`](file:///c:/Users/hasan/antigravity/QSC/src/utils/timestamp.py)).
3. **Stage 3: Replay Cache Verification:** Queries the replay registry ([`validator.py`](file:///c:/Users/hasan/antigravity/QSC/src/capsule/validator.py)) to ensure the `replay_token` has not been seen within the TTL window.
4. **Stage 4: Canonical Integrity Verification:** Re-computes canonical SHA3-512 integrity hash from capsule fields and compares against `integrity_hash`.
5. **Stage 5: ML-DSA-65 Signature Verification:** Verifies signature authenticity using sender public key ([`dsa.py`](file:///c:/Users/hasan/antigravity/QSC/src/crypto/dsa.py)).

---

## 5. QSC Wire Format & Data Schema ([`models.py`](file:///c:/Users/hasan/antigravity/QSC/src/capsule/models.py))

```json
{
  "capsule_id": "qsc_99a81f3b7c2a41d0",
  "version": "QSC-1.0",
  "issued_at": "2026-07-28T11:50:00Z",
  "expires_at": "2026-07-28T11:55:00Z",
  "sender_id": "barclays-mobile-app-001",
  "recipient_id": "barclays-core-ledger-002",
  "policy": {
    "classification": "RESTRICTED",
    "max_hops": 2,
    "allowed_networks": ["SWIFT", "KAFKA-CORE"]
  },
  "replay_token": "a4f89... (128 hex chars SHA3-512 digest)",
  "kem_ciphertext": "7c12d... (Base64 ML-KEM-768 ciphertext, 1088 bytes)",
  "aes_nonce": "91a2b... (Base64 12-byte GCM IV)",
  "payload_ciphertext": "e8810... (Base64 AES-256-GCM encrypted payload)",
  "gcm_tag": "33f01... (Base64 16-byte GCM authentication tag)",
  "integrity_hash": "b9012... (128 hex chars canonical SHA3-512 digest)",
  "signature": "d2218... (Base64 ML-DSA-65 lattice signature, 3309 bytes)"
}
```
