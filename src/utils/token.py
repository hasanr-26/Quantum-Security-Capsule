import uuid
import hashlib

def generate_capsule_id() -> str:
    """Generates a globally unique UUID v4 identifier."""
    return f"qsc_{uuid.uuid4().hex}"

def generate_replay_token(capsule_id: str, issued_at: str, sender_id: str, nonce: str) -> str:
    """
    Computes a cryptographic replay prevention token using SHA3-512.
    Combines capsule_id, timestamp, sender identity, and AES nonce.
    """
    raw_bind = f"{capsule_id}:{issued_at}:{sender_id}:{nonce}".encode('utf-8')
    return hashlib.sha3_512(raw_bind).hexdigest()
