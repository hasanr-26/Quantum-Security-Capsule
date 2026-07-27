import http.server
import socketserver
import json
import os
import sys
import base64
import time
from typing import Dict, Any, List

# Ensure parent directory is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.crypto import (
    MLKEM768,
    MLDSA65,
    compute_sha3_512,
    canonicalize_json,
    decrypt_aes_256_gcm
)
from src.utils import get_utc_now, parse_iso8601
from src.capsule import CapsuleBuilder, SecureReceiver, PolicyMetadata, QuantumSecurityCapsule
from src.capsule.validator import CapsuleValidator

# Persistent state for the visualizer session
SESSION = {
    "sender_dsa_pub": None,
    "sender_dsa_priv": None,
    "receiver_kem_pub": None,
    "receiver_kem_priv": None,
    "receiver": None,
    "last_capsule": None,
    "last_payload_bytes": None,
    "sender_id": "barclays-mobile-client-0091",
    "recipient_id": "barclays-core-settlement-engine"
}

def init_keys():
    """Initializes cryptographic keypairs for demo session."""
    sender_pub, sender_priv = MLDSA65.generate_keypair()
    receiver_pub, receiver_priv = MLKEM768.generate_keypair()
    
    SESSION["sender_dsa_pub"] = sender_pub
    SESSION["sender_dsa_priv"] = sender_priv
    SESSION["receiver_kem_pub"] = receiver_pub
    SESSION["receiver_kem_priv"] = receiver_priv
    SESSION["receiver"] = SecureReceiver(SESSION["recipient_id"], receiver_priv)

init_keys()

class QSCVisualizerHandler(http.server.SimpleHTTPRequestHandler):

    def do_GET(self):
        if self.path == "/" or self.path == "/index.html":
            html_path = os.path.join(os.path.dirname(__file__), "index.html")
            if os.path.exists(html_path):
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.end_headers()
                with open(html_path, "rb") as f:
                    self.wfile.write(f.read())
                return
            else:
                self.send_error(404, "index.html not found")
                return
        
        elif self.path == "/api/status":
            self._send_json({
                "status": "online",
                "sender_dsa_pub_size": len(SESSION["sender_dsa_pub"]),
                "receiver_kem_pub_size": len(SESSION["receiver_kem_pub"]),
                "sender_id": SESSION["sender_id"],
                "recipient_id": SESSION["recipient_id"]
            })
            return

        elif self.path == "/api/replay_cache":
            seen_tokens = getattr(SESSION["receiver"].validator, "_seen_replay_tokens", set())
            items = []
            for token in seen_tokens:
                items.append({
                    "replay_token": token[:32] + "...",
                    "full_token": token,
                    "expires_at": "Session Register"
                })
            self._send_json({"count": len(items), "tokens": items})
            return

        super().do_GET()

    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length) if content_length > 0 else b"{}"
        try:
            req_data = json.loads(body.decode('utf-8'))
        except Exception:
            req_data = {}

        if self.path == "/api/reset_keys":
            init_keys()
            self._send_json({"message": "Keypairs regenerated successfully!"})
            return

        elif self.path == "/api/build_capsule":
            start_time = time.perf_counter()

            sender_id = req_data.get("sender_id", SESSION["sender_id"])
            recipient_id = req_data.get("recipient_id", SESSION["recipient_id"])
            payload_str = req_data.get("payload", '{"transaction_id": "TXN-99182", "amount": 50000.0, "currency": "INR"}')
            validity = int(req_data.get("validity_seconds", 300))
            classification = req_data.get("classification", "RESTRICTED_FINANCIAL")
            jurisdiction = req_data.get("jurisdiction", "UK_IN")

            payload_bytes = payload_str.encode('utf-8')
            SESSION["last_payload_bytes"] = payload_bytes
            SESSION["sender_id"] = sender_id
            SESSION["recipient_id"] = recipient_id

            if SESSION["receiver"].recipient_id != recipient_id:
                SESSION["receiver"] = SecureReceiver(recipient_id, SESSION["receiver_kem_priv"])

            builder = CapsuleBuilder(sender_id, SESSION["sender_dsa_priv"])
            policy = PolicyMetadata(classification=classification, jurisdiction=jurisdiction, max_hops=2)

            capsule = builder.build_capsule(
                recipient_id=recipient_id,
                recipient_public_kem_key=SESSION["receiver_kem_pub"],
                payload=payload_bytes,
                validity_seconds=validity,
                policy=policy
            )

            SESSION["last_capsule"] = capsule
            elapsed_ms = round((time.perf_counter() - start_time) * 1000, 3)

            # Generate intermediate stage trace info
            canonical_bytes = canonicalize_json(capsule.get_canonical_fields())
            intermediate_trace = {
                "step_1_ml_kem_768": {
                    "public_key_len": f"{len(SESSION['receiver_kem_pub'])} bytes",
                    "ciphertext_len": f"{len(base64.b64decode(capsule.kem_ciphertext))} bytes",
                    "kem_ciphertext_b64_preview": capsule.kem_ciphertext[:32] + "..."
                },
                "step_2_aes_256_gcm": {
                    "nonce_len": f"{len(base64.b64decode(capsule.nonce))} bytes",
                    "tag_len": f"{len(base64.b64decode(capsule.payload_tag))} bytes",
                    "ciphertext_b64_preview": capsule.payload_ciphertext[:32] + "..."
                },
                "step_3_sha3_512": {
                    "canonical_bytes_len": f"{len(canonical_bytes)} bytes",
                    "canonical_sample": canonical_bytes.decode('utf-8', errors='ignore')[:64] + "...",
                    "digest_hex": capsule.integrity_hash
                },
                "step_4_ml_dsa_65": {
                    "private_key_len": f"{len(SESSION['sender_dsa_priv'])} bytes",
                    "signature_len": f"{len(base64.b64decode(capsule.signature))} bytes",
                    "signature_b64_preview": capsule.signature[:32] + "..."
                }
            }

            self._send_json({
                "success": True,
                "elapsed_ms": elapsed_ms,
                "capsule": capsule.to_dict(),
                "trace": intermediate_trace,
                "keys_info": {
                    "sender_dsa_pub_hex": SESSION["sender_dsa_pub"][:32].hex() + "...",
                    "receiver_kem_pub_hex": SESSION["receiver_kem_pub"][:32].hex() + "..."
                }
            })
            return

        elif self.path == "/api/verify_capsule":
            if not SESSION["last_capsule"]:
                self._send_json({"success": False, "message": "No capsule built yet!"})
                return

            start_time = time.perf_counter()
            capsule = SESSION["last_capsule"]
            
            success, decrypted, msg = SESSION["receiver"].process_and_decrypt(
                capsule,
                SESSION["sender_dsa_pub"]
            )
            elapsed_ms = round((time.perf_counter() - start_time) * 1000, 3)

            self._send_json({
                "success": success,
                "status_message": msg,
                "decrypted_payload": decrypted.decode('utf-8', errors='ignore') if success else None,
                "elapsed_ms": elapsed_ms
            })
            return

        elif self.path == "/api/verify_raw_packet":
            raw_str = req_data.get("raw_json", "")
            if not raw_str:
                self._send_json({"success": False, "message": "Empty raw packet JSON string!"})
                return

            start_time = time.perf_counter()
            diagnostic_steps = []

            try:
                packet_dict = json.loads(raw_str)
                capsule = QuantumSecurityCapsule(**packet_dict)
            except Exception as e:
                self._send_json({
                    "success": False,
                    "parse_error": True,
                    "message": f"JSON Syntax Error: {str(e)}",
                    "diagnostic_steps": [{
                        "name": "1. JSON Schema Deserialization",
                        "passed": False,
                        "details": f"Failed to parse raw text into QuantumSecurityCapsule model: {str(e)}"
                    }]
                })
                return

            diagnostic_steps.append({
                "name": "1. JSON Wire Deserialization",
                "passed": True,
                "details": f"Capsule ID '{capsule.capsule_id}' successfully parsed into data structure."
            })

            # Step 2: Live SHA3-512 Digest Re-computation over incoming raw fields
            canonical_bytes = canonicalize_json(capsule.get_canonical_fields())
            computed_sha3 = compute_sha3_512(canonical_bytes)
            sha3_match = (computed_sha3 == capsule.integrity_hash)

            diagnostic_steps.append({
                "name": "2. Live SHA3-512 Integrity Check",
                "passed": sha3_match,
                "details": f"Provided SHA3: {capsule.integrity_hash[:32]}...\nComputed SHA3: {computed_sha3[:32]}...",
                "canonical_bytes_preview": canonical_bytes.decode('utf-8', errors='ignore')[:80] + "..."
            })

            # Step 3: ML-DSA-65 Signature Verification over compute_sha3
            sig_valid = False
            try:
                sig_bytes = base64.b64decode(capsule.signature)
                sig_valid = MLDSA65.verify(SESSION["sender_dsa_pub"], capsule.integrity_hash, sig_bytes)
            except Exception as e:
                sig_valid = False

            diagnostic_steps.append({
                "name": "3. ML-DSA-65 Lattice Signature Check",
                "passed": sig_valid,
                "details": f"Verified ML-DSA-65 signature against sender '{capsule.sender_id}' public key ({len(SESSION['sender_dsa_pub'])} bytes)." if sig_valid else "Signature verification failed! Signature lattice mismatch or rogue public key."
            })

            # Step 4: Replay Cache & Expiration Check
            now = get_utc_now()
            exp_time = parse_iso8601(capsule.expires_at)
            not_expired = (now <= exp_time)
            
            seen_tokens = getattr(SESSION["receiver"].validator, "_seen_replay_tokens", set())
            is_replayed = (capsule.replay_token in seen_tokens)

            diagnostic_steps.append({
                "name": "4. Replay Cache & Validity Window",
                "passed": (not_expired and not is_replayed),
                "details": f"Replay Token: {capsule.replay_token[:32]}... | Status: {'CONSUMED (Replay Detected!)' if is_replayed else 'FRESH'}\nExpires At: {capsule.expires_at} | Current: {now.isoformat()}"
            })

            # Full Receiver Evaluation
            success, decrypted, msg = SESSION["receiver"].process_and_decrypt(
                capsule,
                SESSION["sender_dsa_pub"]
            )
            elapsed_ms = round((time.perf_counter() - start_time) * 1000, 3)

            diagnostic_steps.append({
                "name": "5. ML-KEM-768 Decapsulation & AES-256-GCM Decryption",
                "passed": success,
                "details": msg
            })

            self._send_json({
                "success": success,
                "status_message": msg,
                "decrypted_payload": decrypted.decode('utf-8', errors='ignore') if success else None,
                "diagnostic_steps": diagnostic_steps,
                "elapsed_ms": elapsed_ms
            })
            return

        elif self.path == "/api/simulate_attack":
            if not SESSION["last_capsule"]:
                self._send_json({"success": False, "message": "No active capsule to attack!"})
                return

            attack_type = req_data.get("attack_type")
            orig_capsule = SESSION["last_capsule"]

            if attack_type == "tamper":
                ct = orig_capsule.payload_ciphertext
                tampered_ct = ct[:-2] + ("AA" if ct[-2:] != "AA" else "BB")
                
                tampered_capsule = QuantumSecurityCapsule(
                    **{**orig_capsule.to_dict(), "payload_ciphertext": tampered_ct}
                )
                
                fresh_receiver = SecureReceiver(SESSION["recipient_id"], SESSION["receiver_kem_priv"])
                success, decrypted, msg = fresh_receiver.process_and_decrypt(
                    tampered_capsule, SESSION["sender_dsa_pub"]
                )
                self._send_json({
                    "attack_name": "Ciphertext Tampering",
                    "attack_desc": "Modified 1 byte in the AES-256-GCM encrypted payload in transit",
                    "success": success,
                    "status_message": msg,
                    "blocked": not success
                })

            elif attack_type == "replay":
                success, decrypted, msg = SESSION["receiver"].process_and_decrypt(
                    orig_capsule, SESSION["sender_dsa_pub"]
                )
                self._send_json({
                    "attack_name": "Replay Attack",
                    "attack_desc": "Re-sent the exact same capsule replay token to the settlement receiver",
                    "success": success,
                    "status_message": msg,
                    "blocked": not success
                })

            elif attack_type == "forgery":
                rogue_pub, rogue_priv = MLDSA65.generate_keypair()
                fresh_receiver = SecureReceiver(SESSION["recipient_id"], SESSION["receiver_kem_priv"])
                
                success, decrypted, msg = fresh_receiver.process_and_decrypt(
                    orig_capsule, rogue_pub
                )
                self._send_json({
                    "attack_name": "Signature Forgery / Key Spoofing",
                    "attack_desc": "Attempted validation with an unverified rogue public key",
                    "success": success,
                    "status_message": msg,
                    "blocked": not success
                })

            elif attack_type == "expired":
                expired_capsule = QuantumSecurityCapsule(
                    **{**orig_capsule.to_dict(), "expires_at": "2020-01-01T00:00:00Z"}
                )
                fresh_receiver = SecureReceiver(SESSION["recipient_id"], SESSION["receiver_kem_priv"])
                success, decrypted, msg = fresh_receiver.process_and_decrypt(
                    expired_capsule, SESSION["sender_dsa_pub"]
                )
                self._send_json({
                    "attack_name": "Expired TTL Violation",
                    "attack_desc": "Capsule timestamp expired prior to processing",
                    "success": success,
                    "status_message": msg,
                    "blocked": not success
                })
            else:
                self._send_json({"success": False, "message": "Unknown attack type"})
            return

        self.send_error(404, "Endpoint not found")

    def _send_json(self, data: Dict[str, Any], status=200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2).encode('utf-8'))

def run(port=8000):
    server_address = ('', port)
    httpd = socketserver.TCPServer(server_address, QSCVisualizerHandler)
    print(f"======================================================================")
    print(f" BARCLAYS INNOVATION LAB - QUANTUM SECURITY CAPSULE WORKBENCH")
    print(f" Running live server at http://localhost:{port}")
    print(f"======================================================================")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down QSC Visualizer server.")
        httpd.server_close()

if __name__ == "__main__":
    port = 8000
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            pass
    run(port)
