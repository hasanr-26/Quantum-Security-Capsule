import http.server
import socketserver
import json
import os
import sys
import base64
import time
from typing import Dict, Any

# Ensure parent directory is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.crypto import MLKEM768, MLDSA65
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

            # Update receiver if recipient_id changed
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

            self._send_json({
                "success": True,
                "elapsed_ms": elapsed_ms,
                "capsule": capsule.to_dict(),
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

        elif self.path == "/api/simulate_attack":
            if not SESSION["last_capsule"]:
                self._send_json({"success": False, "message": "No active capsule to attack!"})
                return

            attack_type = req_data.get("attack_type")
            orig_capsule = SESSION["last_capsule"]

            if attack_type == "tamper":
                # Modify payload ciphertext
                ct = orig_capsule.payload_ciphertext
                tampered_ct = ct[:-2] + ("AA" if ct[-2:] != "AA" else "BB")
                
                tampered_capsule = QuantumSecurityCapsule(
                    **{**orig_capsule.to_dict(), "payload_ciphertext": tampered_ct}
                )
                
                # Fresh receiver to bypass replay check
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
                # Re-send the exact same capsule to the existing receiver session
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
                # Rogue key forgery
                rogue_pub, rogue_priv = MLDSA65.generate_keypair()
                fresh_receiver = SecureReceiver(SESSION["recipient_id"], SESSION["receiver_kem_priv"])
                
                # Pass capsule signed by rogue key, but receiver checks against legitimate sender pub key
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
                # Past expiration
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
