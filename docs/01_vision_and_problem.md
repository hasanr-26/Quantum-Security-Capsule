# 01 — Vision and Problem Statement

[![Barclays Innovation Lab](https://img.shields.io/badge/Barclays-Innovation%20Lab-blue.svg)](https://www.barclays.com)
[![NIST PQC](https://img.shields.io/badge/NIST-FIPS%20203%20%7C%20FIPS%20204-green.svg)](https://csrc.nist.gov/projects/post-quantum-cryptography)
[![Tests](https://img.shields.io/badge/tests-69%20passed%20%7C%20100%25-brightgreen.svg)](../tests/)

---

## 1. Project Identity

### **Quantum Security Capsule (QSC)**
*Message-Centric Post-Quantum Cryptographic Architecture for Financial Infrastructure*

---

## 2. Vision Statement

To transition tier-1 financial infrastructure from transient, transport-centric security models to an autonomous, **message-centric post-quantum cryptographic paradigm**. Every high-value wire transfer, SWIFT instruction, ISO 20022 transaction, Kafka event stream, and treasury document is encapsulated into an independent cryptographic safe that remains mathematically immune to quantum decryption, middlebox exposure, and replay attacks &mdash; regardless of the underlying network transport.

> *"We do not merely secure the ephemeral communication tunnel; we cryptographically fortify every individual financial message for decades."*

---

## 3. The Problem Landscape in Institutional Banking

Modern global banking operations &mdash; high-value interbank settlement (CHAPS, Fedwire, TARGET2), international correspondent banking via SWIFT, cloud-native microservices, enterprise message brokers (Apache Kafka, IBM MQ), and treasury file transfers &mdash; depend overwhelmingly on transport-layer encryption (TLS 1.3, mTLS, IPSec).

While TLS provides robust protection for contemporary classical communications over direct point-to-point sockets, it introduces two existential structural vulnerabilities for financial institutions:

```
[ Originating Bank / Client ] <========= TLS Tunnel (RSA-3072 / ECDH P-256) =========> [ Ingress Gateway / WAF ]
                                                   │
                                       Captured Network Traffic
                                 (Harvest Now, Decrypt Later - HNDL)
                                                   │
                                                   ▼ (CRQC - Shor's Algorithm)
                                          PLAINTEXT WIRE DATA
```

### 3.1 Threat 1: "Harvest Now, Decrypt Later" (HNDL)
Hostile nation-states and well-resourced adversarial groups are actively recording and warehousing petabytes of encrypted financial network traffic from transatlantic cables, cloud interconnects, and public internet exchanges today.

1. **The Quantum Threat Horizon:** Practical Cryptographically Relevant Quantum Computers (CRQCs) running **Shor's algorithm** will factor large integers and solve discrete logarithms in polynomial time. This breaks RSA-2048/3072 and ECDH/ECDSA P-256/P-384.
2. **The Financial Confidentiality Lifespan:** Unlike disposable consumer web sessions, financial assets have confidentiality requirements extending 10, 20, or even 30 years:
   - Long-dated sovereign bonds and syndicated credit agreements
   - Strategic corporate treasury positions and mergers & acquisitions financing
   - Customer personally identifiable information (PII) and institutional account credentials
3. **The Current Danger:** A transaction encrypted with classical TLS today is **already compromised** if an adversary intercepts and archives the encrypted session bytes. When a quantum computer arrives in the 2030s, the attacker will compute the private key, derive the session key, and recover the historical cleartext.

### 3.2 Threat 2: The Multi-Hop Middlebox Blindspot
In modern distributed banking architecture, a message almost never travels directly from the originator to the final settlement engine over a single uninterrupted socket:

```
TRADITIONAL TRANSPORT SECURITY (TLS 1.3):
Client ──[TLS Tunnel 1]──► API Gateway / WAF ──[Internal Plaintext]──► Kafka Broker ──[TLS Tunnel 2]──► Settlement Node
                                ▲                                           ▲
                                └── Decrypted into memory at boundary        └── Exposed in message topic & on disk
```

- **TLS Terminates at Boundaries:** TLS only encrypts the connection between two immediate network interfaces. It terminates at the first reverse proxy, WAF, or ingress gateway.
- **Cleartext Exposure in Transit & Memory:** Across internal microservices, proxies, service mesh sidecars, corporate inspection appliances, and message brokers, transaction instructions exist in memory as unencrypted cleartext.
- **Asynchronous Pipelines & Queues:** Financial settlement relies heavily on asynchronous event streaming (Kafka, IBM MQ). TLS offers zero protection for data resting in queue topics or distributed logs.
- **Why "Hybrid TLS" Fails to Solve the Problem:** Upgrading connection pipes to Hybrid Post-Quantum TLS (PQ-TLS) protects the wire socket against quantum harvesting, but leaves data completely exposed the instant the socket terminates at the ingress proxy.

---

## 4. The QSC Paradigm Shift: Channel Security vs Message Security

The **Quantum Security Capsule (QSC)** shifts the cryptographic perimeter from the **transient communication channel** directly into the **data payload itself**:

```
QUANTUM SECURITY CAPSULE (QSC):
Client ──[Self-Contained Quantum Capsule]───────────────────────────────────────────────────────► Settlement Node
             │                                                                                         ▲
             ├─ Encapsulate: ML-KEM-768 Shared Secret (FIPS 203)                                       │
             ├─ Derive: HKDF-SHA3-512 Key with Domain Separation (SP 800-56C)                          │
             ├─ Encrypt: AES-256-GCM Payload with Capsule ID Binding (SP 800-38D)                      │
             ├─ Lock: SHA3-512 Canonical Integrity Digest (FIPS 202)                                   │
             ├─ Bind: SHA3-512 Single-Use Replay Token (TTL: 300s)                                     │
             └─ Sign: ML-DSA-65 Lattice Signature over Hash (FIPS 204)                                 │
             (Remains sealed and verified across proxies, brokers, queues, and untrusted clouds) ──────┘
```

Every transaction payload is converted into an autonomous cryptographic safe:
1. **Self-Armored:** Protected by NIST-standardized lattice cryptography before touching any network wire.
2. **Hop-Agnostic:** Can traverse public HTTPS APIs, reverse proxies, Kafka message brokers, IBM MQ queues, SWIFT rails, or offline files (`.qsc`) without intermediate decryption.
3. **Zero-Trust Verifiable:** Evaluated by a 5-stage validation gate that drops malicious or expired traffic in microseconds before invoking heavy lattice operations.

---

## 5. Architectural Comparison Matrix

| Dimension / Metric | Legacy Transport Security (TLS 1.3 / mTLS) | Hybrid PQ-TLS (FIPS 203 TLS) | Quantum Security Capsule (QSC) |
| :--- | :--- | :--- | :--- |
| **Security Perimeter** | Channel / Socket pipe | Channel / Socket pipe | **Individual message payload** |
| **HNDL Resistance** | Vulnerable (broken by Shor's) | Protected in transit only | **Protected end-to-end for decades** |
| **Middlebox Exposure** | Cleartext at reverse proxies / WAFs | Cleartext at reverse proxies / WAFs | **Zero exposure** (stays sealed until receiver) |
| **Async Queues (Kafka/MQ)** | No protection at rest in topics | No protection at rest in topics | **Cryptographically armored in any queue** |
| **Replay Defense** | Handled per socket session | Handled per socket session | **Cryptographic per-message SHA3-512 token** |
| **Origin Non-Repudiation** | Endpoint socket authentication | Endpoint socket authentication | **Cryptographic ML-DSA-65 signature on wire payload** |
| **Transport Agnostic** | Strictly requires TCP/TLS | Strictly requires TCP/TLS | **Runs over HTTPS, Kafka, MQ, SWIFT, files** |
| **Infrastructure Impact** | Requires edge-to-edge network upgrade | Requires full CA and client upgrades | **Incremental SDK rollout without network disruption** |

---

## 6. The Three Pillars of the QSC System

The QSC platform provides concrete, demonstrable verification across three foundational pillars:

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                     THE THREE PILLARS OF QSC                                     │
├──────────────────────────────┬───────────────────────────────────┬───────────────────────────────┤
│    PILLAR 1: NETWORK LIVE    │       PILLAR 2: 3D VISUALIZER     │    PILLAR 3: FINANCIAL REALITY│
├──────────────────────────────┼───────────────────────────────────┼───────────────────────────────┤
│ • Real TLS 1.3 / HTTPS API   │ • Three.js WebGL Interactive      │ • Genuine ISO 20022 pacs.008  │
│ • Live settlement on :8443   │ • TLS Tunnel vs QSC Capsule       │ • Genuine SWIFT MT103 Wires   │
│ • TLS-Terminating MITM Proxy │ • Simulated Quantum Attack        │ • Wireshark-Style Hex Dump    │
│ • Live HNDL Proof on :8444   │ • Harvest Now Decrypt Later Expl. │ • Interactive Bit-Flipping    │
└──────────────────────────────┴───────────────────────────────────┴───────────────────────────────┘
```

1. **Live Network Reality ([`src/server/`](../src/server/)):** Runs a real FastAPI settlement node over TLS 1.3 (`https://127.0.0.1:8443`) and an active interception proxy (`https://127.0.0.1:8444`). Clients execute real HTTPS calls, proving how captured TLS sessions expose cleartext while QSC capsules remain impenetrable.
2. **Interactive 3D Visualizer ([`src/frontend/`](../src/frontend/)):** A WebGL/Three.js simulation visually demonstrating the structural mechanics of tunnel collapse under Shor's algorithm versus lattice crystal armor resilience.
3. **Institutional Financial Standards & Hex Inspection ([`src/capsule/wire.py`](../src/capsule/wire.py)):** Generates live ISO 20022 `pacs.008` and SWIFT MT103 wire messages, mapped byte-for-byte in a real-time hex inspector with live tampering and bit-flipping controls.
