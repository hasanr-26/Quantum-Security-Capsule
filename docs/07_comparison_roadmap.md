# 07 — Cryptographic Comparison and Strategic Roadmap

[![NIST PQC](https://img.shields.io/badge/NIST-FIPS%20203%20%7C%20FIPS%20204-green.svg)](https://csrc.nist.gov/projects/post-quantum-cryptography)
[![Tests](https://img.shields.io/badge/tests-69%20passed%20%7C%20100%25-brightgreen.svg)](../tests/)

---

## 1. Multi-Dimensional Security Architecture Comparison

To understand why the Quantum Security Capsule (QSC) represents an architectural advancement rather than a mere cipher substitution, consider how it compares across legacy, transitional, and specialized security architectures:

| Architectural Dimension | Legacy TLS 1.3 / mTLS | Hybrid PQ-TLS (draft-ietf-tls) | Application PGP / S/MIME | Enterprise IPSec / VPN | Quantum Security Capsule (QSC) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Security Scope** | Transient socket pipe | Transient socket pipe | Message / Document | Network segment pipe | **Individual message payload** |
| **HNDL Quantum Resilience** | Vulnerable (broken by Shor's) | Protected in transit only | Vulnerable (RSA/ECC keys) | Vulnerable (broken by Shor's) | **Immune for decades (FIPS 203/204)** |
| **Middlebox / Proxy Survival** | Decrypted at first proxy | Decrypted at first proxy | Preserved through proxies | Decrypted at VPN gateway | **100% intact through all proxies** |
| **Async Queues (Kafka / MQ)** | No protection in topics | No protection in topics | Preserved, but no fast gating | No protection in topics | **Armored in queue topics & on disk** |
| **Data At Rest Protection** | None | None | File encryption only | None | **Self-contained encryption at rest** |
| **Replay Defense** | Handled per TCP session | Handled per TCP session | Weak / Nonce-dependent | Handled per IP packet | **Cryptographic per-message token** |
| **Origin Non-Repudiation** | Endpoint socket only | Endpoint socket only | Document signature | Network endpoint only | **ML-DSA-65 signature on wire payload** |
| **Fast-Path Rejection Gate** | TCP/TLS handshake | TCP/TLS handshake | None (decrypt first) | IP packet filter | **5-Stage Zero-Trust Gate (<10 µs)** |
| **Rollout / Migration Burden** | N/A (Standard) | High (Flag-day network upgrade)| High (User tooling) | High (Network topology) | **Zero (Incremental SDK inside TLS)** |

---

## 2. Why Hybrid TLS is Insufficient for Modern Financial Architecture

Proponents of network-layer updates often suggest that swapping post-quantum key exchange algorithms into TLS 1.3 ("Hybrid TLS") resolves the post-quantum problem. While Hybrid TLS is a valuable transport upgrade, it leaves systemic banking blindspots unaddressed:

### 2.1 The "Termination Fallacy"
In cloud-native banking environments, TLS terminates at the edge:
- **Cloud Ingress & CDN:** Cloudflare, AWS CloudFront, or Akamai terminate TLS at edge points of presence.
- **Enterprise WAF & Load Balancers:** F5 BIG-IP, NGINX, or Envoy terminate TLS to inspect headers and route traffic.
- **API Gateways:** Kong, Apigee, or AWS API Gateway terminate TLS to enforce rate limits and authorization.

The moment TLS terminates, the payload exists in cleartext in process memory. If an internal node, inspection appliance, or sidecar proxy is compromised, the transaction is exposed in full.

### 2.2 The "Asynchronous Broker Fallacy"
Financial architectures are inherently asynchronous. Core banking engines do not communicate exclusively via synchronous RPCs; they publish events to Kafka, RabbitMQ, or IBM MQ. TLS protects the client-to-broker connection, but the message sits unencrypted inside the broker's topic log on disk. A compromised broker volume exposes historical payments.

### 2.3 The "Infrastructure Upgrade Trap"
Deploying Hybrid TLS across an enterprise requires:
- Upgrading every intermediate reverse proxy, load balancer, WAF, and hardware appliance.
- Re-issuing enterprise CA certificate hierarchies with massive post-quantum certificates.
- Coordinated multi-vendor compatibility.

**The QSC Advantage:** QSC operates at the application payload layer. It runs *inside* ordinary TLS 1.3 connections today. A bank can deploy QSC between two critical microservices immediately without touching any network infrastructure, firewall rules, or load balancers.

---

## 3. Technical Roadmap & Evolution Phases

The QSC platform follows a structured development roadmap:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ PHASE 1: COMPLETED REFERENCE PLATFORM (Current Release)                     │
├─────────────────────────────────────────────────────────────────────────────┤
│ ✔ NIST FIPS 203 (ML-KEM-768) and FIPS 204 (ML-DSA-65) reference engines     │
│ ✔ NIST SP 800-56C HKDF-SHA3-512 content key derivation with domain separation│
│ ✔ NIST SP 800-38D AES-256-GCM AEAD payload encryption                        │
│ ✔ 8-step builder pipeline and 5-stage zero-trust validation gate             │
│ ✔ Live FastAPI TLS 1.3 settlement node (:8443) and interception proxy (:8444)│
│ ✔ Institutional Web Security Workbench with Three.js 3D visualizer           │
│ ✔ Wireshark-style interactive hex dump inspector with live bit-flipping      │
│ ✔ Real financial standards: ISO 20022 pacs.008.001.08 and SWIFT MT103       │
│ ✔ 69 automated tests passing across 8 dedicated test suites                  │
│ ✔ 6 standalone CLI executable demonstration tools                            │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ PHASE 2: HIGH-THROUGHPUT ENTERPRISE HARDENING (Months 6-18)                 │
├─────────────────────────────────────────────────────────────────────────────┤
│ • Native C Cryptographic Acceleration: Drop-in bindings to liboqs / AWS-LC   │
│   for 50x-100x latency reduction (bringing ML-DSA signing under 1 ms).      │
│ • Binary Wire Encoding: CBOR / Protobuf serialisation to remove the ~33%    │
│   base64 transport size overhead.                                           │
│ • Distributed Replay Cache: Redis / Valkey integration with atomic SET NX   │
│   and automatic TTL expiry for horizontal multi-node scaling.               │
│ • Hardware Security Module (HSM) Integration: PKCS#11 key management.      │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ PHASE 3: ECOSYSTEM & MULTI-PLATFORM EXPANSION (Months 18-36)                │
├─────────────────────────────────────────────────────────────────────────────┤
│ • Native Apache Kafka & IBM MQ Serializer/Deserializer (SerDe) interceptors.│
│ • High-performance gRPC streaming transport support.                        │
│ • Mobile SDKs: Native Swift (iOS Secure Enclave) & Kotlin (Android Keystore)│
│   for consumer banking integration.                                         │
│ • Crypto-Agility Engine: Runtime pluggability for alternative PQC algorithms│
│   (e.g., Falcon-512, SPHINCS+) via dynamic policy negotiation.              │
└─────────────────────────────────────────────────────────────────────────────┘
```
