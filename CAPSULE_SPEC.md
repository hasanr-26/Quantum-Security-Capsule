# Quantum Security Capsule (QSC) Specification (v1.0)

[![NIST PQC](https://img.shields.io/badge/NIST-FIPS%20203%20%7C%20FIPS%20204-green.svg)](https://csrc.nist.gov/projects/post-quantum-cryptography)
[![Tests](https://img.shields.io/badge/tests-69%20passed%20%7C%20100%25-brightgreen.svg)](tests/)
[![Status](https://img.shields.io/badge/Status-Active%20Production%20Spec-blue.svg)]()

## 1. Overview
The **Quantum Security Capsule (QSC)** is a self-contained, message-level cryptographic object designed for post-quantum financial and enterprise environments. Instead of relying exclusively on transient transport-layer security (TLS 1.3 / VPNs) which terminates at intermediate middleboxes and is vulnerable to "Harvest Now, Decrypt Later" (HNDL) attacks, a QSC encapsulates:
- Message confidentiality (AES-256-GCM)
- Post-quantum shared key encapsulation (ML-KEM-768)
- Key derivation with domain separation (HKDF-SHA3-512)
- Post-quantum non-repudiable origin signatures (ML-DSA-65)
- Deterministic integrity locking (SHA3-512)
- Temporal freshness bounds (UTC ISO-8601 timestamps)
- Single-use replay protection tokens (SHA3-512)
- Governance and policy metadata

---

## 2. Technical Cryptographic Primitives

| Component | Standard / Algorithm | Role / Purpose | NIST Standard |
| :--- | :--- | :--- | :--- |
| **Key Encapsulation Mechanism** | **ML-KEM-768** | Ephemeral post-quantum shared secret establishment per message (1088-byte ciphertext) | **NIST FIPS 203** |
| **Key Derivation Function** | **HKDF-SHA3-512** | Derives 256-bit AES content key from ML-KEM shared secret; salted with `capsule_id` and domain separated | **NIST SP 800-56C Rev. 2** |
| **Digital Signatures** | **ML-DSA-65** | Quantum-resistant lattice digital signature over canonical integrity hash (3309-byte signature) | **NIST FIPS 204** |
| **Symmetric Payload Encryption** | **AES-256-GCM** | Authenticated Encryption with Associated Data (AEAD); associated data binds `capsule_id` | **NIST SP 800-38D** |
| **Integrity Hashing & Tokens** | **SHA3-512** | Permutation-based Keccak sponge digest for canonical field binding and single-use replay tokens | **NIST FIPS 202** |

---

## 3. Data Schema & Wire Format

The reference implementation defines the schema in [`src/capsule/models.py`](src/capsule/models.py) and serializes it in [`src/capsule/wire.py`](src/capsule/wire.py).

### 3.1 JSON Wire Representation
```json
{
  "version": "QSC-1.0",
  "capsule_id": "qsc_7f2b918a3e0c45d1",
  "issued_at": "2026-09-13T01:30:00Z",
  "expires_at": "2026-09-13T01:35:00Z",
  "replay_token": "a4f89b12... (128 hex chars SHA3-512 digest)",
  "sender_id": "BARCGB22XXX",
  "recipient_id": "HDFCINBBXXX",
  "kem_ciphertext": "7c12d... (Base64 ML-KEM-768 ciphertext, 1088 bytes raw)",
  "payload_ciphertext": "e8810... (Base64 AES-256-GCM encrypted payload)",
  "payload_tag": "33f01... (Base64 16-byte GCM authentication tag)",
  "nonce": "91a2b... (Base64 12-byte GCM initialization vector)",
  "integrity_hash": "b9012... (128 hex chars canonical SHA3-512 digest)",
  "signature": "d2218... (Base64 ML-DSA-65 lattice signature, 3309 bytes raw)",
  "policy": {
    "classification": "CONFIDENTIAL",
    "jurisdiction": "UK",
    "max_hops": 3,
    "allowed_channels": ["HTTPS", "KAFKA", "MQ", "SWIFT"]
  }
}
```

### 3.2 Canonical Wire Encoding
To ensure deterministic verification and honest byte-level packet inspection:
1. Serialization uses canonical JSON formatting: keys sorted alphabetically, no insignificant whitespace (`separators=(',', ':')`), UTF-8 encoded.
2. The byte sequence transmitted over the wire is identical to the byte stream mapped by the Wireshark-style Hex Inspector in [`src/capsule/wire.py`](src/capsule/wire.py).

---

## 4. Field Specifications

### 4.1 Header & Metadata Fields
- **`version`**: `string` &mdash; Protocol specification identifier (`QSC-1.0`). Verified at Stage 1.
- **`capsule_id`**: `string` &mdash; Globally unique 64-bit hex token prefixed with `qsc_`. Serves as the unique message identifier, HKDF salt, and AEAD associated data.
- **`issued_at`**: `string (ISO-8601 UTC)` &mdash; Timestamp of capsule construction (e.g., `2026-09-13T01:30:00Z`).
- **`expires_at`**: `string (ISO-8601 UTC)` &mdash; Hard expiry deadline. Validated at Stage 2. Default validity window: 300 seconds (5 minutes).
- **`replay_token`**: `string (hex, 128 characters)` &mdash; Cryptographic binding derived via `SHA3-512(capsule_id || issued_at || sender_id || nonce)`. Validated at Stage 3.
- **`sender_id`**: `string` &mdash; Institutional BIC or service identifier of the origin client (e.g., `BARCGB22XXX`).
- **`recipient_id`**: `string` &mdash; Institutional BIC or service identifier of the destination receiver (e.g., `HDFCINBBXXX`).
- **`policy`**: `object` &mdash; Mandatory governance parameters:
  - `classification`: Data classification level (`RESTRICTED`, `CONFIDENTIAL`, `SECRET`).
  - `jurisdiction`: Regulatory territory (`UK`, `EU`, `US`).
  - `max_hops`: Maximum allowed proxy/queue hops.
  - `allowed_channels`: Permitted transport routes (`["HTTPS", "KAFKA", "MQ", "SWIFT"]`).

### 4.2 Cryptographic Payloads
- **`kem_ciphertext`**: `string (base64)` &mdash; ML-KEM-768 ciphertext (1088 bytes decoded) encapsulating the 256-bit shared secret.
- **`payload_ciphertext`**: `string (base64)` &mdash; AES-256-GCM encrypted financial payload.
- **`payload_tag`**: `string (base64)` &mdash; 16-byte authentication tag produced by AES-256-GCM.
- **`nonce`**: `string (base64)` &mdash; 12-byte (96-bit) cryptographically random initialization vector.

### 4.3 Verification & Authenticity
- **`integrity_hash`**: `string (hex, 128 characters)` &mdash; SHA3-512 digest computed over canonical representation of all fields except `signature` and `integrity_hash`.
- **`signature`**: `string (base64)` &mdash; ML-DSA-65 post-quantum digital signature (3309 bytes decoded) over `integrity_hash`, verified with the sender's registered public key.

---

## 5. Capsule Construction Pipeline (8 Steps)

Implemented in [`CapsuleBuilder.build_capsule()`](src/capsule/builder.py):

```
[ Step 1: Identifiers & Timestamps ]
   └── Generate unique capsule_id (qsc_<hex>), issued_at, and expires_at (now + 300s)

[ Step 2: ML-KEM-768 Key Encapsulation ]
   └── Encapsulate 256-bit shared secret (K) against recipient's ML-KEM public key
   └── Output: shared_secret, kem_ciphertext (1088 bytes)

[ Step 3: Key Derivation via HKDF-SHA3-512 (SP 800-56C) ]
   └── content_key = HKDF-SHA3-512(secret=K, salt=capsule_id, info="QSC-1.0/AES-256-GCM")
   └── Ensures K is never used directly as an encryption key and binds key to capsule_id

[ Step 4: AES-256-GCM Authenticated Encryption ]
   └── Encrypt payload bytes using content_key, fresh 96-bit nonce, and associated_data=capsule_id
   └── Output: payload_ciphertext, payload_tag (16 bytes), nonce (12 bytes)

[ Step 5: Single-Use Replay Token Generation ]
   └── replay_token = SHA3-512(capsule_id + issued_at + sender_id + nonce)

[ Step 6: Canonical Field Serialization ]
   └── Populate pre-capsule object with header, ciphertexts, and policy
   └── Extract canonical dictionary (excluding signature and integrity_hash)

[ Step 7: SHA3-512 Canonical Integrity Digest ]
   └── Compute 512-bit hash over canonical UTF-8 JSON bytes -> integrity_hash

[ Step 8: ML-DSA-65 Lattice Signature ]
   └── Sign integrity_hash with sender's private ML-DSA-65 key -> signature
   └── Assemble complete QuantumSecurityCapsule object
```

---

## 6. 5-Stage Zero-Trust Validation Pipeline

Implemented in [`CapsuleValidator.validate_detailed()`](src/capsule/validator.py).

Every capsule must traverse all five stages in strict sequence, cheapest first. The validator **fails closed** at the earliest failed stage, shielding expensive lattice signature calculations from malformed, expired, or replayed denial-of-service traffic:

```
┌──────────────────────────────────────────────────────────────────────────────┐
│ STAGE 1: Protocol Version Check (~1 µs)                                      │
│ Checks version == "QSC-1.0". Rejects incompatible wire versions instantly.   │
└──────────────────────────────────────┬───────────────────────────────────────┘
                                       │ PASS
                                       ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│ STAGE 2: Freshness Window Enforcement (~7 µs)                                │
│ Validates current_time <= expires_at. Rejects expired capsules without crypto.│
└──────────────────────────────────────┬───────────────────────────────────────┘
                                       │ PASS
                                       ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│ STAGE 3: Replay Cache Verification (~2 µs)                                   │
│ Queries replay registry. If replay_token seen, reject immediately.          │
└──────────────────────────────────────┬───────────────────────────────────────┘
                                       │ PASS
                                       ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│ STAGE 4: Integrity Lock (SHA3-512) (~60 µs)                                  │
│ Re-computes canonical digest. Fails if even 1 bit in headers/ciphertexts flipped.│
└──────────────────────────────────────┬───────────────────────────────────────┘
                                       │ PASS
                                       ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│ STAGE 5: Origin Authenticity Verification (ML-DSA-65) (~17 ms)               │
│ Verifies lattice signature against sender's public key. Non-repudiation lock.│
└──────────────────────────────────────┬───────────────────────────────────────┘
                                       │ ALL PASS
                                       ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│ COMMIT REPLAY TOKEN & RELEASE TO SETTLEMENT ENGINE                           │
│ Replay token committed to registry ONLY after all 5 stages succeed.          │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## 7. Decapsulation & Settlement Pipeline

Implemented in [`SecureReceiver.settle_with_report()`](src/capsule/receiver.py):
1. **Validation Prerequisite:** Capsule must achieve `ValidationReport.accepted == True` across all 5 stages.
2. **ML-KEM-768 Decapsulation:** Recipient decapsulates `kem_ciphertext` with its private ML-KEM key to recover the 256-bit shared secret $K$.
3. **Content Key Reconstruction:** Re-derives the identical 256-bit AES key via `HKDF-SHA3-512(secret=K, salt=capsule_id)`.
4. **AES-256-GCM Authenticated Decryption:** Decrypts `payload_ciphertext` using recovered `content_key`, `nonce`, `payload_tag`, and `associated_data=capsule_id`.
5. **Execution & Audit Dispatch:** Passes verified plaintext payload to core settlement ledger and records telemetry.
