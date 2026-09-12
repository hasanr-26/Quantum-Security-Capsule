import pytest
import json
import io
from src.visualizer.app import QSCVisualizerHandler, SESSION, init_keys

class DummyWFile:
    """Mock wfile output for HTTP handler testing."""
    def __init__(self):
        self.buffer = io.BytesIO()

    def write(self, data):
        self.buffer.write(data)

    def getvalue(self):
        return self.buffer.getvalue()

def call_handler(method, path, body_dict=None):
    """Helper to invoke QSCVisualizerHandler without spawning a network socket."""
    handler = QSCVisualizerHandler.__new__(QSCVisualizerHandler)
    handler.path = path
    handler.headers = {}
    handler.wfile = DummyWFile()
    
    # Mock send_response, send_header, end_headers
    handler.response_code = 200
    handler.response_headers = {}

    def mock_send_response(code, message=None):
        handler.response_code = code

    def mock_send_header(keyword, value):
        handler.response_headers[keyword] = value

    def mock_end_headers():
        pass

    handler.send_response = mock_send_response
    handler.send_header = mock_send_header
    handler.end_headers = mock_end_headers

    if method == "GET":
        handler.do_GET()
    elif method == "POST":
        body_bytes = json.dumps(body_dict or {}).encode('utf-8')
        handler.rfile = io.BytesIO(body_bytes)
        handler.headers['Content-Length'] = str(len(body_bytes))
        handler.do_POST()

    raw_output = handler.wfile.getvalue()
    # Extract JSON response payload
    if b"\r\n\r\n" in raw_output:
        json_bytes = raw_output.split(b"\r\n\r\n", 1)[1]
    else:
        json_bytes = raw_output

    try:
        return json.loads(json_bytes.decode('utf-8'))
    except Exception:
        return {}

def test_api_status_endpoint():
    init_keys()
    res = call_handler("GET", "/api/status")
    assert res.get("status") == "online"
    assert res.get("sender_id") == "barclays-mobile-client-0091"

def test_api_build_and_verify_capsule():
    init_keys()
    # 1. Build Capsule via API
    build_req = {
        "sender_id": "alice-test",
        "recipient_id": "bob-test",
        "payload": json.dumps({"action": "TRANSFER", "amount": 10000.0, "currency": "GBP"}),
        "validity_seconds": 300
    }
    build_res = call_handler("POST", "/api/build_capsule", build_req)
    assert build_res.get("success") is True
    assert "capsule" in build_res
    assert build_res["capsule"]["sender_id"] == "alice-test"

    # 2. Verify Capsule via API
    verify_res = call_handler("POST", "/api/verify_capsule", {})
    assert verify_res.get("success") is True
    assert "Capsule validated and payload decrypted successfully" in verify_res.get("status_message", "")
    assert "TRANSFER" in verify_res.get("decrypted_payload", "")

def test_api_attack_simulations():
    init_keys()
    # Build initial capsule
    call_handler("POST", "/api/build_capsule", {"payload": "Sensitive Attack Test Payload"})

    # 1. Tamper Attack
    tamper_res = call_handler("POST", "/api/simulate_attack", {"attack_type": "tamper"})
    assert tamper_res.get("success") is False
    assert "Tampering" in tamper_res.get("attack_name", "") or "Tamper" in tamper_res.get("attack_name", "")

    # 2. Replay Attack
    # First verify legitimately
    call_handler("POST", "/api/verify_capsule", {})
    # Second verify (Replay)
    replay_res = call_handler("POST", "/api/simulate_attack", {"attack_type": "replay"})
    assert replay_res.get("success") is False
    assert "Replay" in replay_res.get("attack_name", "") or "replay" in replay_res.get("status_message", "").lower()
