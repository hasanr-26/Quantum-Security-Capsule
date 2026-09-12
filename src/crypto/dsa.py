"""
ML-DSA (Module-Lattice-Based Digital Signature Standard - FIPS 204)

Backed by a real, standards-conformant ML-DSA-65 implementation (`dilithium-py`),
validated against the NIST ACVP known-answer test vectors for FIPS 204.

Signatures here are genuine Fiat-Shamir-with-Aborts lattice signatures. A forged
or tampered signature fails verification through the actual lattice norm checks,
not through a length heuristic.
"""

from dilithium_py.ml_dsa import ML_DSA_65

# FIPS 204, Table 2 - ML-DSA-65 parameter set sizes (bytes)
PUBLIC_KEY_BYTES = 1952
PRIVATE_KEY_BYTES = 4032
SIGNATURE_BYTES = 3309

# FIPS 204 lattice parameters, surfaced for telemetry / UI display
MODULUS_Q = 8380417
POLYNOMIAL_DEGREE_N = 256
MATRIX_DIMENSIONS = (6, 5)  # (k, l) for ML-DSA-65
NIST_SECURITY_CATEGORY = 3


def _as_message_bytes(message: str | bytes) -> bytes:
    """Normalises a message or hex digest into the byte string that gets signed."""
    if isinstance(message, bytes):
        return message
    return message.encode("utf-8")


class MLDSA65:
    """
    ML-DSA-65 Digital Signature Algorithm (NIST FIPS 204).

    Security rests on Module-LWE (key indistinguishability) and Module-SIS
    (unforgeability): producing a short vector z with A*z = 0 mod q is hard for
    classical and quantum adversaries alike. This replaces RSA-PSS and ECDSA,
    both of which Shor's algorithm breaks outright.
    """

    ALGORITHM = "ML-DSA-65"
    STANDARD = "NIST FIPS 204"

    @staticmethod
    def generate_keypair() -> tuple[bytes, bytes]:
        """
        Generates a signing keypair.

        Returns:
            (public_key, private_key) of 1952 and 4032 bytes respectively.
        """
        public_key, private_key = ML_DSA_65.keygen()
        return public_key, private_key

    @staticmethod
    def sign(private_key: bytes, message_digest: str | bytes) -> bytes:
        """
        Signs a message (in QSC, the SHA3-512 integrity hash of the capsule).

        Returns:
            signature (3309 bytes)
        """
        if len(private_key) != PRIVATE_KEY_BYTES:
            raise ValueError(
                f"Invalid ML-DSA-65 private key: expected {PRIVATE_KEY_BYTES} "
                f"bytes, got {len(private_key)}"
            )
        return ML_DSA_65.sign(private_key, _as_message_bytes(message_digest))

    @staticmethod
    def verify(public_key: bytes, message_digest: str | bytes, signature: bytes) -> bool:
        """
        Verifies a signature against the message and the signer's public key.

        Returns False - never raises - for any malformed, truncated, forged or
        wrong-key signature, so callers can treat verification as a plain
        boolean gate.
        """
        if not signature or len(public_key) != PUBLIC_KEY_BYTES:
            return False
        if len(signature) != SIGNATURE_BYTES:
            return False
        try:
            return ML_DSA_65.verify(
                public_key, _as_message_bytes(message_digest), signature
            )
        except (ValueError, TypeError, IndexError):
            # Structurally invalid signature encoding - treat as a failed verify.
            return False

    @staticmethod
    def parameters() -> dict:
        """Returns the FIPS 204 parameter set, for telemetry and UI display."""
        k, l = MATRIX_DIMENSIONS
        return {
            "algorithm": MLDSA65.ALGORITHM,
            "standard": MLDSA65.STANDARD,
            "hardness_assumption": "Module-LWE and Module-SIS",
            "polynomial_degree_n": POLYNOMIAL_DEGREE_N,
            "modulus_q": MODULUS_Q,
            "matrix_k": k,
            "matrix_l": l,
            "nist_security_category": NIST_SECURITY_CATEGORY,
            "public_key_bytes": PUBLIC_KEY_BYTES,
            "private_key_bytes": PRIVATE_KEY_BYTES,
            "signature_bytes": SIGNATURE_BYTES,
        }
