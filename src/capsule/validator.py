import base64
from typing import Set, Tuple, Dict, Any

from src.crypto import (
    compute_sha3_512,
    canonicalize_json,
    MLDSA65
)
from src.utils import is_expired
from src.capsule.models import QuantumSecurityCapsule

class CapsuleValidator:
    """
    Validates Quantum Security Capsules before decryption.
    Verifies:
    1. Version match & schema integrity
    2. Expiry & freshness timestamps
    3. Replay protection token presence in replay cache
    4. Deterministic SHA3-512 integrity hash
    5. Post-Quantum ML-DSA-65 digital signature against sender's public key
    """

    def __init__(self):
        # Replay protection store (In-memory registry; production would use Redis / Distributed KV)
        self._seen_replay_tokens: Set[str] = set()

    def validate_capsule(
        self,
        capsule: QuantumSecurityCapsule,
        sender_public_dsa_key: bytes
    ) -> Tuple[bool, str]:
        """
        Runs complete 5-stage validation pipeline.
        Returns (is_valid, reason).
        """
        # 1. Version Check
        if capsule.version != "QSC-1.0":
            return False, f"Unsupported QSC version: {capsule.version}"

        # 2. Timestamp & Expiry Check
        if is_expired(capsule.expires_at):
            return False, f"Capsule expired at {capsule.expires_at}"

        # 3. Replay Protection Check
        if capsule.replay_token in self._seen_replay_tokens:
            return False, f"Replay attack detected! Token {capsule.replay_token[:16]}... already consumed."

        # 4. Integrity Lock Verification (SHA3-512)
        canonical_bytes = canonicalize_json(capsule.get_canonical_fields())
        computed_hash = compute_sha3_512(canonical_bytes)
        if computed_hash != capsule.integrity_hash:
            return False, "Integrity Lock failure: Capsule contents modified in transit."

        # 5. PQC Digital Signature Verification (ML-DSA-65)
        try:
            signature_bytes = base64.b64decode(capsule.signature)
        except Exception:
            return False, "Malformed signature encoding."

        is_sig_valid = MLDSA65.verify(
            public_key=sender_public_dsa_key,
            message_digest=capsule.integrity_hash,
            signature=signature_bytes
        )
        if not is_sig_valid:
            return False, "Digital Signature Verification failed: Invalid ML-DSA signature."

        # Register replay token upon successful validation
        self._seen_replay_tokens.add(capsule.replay_token)
        return True, "Validation successful"
