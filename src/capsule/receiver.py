import base64
from typing import Tuple

from src.crypto import (
    decrypt_aes_256_gcm,
    MLKEM768
)
from src.capsule.models import QuantumSecurityCapsule
from src.capsule.validator import CapsuleValidator

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

    def process_and_decrypt(
        self,
        capsule: QuantumSecurityCapsule,
        sender_public_dsa_key: bytes
    ) -> Tuple[bool, bytes, str]:
        """
        Processes an incoming capsule:
        1. Validates capsule via CapsuleValidator.
        2. Decapsulates ML-KEM shared secret using recipient private KEM key.
        3. Decrypts AES-256-GCM payload.
        
        Returns (success, decrypted_payload_bytes, status_message).
        """
        # Step 1: Enforce complete validation
        is_valid, reason = self.validator.validate_capsule(capsule, sender_public_dsa_key)
        if not is_valid:
            return False, b"", f"Receiver rejected capsule: {reason}"

        # Step 2: Recipient check
        if capsule.recipient_id != self.recipient_id:
            return False, b"", f"Recipient mismatch: Expected {self.recipient_id}, got {capsule.recipient_id}"

        try:
            # Step 3: Decapsulate ML-KEM shared secret
            kem_ct_bytes = base64.b64decode(capsule.kem_ciphertext)
            shared_secret = MLKEM768.decapsulate(
                private_key=self.recipient_private_kem_key,
                ciphertext=kem_ct_bytes
            )

            # Step 4: AES-256-GCM Decryption
            ciphertext_bytes = base64.b64decode(capsule.payload_ciphertext)
            nonce_bytes = base64.b64decode(capsule.nonce)
            tag_bytes = base64.b64decode(capsule.payload_tag)

            plaintext = decrypt_aes_256_gcm(
                key=shared_secret,
                ciphertext=ciphertext_bytes,
                nonce=nonce_bytes,
                tag=tag_bytes,
                associated_data=capsule.capsule_id.encode('utf-8')
            )
            return True, plaintext, "Capsule validated and payload decrypted successfully."

        except Exception as e:
            return False, b"", f"Cryptographic decryption failed: {str(e)}"
