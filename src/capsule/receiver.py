import base64
from typing import Tuple

from src.crypto import (
    decrypt_aes_256_gcm,
    derive_payload_key,
    MLKEM768
)
from src.capsule.models import QuantumSecurityCapsule
from src.capsule.validator import CapsuleValidator, ValidationReport

class SecureReceiver:
    """
    Secure Receiver component in the QSC architecture.
    Refuses to decrypt payload unless CapsuleValidator verifies 100% of security constraints.
    """

    def __init__(
        self,
        recipient_id: str,
        recipient_private_kem_key: bytes,
        validator: CapsuleValidator = None
    ):
        self.recipient_id = recipient_id
        self.recipient_private_kem_key = recipient_private_kem_key
        self.validator = validator or CapsuleValidator()

    def decrypt_payload(self, capsule: QuantumSecurityCapsule) -> Tuple[bool, bytes, str]:
        """
        Performs the cryptographic recovery steps for an already-validated capsule.

        Callers must have run the validation pipeline first - this method
        deliberately performs no policy checks of its own. It exists so that a
        caller holding a validation report (and therefore already having
        consumed the replay token) can decrypt without triggering a second,
        self-inflicted replay rejection.

        Steps:
        1. Decapsulate the ML-KEM-768 shared secret with the recipient private key.
        2. Re-derive the AES content key via HKDF-SHA3-512.
        3. Decrypt and authenticate the payload with AES-256-GCM.
        """
        try:
            kem_ct_bytes = base64.b64decode(capsule.kem_ciphertext)
            shared_secret = MLKEM768.decapsulate(
                private_key=self.recipient_private_kem_key,
                ciphertext=kem_ct_bytes
            )

            content_key = derive_payload_key(shared_secret, capsule.capsule_id)

            plaintext = decrypt_aes_256_gcm(
                key=content_key,
                ciphertext=base64.b64decode(capsule.payload_ciphertext),
                nonce=base64.b64decode(capsule.nonce),
                tag=base64.b64decode(capsule.payload_tag),
                associated_data=capsule.capsule_id.encode('utf-8')
            )
            return True, plaintext, "Capsule validated and payload decrypted successfully."

        except Exception as e:
            return False, b"", f"Cryptographic decryption failed: {str(e)}"

    def process_and_decrypt(
        self,
        capsule: QuantumSecurityCapsule,
        sender_public_dsa_key: bytes
    ) -> Tuple[bool, bytes, str]:
        """
        Processes an incoming capsule end to end:
        1. Validates the capsule via CapsuleValidator (all five stages).
        2. Confirms this node is the intended recipient.
        3. Decapsulates, derives the content key, and decrypts the payload.

        Returns (success, decrypted_payload_bytes, status_message).
        """
        # Step 1: Enforce complete validation
        is_valid, reason = self.validator.validate_capsule(capsule, sender_public_dsa_key)
        if not is_valid:
            return False, b"", f"Receiver rejected capsule: {reason}"

        # Step 2: Recipient check
        if capsule.recipient_id != self.recipient_id:
            return False, b"", f"Recipient mismatch: Expected {self.recipient_id}, got {capsule.recipient_id}"

        # Step 3: Cryptographic recovery
        return self.decrypt_payload(capsule)

    def settle_with_report(
        self,
        capsule: QuantumSecurityCapsule,
        sender_public_dsa_key: bytes
    ) -> Tuple[ValidationReport, bytes]:
        """
        Validates and decrypts in one pass, returning the full stage trace.

        Returns (report, plaintext). On rejection the plaintext is empty and the
        report explains which control stopped the capsule.
        """
        report = self.validator.validate_detailed(capsule, sender_public_dsa_key)
        if not report.accepted:
            return report, b""

        if capsule.recipient_id != self.recipient_id:
            report.accepted = False
            report.reason = (
                f"Recipient mismatch: Expected {self.recipient_id}, "
                f"got {capsule.recipient_id}"
            )
            return report, b""

        ok, plaintext, message = self.decrypt_payload(capsule)
        if not ok:
            report.accepted = False
            report.reason = message
            return report, b""

        return report, plaintext
