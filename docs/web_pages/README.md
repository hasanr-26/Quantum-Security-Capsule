# QSC Web Interfaces & Feature Documentation Suite

[![NIST PQC](https://img.shields.io/badge/NIST-FIPS%20203%20%7C%20FIPS%20204-green.svg)](https://csrc.nist.gov/projects/post-quantum-cryptography)
[![Live UI](https://img.shields.io/badge/Interface-Institutional%20Workbench-blue.svg)](https://127.0.0.1:8443)
[![Tests](https://img.shields.io/badge/tests-69%20passed%20%7C%20100%25-brightgreen.svg)](../../tests/)

---

## Overview

This directory provides an exhaustive, feature-by-feature operational and theoretical manual for every web interface, screen, tab, and control element in the Quantum Security Capsule (QSC) platform.

For each interface, the documentation specifies:
1. **What it does** (user triggers, request payloads, backend routing, state transitions)
2. **What it shows** (UI outputs, telemetry indicators, color codes, timing metrics)
3. **How each feature works** (client-side JS logic, backend Python algorithms, OpenSSL session extraction)
4. **The theory behind it** (mathematical foundations, NIST standards, threat modeling, regulatory mandates)

---

## Documentation Index

| Document | Focus Area | Key Features Covered |
| :--- | :--- | :--- |
| **[`00_overview_and_masthead.md`](00_overview_and_masthead.md)** | **Workbench Architecture & Masthead** | SPA layout, live heartbeat polling, node identity, transport health indicator, cipher suite inspector, uptime, API request counter, capsule counter, rejection counter, replay cache occupancy, ML-KEM fingerprint. |
| **[`01_settlement.md`](01_settlement.md)** | **Tab 01 &mdash; Settlement Console** | ISO 20022 `pacs.008` & SWIFT MT103 message selector, validity TTL, policy jurisdiction selector, Rotate Keys, Build Capsule (8-step pipeline), Transmit & Settle, direct vs proxy routing, 5-stage zero-trust validation trace, decrypted payload display, network console. |
| **[`02_packet_inspector.md`](02_packet_inspector.md)** | **Tab 02 &mdash; Packet Inspector & Attack Lab** | Raw wire format hex dump, interactive colored field chips legend, byte selection inspector (hex/binary/ASCII/role), single-bit flip tampering lab, verbatim capsule replay simulator, stage diagnostics. |
| **[`03_3d_visualizer.md`](03_3d_visualizer.md)** | **Tab 03 &mdash; Interactive 3D Visualizer** | Three.js WebGL isometric banking graph, Mode A (TLS 1.3) vs Mode B (QSC Capsule), 5-step transit sequence, 4-phase quantum attack simulation (Harvest $\rightarrow$ Archive $\rightarrow$ Shor's algorithm $\rightarrow$ Breach vs Resilience), camera navigation, lattice parameter HUD, scrubbable timeline, narration stream. |
| **[`04_interception_lab.md`](04_interception_lab.md)** | **Tab 04 &mdash; Interception Lab & Proxy Forensics** | Port 8444 TLS-terminating forward proxy, Send Payment via TLS Only (control group), Send Payment as Capsule, Break Archived TLS Sessions, harvested flows table, post-quantum forensic analysis (cleartext card/wire breach vs opaque ciphertext). |
| **[`05_cryptography.md`](05_cryptography.md)** | **Tab 05 &mdash; Cryptographic Parameters & Telemetry** | NIST FIPS 203 (ML-KEM-768) parameter sets, NIST FIPS 204 (ML-DSA-65) parameter sets, AES-256-GCM, HKDF-SHA3-512, SHA3-512, live loopback TLS handshake probe, handshake duration, active X.509 certificate inspection. |
| **[`06_api_docs_and_visualizer.md`](06_api_docs_and_visualizer.md)** | **Interactive OpenAPI & Standalone Visualizer** | FastAPI interactive Swagger UI (`/api/docs`), OpenAPI 3.0 schema (`/api/openapi.json`), standalone educational dashboard on port 5000 (`src/visualizer/`). |

---

## Quick Navigation Matrix

```
                                    QSC WEB INTERFACES
                                             │
               ┌─────────────────────────────┴─────────────────────────────┐
               ▼                                                           ▼
    Security Workbench (:8443)                                  FastAPI OpenAPI Docs (:8443/api/docs)
    [00_overview_and_masthead.md]                               [06_api_docs_and_visualizer.md]
               │
    ┌──────────┼──────────┬──────────┬──────────┐
    ▼          ▼          ▼          ▼          ▼
  Tab 01     Tab 02     Tab 03     Tab 04     Tab 05
Settlement Inspector 3D Visual Intercept  Crypto
 [01.md]    [02.md]    [03.md]    [04.md]    [05.md]
```
