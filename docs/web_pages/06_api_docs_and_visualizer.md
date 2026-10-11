# Interactive API Documentation & Standalone Educational Visualizer

[![FastAPI](https://img.shields.io/badge/API-FastAPI%20OpenAPI%203.0-009688.svg)](https://127.0.0.1:8443/api/docs)
[![Swagger](https://img.shields.io/badge/Docs-Interactive%20Swagger%20UI-green.svg)](https://127.0.0.1:8443/api/docs)
[![NIST PQC](https://img.shields.io/badge/NIST-FIPS%20203%20%7C%20FIPS%20204-green.svg)](https://csrc.nist.gov/projects/post-quantum-cryptography)

---

## 1. Overview

In addition to the primary **Security Workbench**, the QSC platform provides two dedicated web interfaces:
1. **Interactive OpenAPI / Swagger Documentation (`/api/docs`):** Live, auto-generated REST API documentation hosted on the settlement node (`https://127.0.0.1:8443/api/docs`).
2. **Standalone Educational Visualizer (`src/visualizer/`):** A lightweight, self-contained demonstration dashboard designed for isolated local testing without TLS dependencies.

---

## 2. Interactive OpenAPI / Swagger UI (`/api/docs`)

FastAPI automatically parses Pydantic request models, type hints, and docstrings in [`src/server/api.py`](../../src/server/api.py) to render an interactive **Swagger UI** over TLS 1.3 at `https://127.0.0.1:8443/api/docs` (with raw OpenAPI JSON schema available at `/api/openapi.json`).

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ QSC Settlement Network API — v1.0 [OpenAPI 3.0]                             │
│ Base URL: https://127.0.0.1:8443                                            │
├─────────────────────────────────────────────────────────────────────────────┤
│ GET    /api/v1/health                  Liveness probe with uptime           │
│ GET    /api/v1/pqc/parameters          Active NIST parameter sets HUD       │
│ POST   /api/v1/pqc/keys/generate       Generate fresh ML-KEM & ML-DSA keys  │
│ GET    /api/v1/payloads                List financial message templates     │
│ POST   /api/v1/payloads/generate       Generate fresh pacs.008 or MT103 wire│
│ POST   /api/v1/capsule/encapsulate     Assemble an 8-step quantum capsule   │
│ POST   /api/v1/capsule/settle          Execute 5-stage validation & settle  │
│ GET    /api/v1/capsule/{id}/hexdump    Raw canonical wire byte dump         │
│ POST   /api/v1/legacy/transfer         Conventional TLS transfer (control)  │
│ POST   /api/v1/attack/tamper           Single-bit wire mutation simulation  │
│ POST   /api/v1/attack/replay           Verbatim capsule replay simulation   │
│ GET    /api/v1/network/telemetry       Node operational metrics & telemetry │
│ GET    /api/v1/network/tls             Loopback TLS handshake probe         │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.1 Key Endpoints Breakdown

#### `POST /api/v1/capsule/encapsulate`
- **What it does:** Accepts financial payload bytes and policy constraints, then constructs a complete Quantum Security Capsule using the 8-step pipeline.
- **Request Body:**
  ```json
  {
    "sender_id": "BARCGB22XXX",
    "recipient_id": "HDFCINBBXXX",
    "payload_kind": "pacs008",
    "policy": {
      "classification": "CONFIDENTIAL",
      "jurisdiction": "UK",
      "max_hops": 3,
      "ttl_seconds": 300
    }
  }
  ```
- **Response:** Returns `capsule_id`, canonical wire base64 string, byte sizes, field offsets, and microsecond build timings.

---

#### `POST /api/v1/capsule/settle`
- **What it does:** Submits an inbound capsule for zero-trust validation and clearing.
- **Header:** `X-QSC-Version: 1.0`
- **Response:**
  ```json
  {
    "status": "SETTLED",
    "capsule_id": "qsc_99a81f3b7c2a41d0",
    "stage_diagnostics": [
      {"stage": 1, "name": "Protocol Version", "status": "PASS", "elapsed_us": 1.2},
      {"stage": 2, "name": "Freshness Window", "status": "PASS", "elapsed_us": 6.8},
      {"stage": 3, "name": "Replay Token", "status": "PASS", "elapsed_us": 2.1},
      {"stage": 4, "name": "Integrity Lock", "status": "PASS", "elapsed_us": 58.4},
      {"stage": 5, "name": "Origin Signature", "status": "PASS", "elapsed_us": 16820.0}
    ],
    "decrypted_payload": "<Document xmlns=\"urn:iso:std:iso:20022:tech:xsd:pacs.008.001.08\">...",
    "timings": {"validation_ms": 16.89, "decryption_ms": 8.41, "total_ms": 25.30}
  }
  ```

---

#### `POST /api/v1/attack/tamper`
- **What it does:** Flips a single bit in the capsule's wire bytes and evaluates which validation gate rejects it.
- **Request Body:** `{"capsule_id": "qsc_...", "byte_offset": 146, "bit": 2}`
- **Response:** Details the byte before (`0x4d`), byte after (`0x4f`), affected field, and the exact stage diagnostic failure.

---

## 3. Standalone Educational Visualizer (`src/visualizer/`)

Located in [`src/visualizer/`](../../src/visualizer/), this legacy educational interface provides a lightweight, single-file dashboard for demonstrating the cryptographic primitives without requiring TLS certificates.

### 3.1 Architecture & Launch
```bash
python src/visualizer/app.py
```
- Listens on `http://127.0.0.1:5000`.
- Provides a simple two-column card dashboard with interactive buttons for:
  1. Key Generation (ML-KEM & ML-DSA)
  2. Capsule Assembly & Canonical Serialization
  3. Replay Protection Testing
  4. Bit-Flipping Tampering Simulation

### 3.2 Role within the Project
While the primary production system is the **FastAPI Security Workbench on port 8443**, the standalone visualizer serves as an isolated developer playground and unit-testing fixture ([`tests/test_api_endpoints.py`](../../tests/test_api_endpoints.py)).
