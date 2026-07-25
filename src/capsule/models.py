from dataclasses import dataclass, field, asdict
from typing import Dict, Any, Optional

@dataclass
class PolicyMetadata:
    classification: str = "CONFIDENTIAL"
    jurisdiction: str = "UK"
    max_hops: int = 3
    allowed_channels: list[str] = field(default_factory=lambda: ["HTTPS", "KAFKA", "MQ", "SWIFT"])

@dataclass
class QuantumSecurityCapsule:
    version: str
    capsule_id: str
    issued_at: str
    expires_at: str
    replay_token: str
    sender_id: str
    recipient_id: str
    kem_ciphertext: str
    payload_ciphertext: str
    payload_tag: str
    nonce: str
    integrity_hash: str
    signature: str
    policy: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        """Converts capsule to dictionary."""
        return asdict(self)

    def get_canonical_fields(self) -> Dict[str, Any]:
        """
        Returns fields included in the integrity hash computation.
        Excludes signature and integrity_hash itself to prevent circularity.
        """
        d = self.to_dict()
        d.pop("signature", None)
        d.pop("integrity_hash", None)
        return d
