# Web Security Workbench &mdash; Overview & Masthead Telemetry

[![NIST PQC](https://img.shields.io/badge/NIST-FIPS%20203%20%7C%20FIPS%20204-green.svg)](https://csrc.nist.gov/projects/post-quantum-cryptography)
[![Live UI](https://img.shields.io/badge/Interface-Institutional%20Workbench-blue.svg)](https://127.0.0.1:8443)
[![Tests](https://img.shields.io/badge/tests-69%20passed%20%7C%20100%25-brightgreen.svg)](../../tests/)

---

## 1. Web Application Architecture Overview

The **QSC Security Workbench** is an institutional financial security application served over real TLS 1.3 by FastAPI and Uvicorn at `https://127.0.0.1:8443`. It provides an authentic, high-density operational workbench styled in accordance with mission-critical financial engineering consoles (Bloomberg Terminal, Palantir Foundry, Cloudflare Radar).

### 1.1 Structural Foundations
- **Frontend Stack:** Pure HTML5, modern vanilla ECMAScript (ES2022+), CSS variables, and WebGL/Three.js &mdash; zero external frontend frameworks (no React/Vue overhead, no "AI slop" CSS component libraries).
- **Client Controller:** Implemented across modular client engines in [`src/frontend/js/`](../../src/frontend/js/):
  - [`api_client.js`](../../src/frontend/js/api_client.js): Core asynchronous fetch client with millisecond network performance timing.
  - [`workbench.js`](../../src/frontend/js/workbench.js): Global controller managing tab switching, background polling, and view routing.
  - [`pipeline_view.js`](../../src/frontend/js/pipeline_view.js): 5-stage zero-trust validation rendering engine.
  - [`hex_inspector.js`](../../src/frontend/js/hex_inspector.js): Interactive Wireshark-style byte offset renderer.
  - [`attack_lab.js`](../../src/frontend/js/attack_lab.js): Single-bit wire mutation and replay execution controller.
  - [`visualizer_3d.js`](../../src/frontend/js/visualizer_3d.js): Three.js WebGL 3D simulation engine.
- **Backend API:** FastAPI REST application served directly by Uvicorn in [`src/server/api.py`](../../src/server/api.py).

---

## 2. Masthead Live Telemetry Bar

The top banner of the application (`<header class="masthead">`) acts as an active heartbeat monitor. Every 4 seconds, [`workbench.js`](../../src/frontend/js/workbench.js) queries the settlement node's live endpoints to extract telemetry directly from runtime memory and active OpenSSL sessions.

```
┌────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ QSC Security Workbench   BARCGB22XXX :: 127.0.0.1:8443                                                 │
├───────────────┬──────────────────────────┬──────────┬───────────┬──────────┬──────────┬──────────┬────────┤
│ Transport     │ Cipher                   │ Uptime   │ API Calls │ Capsules │ Rejected │ Replay   │ ML-KEM │
│ ● TLSv1.3     │ TLS_AES_256_GCM_SHA384   │ 00:14:22 │ 48        │ 12       │ 4        │ 8        │ a4f89b │
└───────────────┴──────────────────────────┴──────────┴───────────┴──────────┴──────────┴──────────┴────────┘
```

---

## 3. Masthead Feature Breakdown

### 3.1 Node Identity & Host Binding
- **DOM Element:** `#node-id`
- **What it does:** Displays the active settlement receiver's BIC identity and network socket binding (e.g., `BARCGB22XXX :: 127.0.0.1:8443`).
- **What it shows:** Confirms which banking entity node is currently hosting the session.
- **How it works:** Extracted from the `node_id` field in `GET /api/v1/network/telemetry` concatenated with `window.location.host`.
- **Theory behind it:** Multi-tenant financial clearing architectures require cryptographically bound identities. Senders must explicitly bind their key encapsulation mechanisms to known recipient BIC addresses (ISO 9362).

---

### 3.2 Transport Status Indicator
- **DOM Element:** `#stat-tls`
- **What it does:** Shows whether the active connection is running over secure TLS and indicates connection health with a pulsing green phosphor dot.
- **What it shows:** Displays `TLSv1.3` with `<span class="dot dot--live"></span>` when healthy, or `offline` with `<span class="dot dot--down"></span>` if disconnected.
- **How it works:** [`workbench.js`](../../src/frontend/js/workbench.js) invokes `GET /api/v1/network/tls`. The server performs an internal loopback probe against itself using Python's `ssl` socket module to extract `protocol` from the active OpenSSL connection context.
- **Theory behind it:** Proves that the workbench is communicating over genuine RFC 8446 TLS 1.3 transport rather than an unencrypted HTTP cleartext mock.

---

### 3.3 Negotiated Cipher Suite Inspector
- **DOM Element:** `#stat-cipher`
- **What it does:** Displays the exact symmetric and hash algorithm negotiated during the client-to-server TLS handshake.
- **What it shows:** Displays `TLS_AES_256_GCM_SHA384` (or ECDHE equivalent).
- **How it works:** Extracted directly from OpenSSL's `SSLSocket.cipher()` tuple during the server's live loopback probe.
- **Theory behind it:** Demonstrates modern transport encryption in action. While `TLS_AES_256_GCM_SHA384` is classically impenetrable, the key exchange relying on ECDHE is vulnerable to retroactive quantum decryption under Shor's algorithm &mdash; motivating the need for message-level QSC capsules.

---

### 3.4 Service Uptime Counter
- **DOM Element:** `#stat-uptime`
- **What it does:** Displays continuous elapsed operational time since the settlement daemon was initialized.
- **What it shows:** Formatted as `HH:MM:SS` or `Xm Ys`.
- **How it works:** The server measures `(now_utc - started_at).total_seconds()` in [`SessionState`](../../src/server/api.py). The client formats it via `QSC.fmtUptime()`.
- **Theory behind it:** Differentiates persistent enterprise network daemons from transient scripts that execute once and terminate.

---

### 3.5 Live API Request Counter
- **DOM Element:** `#stat-requests`
- **What it does:** Tracks the total number of HTTP requests processed by the settlement node during the current session.
- **What it shows:** Increments monotonically in cobalt blue (e.g., `48`).
- **How it works:** FastAPIs middleware (`add_telemetry_headers` in [`src/server/api.py`](../../src/server/api.py)) intercepts every `/api/*` call and increments `SESSION.request_count`.
- **Theory behind it:** Empirical verification of client-server interactivity. Clicking buttons immediately increments this counter across the network.

---

### 3.6 Capsules Built Counter
- **DOM Element:** `#stat-capsules`
- **What it does:** Counts the total number of post-quantum capsules assembled by this node.
- **What it shows:** Integer counter in clean neutral white (e.g., `12`).
- **How it works:** Incremented whenever `/api/v1/capsule/encapsulate` successfully completes an 8-step construction run and caches the capsule in `SESSION.capsules`.
- **Theory behind it:** Quantifies real lattice cryptographic operations performed by the server.

---

### 3.7 Validation Rejection Counter
- **DOM Element:** `#stat-rejected`
- **What it does:** Tracks every capsule that failed one or more zero-trust validation stages.
- **What it shows:** Highlighted in high-contrast red phosphor (e.g., `4`).
- **How it works:** Incremented in [`src/server/api.py`](../../src/server/api.py) whenever `SESSION.receiver.settle_with_report()` returns `accepted == False`.
- **Theory behind it:** Demonstrates fail-closed zero-trust enforcement. Whenever an operator flips a bit in the attack lab or attempts a replay attack, this counter increments.

---

### 3.8 Replay Cache Occupancy
- **DOM Element:** `#stat-replay`
- **What it does:** Displays the number of single-use SHA3-512 replay tokens currently consumed and held in the settlement validator's registry.
- **What it shows:** Counter rendered in warning amber (e.g., `8`).
- **How it works:** Evaluates `len(validator._seen_replay_tokens)` in [`src/capsule/validator.py`](../../src/capsule/validator.py).
- **Theory behind it:** Financial replay protection requires stateful single-use commitment. Settle a capsule, and this count increments. Re-submitting the same capsule triggers a Stage 3 cache hit rejection.

---

### 3.9 Active ML-KEM Public Key Fingerprint
- **DOM Element:** `#stat-kemfp`
- **What it does:** Displays the first 12 hex characters of the active recipient ML-KEM-768 public key fingerprint.
- **What it shows:** 12-character hex digest (e.g., `7f2b918a3e0c`).
- **How it works:** Computed as `SHA3-512(kem_public_bytes)[:12]` in [`src/server/api.py`](../../src/server/api.py).
- **Theory behind it:** Public key identity binding. When an operator triggers "Rotate Keys", this fingerprint immediately updates &mdash; proving that keypairs are dynamic and held in active memory rather than hardcoded in static files.
