# Quantum Security Capsule (QSC) Specification (v1.0)

## Overview
The **Quantum Security Capsule (QSC)** is a self-contained, message-level cryptographic object designed for post-quantum financial and enterprise environments. Instead of relying exclusively on transport-layer security (TLS/VPN), a QSC encapsulates payload confidentiality, digital signatures, sender identity, integrity hashes, timestamp bounds, replay prevention tokens, and policy metadata directly into the message payload itself.

---

## Technical Cryptographic Primitives

| Component | Standard / Algorithm | Role / Purpose |
| :--- | :--- | :--- |
| **Key Encapsulation Mechanism** | **ML-KEM-768 / ML-KEM-1024** (NIST FIPS 203) | Post-quantum shared secret establishment per message |
| **Digital Signatures** | **ML-DSA-65 / ML-DSA-87** (NIST FIPS 204) | Non-repudiable post-quantum signature |
| **Symmetric Payload Encryption** | **AES-256-GCM** (NIST SP 800-38D) | Confidentiality + Authenticated Encryption with Associated Data (AEAD) |
| **Integrity Hashing** | **SHA3-512** (NIST FIPS 202) | Full-capsule integrity digest and replay token binding |

---

## Wire Format (JSON / Serialized Schema)

```json
{
  "version": "QSC-1.0",
  "capsule_id": "qsc_uuid_v4_identifier",
  "issued_at": "2026-07-26T01:19:12Z",
  "expires_at": "2026-07-26T01:24:12Z",
  "replay_token": "sha3_512_hex_token",
  "sender_id": "barclays-core-banking-client-8812",
  "recipient_id": "barclays-swift-gateway-01",
  "kem_ciphertext": "base64_encoded_ml_kem_ciphertext",
  "payload_ciphertext": "base64_encoded_aes_256_gcm_ciphertext",
  "payload_tag": "base64_encoded_gcm_auth_tag",
  "nonce": "base64_encoded_gcm_iv_12_bytes",
  "integrity_hash": "sha3_512_hex_of_canonical_fields",
  "signature": "base64_encoded_ml_dsa_signature",
  "policy": {
    "classification": "CONFIDENTIAL",
    "jurisdiction": "UK",
    "max_hops": 3,
    "allowed_channels": ["HTTPS", "KAFKA", "MQ"]
  }
}
```

---

## Field Specifications

### Header & Metadata
- **`version`**: `string` - Capsule format version tag (`QSC-1.0`).
- **`capsule_id`**: `string` - Globally unique UUID v4 tracking token.
- **`issued_at`**: `ISO8601 string` - UTC timestamp when capsule was assembled.
- **`expires_at`**: `ISO8601 string` - UTC timestamp after which validation MUST fail. Default lifetime: 300 seconds.
- **`replay_token`**: `string (hex)` - SHA3-512 cryptographic binding of `capsule_id + issued_at + sender_id + nonce`.
- **`sender_id`**: `string` - Authenticated client/service identity token.
- **`recipient_id`**: `string` - Target recipient identity.

### Cryptographic Payloads
- **`kem_ciphertext`**: `string (base64)` - ML-KEM encapsulation payload containing encapsulated symmetric key material.
- **`payload_ciphertext`**: `string (base64)` - AES-256-GCM encrypted message body.
- **`payload_tag`**: `string (base64)` - 16-byte authentication tag from AES-256-GCM.
- **`nonce`**: `string (base64)` - 12-byte initialization vector used for GCM encryption.

### Verification & Policy
- **`integrity_hash`**: `string (hex)` - SHA3-512 digest computed over canonical JSON string of all header, ciphertext, and policy fields.
- **`signature`**: `string (base64)` - Post-quantum ML-DSA digital signature created over `integrity_hash` using the sender's private key.
- **`policy`**: `object` - Governance parameters including authorization, classification, and routing limits.

---

## Validation Lifecycle

```
┌─────────────────────────────────────────────────────────┐
│ 1. Header Validation                                    │
│    - Version matches QSC-1.0                            │
│    - Current time <= expires_at                         │
│    - Replay token not present in replay registry        │
└────────────────────────────┬────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────┐
│ 2. Signature & Integrity Verification                   │
│    - Compute SHA3-512 hash over canonical fields        │
│    - Compare computed hash with integrity_hash          │
│    - Verify ML-DSA signature using sender's public key  │
└────────────────────────────┬────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────┐
│ 3. Key Decapsulation & Decryption                       │
│    - Decapsulate shared secret via ML-KEM private key   │
│    - Decrypt payload_ciphertext via AES-256-GCM        │
│    - Verify GCM authentication tag                      │
└─────────────────────────────────────────────────────────┘
```
