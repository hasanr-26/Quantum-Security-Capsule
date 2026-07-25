import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

def generate_symmetric_key() -> bytes:
    """Generates a 256-bit (32-byte) key for AES-256-GCM."""
    return AESGCM.generate_key(bit_length=256)

def encrypt_aes_256_gcm(key: bytes, plaintext: bytes, associated_data: bytes = None) -> tuple[bytes, bytes, bytes]:
    """
    Encrypts plaintext using AES-256-GCM.
    Returns (ciphertext_with_tag, nonce, tag).
    """
    aesgcm = AESGCM(key)
    nonce = os.urandom(12)  # 96-bit IV standard for GCM
    ct_tag = aesgcm.encrypt(nonce, plaintext, associated_data)
    ciphertext = ct_tag[:-16]
    tag = ct_tag[-16:]
    return ciphertext, nonce, tag

def decrypt_aes_256_gcm(key: bytes, ciphertext: bytes, nonce: bytes, tag: bytes, associated_data: bytes = None) -> bytes:
    """
    Decrypts ciphertext using AES-256-GCM with authentication tag.
    Raises InvalidSignature if tampered.
    """
    aesgcm = AESGCM(key)
    ct_tag = ciphertext + tag
    return aesgcm.decrypt(nonce, ct_tag, associated_data)
