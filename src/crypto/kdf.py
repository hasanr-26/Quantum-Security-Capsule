"""
Key derivation for the Quantum Security Capsule.

NIST SP 800-56C Rev. 2 requires that a shared secret produced by a key
establishment scheme be passed through an approved KDF before use as a working
key. The raw ML-KEM shared secret is therefore never used directly as the
AES-256-GCM content key.
"""

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF

# Domain separation string. Binds derived keys to this protocol version so the
# same KEM secret can never be repurposed by another scheme.
QSC_PAYLOAD_KEY_INFO = b"QSC-1.0 ML-KEM-768 -> AES-256-GCM payload key"

AES_256_KEY_BYTES = 32


def derive_payload_key(
    shared_secret: bytes,
    capsule_id: str,
    info: bytes = QSC_PAYLOAD_KEY_INFO,
) -> bytes:
    """
    Derives the AES-256-GCM content key from the ML-KEM shared secret.

    HKDF-SHA3-512 (extract-then-expand) with the capsule identifier as salt, so
    two capsules that somehow shared a KEM secret would still derive unrelated
    content keys.

    Args:
        shared_secret: 32-byte secret from ML-KEM-768 encapsulation/decapsulation.
        capsule_id: Unique capsule identifier, used as the HKDF salt.
        info: Domain separation context string.

    Returns:
        32-byte AES-256 key.
    """
    return HKDF(
        algorithm=hashes.SHA3_512(),
        length=AES_256_KEY_BYTES,
        salt=capsule_id.encode("utf-8"),
        info=info,
    ).derive(shared_secret)
