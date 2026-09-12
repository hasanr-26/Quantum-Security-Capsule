"""
ML-KEM (Module-Lattice-Based Key-Encapsulation Mechanism Standard - FIPS 203)

Backed by a real, standards-conformant ML-KEM-768 implementation (`kyber-py`),
which is validated against the NIST ACVP known-answer test vectors for FIPS 203.

Nothing in this module fabricates key material: every byte returned by
`encapsulate` is produced by the genuine Kyber/ML-KEM lattice arithmetic over
R_q = Z_q[X]/(X^256 + 1) with q = 3329 and module rank k = 3.
"""

from kyber_py.ml_kem import ML_KEM_768

# FIPS 203, Table 2 - ML-KEM-768 parameter set sizes (bytes)
ENCAPSULATION_KEY_BYTES = 1184
DECAPSULATION_KEY_BYTES = 2400
CIPHERTEXT_BYTES = 1088
SHARED_SECRET_BYTES = 32

# FIPS 203 lattice parameters, surfaced for telemetry / UI display
LATTICE_DIMENSION_N = 256
MODULUS_Q = 3329
MODULE_RANK_K = 3
NIST_SECURITY_CATEGORY = 3


class MLKEM768:
    """
    ML-KEM-768 Key Encapsulation Mechanism (NIST FIPS 203).

    Security rests on the hardness of Module Learning With Errors (M-LWE):
    recovering s from (A, A*s + e mod q) where e is a short error vector.
    No known quantum algorithm solves this in polynomial time - Shor's
    algorithm does not apply, as there is no hidden-subgroup structure.
    """

    ALGORITHM = "ML-KEM-768"
    STANDARD = "NIST FIPS 203"

    @staticmethod
    def generate_keypair() -> tuple[bytes, bytes]:
        """
        Generates an (encapsulation_key, decapsulation_key) pair.

        Returns:
            (public_key, private_key) of 1184 and 2400 bytes respectively.
        """
        encapsulation_key, decapsulation_key = ML_KEM_768.keygen()
        return encapsulation_key, decapsulation_key

    @staticmethod
    def encapsulate(public_key: bytes) -> tuple[bytes, bytes]:
        """
        Encapsulates a fresh shared secret against the recipient's public key.

        The shared secret is derived inside the lattice operation and is
        recoverable only by the holder of the matching decapsulation key.

        Returns:
            (shared_secret_32_bytes, ciphertext_1088_bytes)
        """
        if len(public_key) != ENCAPSULATION_KEY_BYTES:
            raise ValueError(
                f"Invalid ML-KEM-768 encapsulation key: expected "
                f"{ENCAPSULATION_KEY_BYTES} bytes, got {len(public_key)}"
            )
        shared_secret, ciphertext = ML_KEM_768.encaps(public_key)
        return shared_secret, ciphertext

    @staticmethod
    def decapsulate(private_key: bytes, ciphertext: bytes) -> bytes:
        """
        Recovers the shared secret from the KEM ciphertext.

        Note on FIPS 203 implicit rejection: a tampered or forged ciphertext
        does NOT raise. ML-KEM deliberately returns a deterministic pseudo-random
        secret derived from the private key's rejection seed, so an attacker
        cannot distinguish "wrong key" from "malformed ciphertext" by timing or
        error behaviour. The resulting secret simply will not decrypt the
        payload, and AES-256-GCM tag verification then fails closed.

        Returns:
            shared_secret (32 bytes)
        """
        if len(private_key) != DECAPSULATION_KEY_BYTES:
            raise ValueError(
                f"Invalid ML-KEM-768 decapsulation key: expected "
                f"{DECAPSULATION_KEY_BYTES} bytes, got {len(private_key)}"
            )
        if len(ciphertext) != CIPHERTEXT_BYTES:
            raise ValueError(
                f"Invalid ML-KEM-768 ciphertext: expected "
                f"{CIPHERTEXT_BYTES} bytes, got {len(ciphertext)}"
            )
        return ML_KEM_768.decaps(private_key, ciphertext)

    @staticmethod
    def parameters() -> dict:
        """Returns the FIPS 203 parameter set, for telemetry and UI display."""
        return {
            "algorithm": MLKEM768.ALGORITHM,
            "standard": MLKEM768.STANDARD,
            "hardness_assumption": "Module Learning With Errors (M-LWE)",
            "polynomial_degree_n": LATTICE_DIMENSION_N,
            "modulus_q": MODULUS_Q,
            "module_rank_k": MODULE_RANK_K,
            "nist_security_category": NIST_SECURITY_CATEGORY,
            "public_key_bytes": ENCAPSULATION_KEY_BYTES,
            "private_key_bytes": DECAPSULATION_KEY_BYTES,
            "ciphertext_bytes": CIPHERTEXT_BYTES,
            "shared_secret_bytes": SHARED_SECRET_BYTES,
        }
