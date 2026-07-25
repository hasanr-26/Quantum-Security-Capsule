import hashlib
import json

def compute_sha3_512(data: bytes) -> str:
    """Computes SHA3-512 hex digest for given bytes."""
    return hashlib.sha3_512(data).hexdigest()

def canonicalize_json(data: dict) -> bytes:
    """Returns canonical UTF-8 JSON representation for deterministic hashing."""
    return json.dumps(data, sort_keys=True, separators=(',', ':')).encode('utf-8')
