import base64
from datetime import timedelta
from typing import Dict, Any

from src.crypto import (
    compute_sha3_512,
    canonicalize_json,
    encrypt_aes_256_gcm,
    derive_payload_key,
    MLKEM768,
    MLDSA65
)
from src.utils import (
    get_utc_now,
    format_iso8601,
    generate_capsule_id,
    generate_replay_token
)
from src.capsule.models import QuantumSecurityCapsule, PolicyMetadata

class CapsuleBuilder:
    """
    Assembles a Quantum Security Capsule by combining PQC Key Encapsulation (ML-KEM-768),
    PQC Digital Signature (ML-DSA-65), AES-256-GCM symmetric payload encryption,
    SHA3-512 integrity locking, and freshness bounds.
    """

    def __init__(self, sender_id: str, sender_private_dsa_key: bytes):
        self.sender_id = sender_id
        self.sender_private_dsa_key = sender_private_dsa_key

    def build_capsule(
        self,
        recipient_id: str,
        recipient_public_kem_key: bytes,
        payload: bytes,
        validity_seconds: int = 300,
        policy: PolicyMetadata = None
    ) -> QuantumSecurityCapsule:
        if policy is None:
            policy = PolicyMetadata()

        # 1. Identifiers & Timestamps
        capsule_id = generate_capsule_id()
        now = get_utc_now()
        issued_at = format_iso8601(now)
        expires_at = format_iso8601(now + timedelta(seconds=validity_seconds))

        # 2. PQC Key Encapsulation (ML-KEM-768)
        shared_secret, kem_ct_bytes = MLKEM768.encapsulate(recipient_public_kem_key)
        kem_ciphertext_b64 = base64.b64encode(kem_ct_bytes).decode('utf-8')

        # 3. Content Key Derivation (HKDF-SHA3-512, NIST SP 800-56C)
        content_key = derive_payload_key(shared_secret, capsule_id)

        # 4. Symmetric Payload Encryption (AES-256-GCM)
        ciphertext_bytes, nonce_bytes, tag_bytes = encrypt_aes_256_gcm(
            key=content_key,
            plaintext=payload,
            associated_data=capsule_id.encode('utf-8')
        )

        payload_ciphertext_b64 = base64.b64encode(ciphertext_bytes).decode('utf-8')
        payload_tag_b64 = base64.b64encode(tag_bytes).decode('utf-8')
        nonce_b64 = base64.b64encode(nonce_bytes).decode('utf-8')

        # 5. Replay Protection Token
        replay_token = generate_replay_token(capsule_id, issued_at, self.sender_id, nonce_b64)

        # 6. Preliminary Capsule Data Assembly
        pre_capsule = QuantumSecurityCapsule(
            version="QSC-1.0",
            capsule_id=capsule_id,
            issued_at=issued_at,
            expires_at=expires_at,
            replay_token=replay_token,
            sender_id=self.sender_id,
            recipient_id=recipient_id,
            kem_ciphertext=kem_ciphertext_b64,
            payload_ciphertext=payload_ciphertext_b64,
            payload_tag=payload_tag_b64,
            nonce=nonce_b64,
            integrity_hash="",
            signature="",
            policy=policy.__dict__ if isinstance(policy, PolicyMetadata) else policy
        )

        # 7. Integrity Hash (SHA3-512 over canonical fields)
        canonical_bytes = canonicalize_json(pre_capsule.get_canonical_fields())
        integrity_hash = compute_sha3_512(canonical_bytes)
        pre_capsule.integrity_hash = integrity_hash

        # 8. Post-Quantum Digital Signature (ML-DSA-65 over integrity_hash)
        signature_bytes = MLDSA65.sign(self.sender_private_dsa_key, integrity_hash)
        signature_b64 = base64.b64encode(signature_bytes).decode('utf-8')
        pre_capsule.signature = signature_b64

        return pre_capsule
