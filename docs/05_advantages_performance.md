# Document 05: Advantages, Performance & Scalability

**Barclays Innovation Lab Proposal**  
**Author**: Principal Security Architect, Barclays Innovation Lab  

---

## 13. Advantages

### 13.1 Architectural Shift
1. **Payload-Centric Security:** Security moves with the data. Whether stored in a database, queued in Apache Kafka, routed through IBM MQ, or transmitted over REST APIs, the message remains fully encrypted and verifiable.
2. **Zero-Trust Middlebox Independence:** Intermediary API gateways, load balancers, and network proxies can route capsules using metadata headers without ever decrypting sensitive payload data.
3. **Granular Non-Repudiation:** Each message carries its own independent ML-DSA signature, establishing clear audit trails for regulatory compliance (e.g., FCA, PRA, SWIFT CSP).

---

## 14. Performance Analysis

### 14.1 Key Sizes & Byte Overhead Comparison

| Cryptographic Primitive | Algorithm | Public Key Size | Private Key Size | Ciphertext / Sig Size |
| :--- | :--- | :--- | :--- | :--- |
| **Legacy KEM / Asymmetric** | RSA-3072 | 384 bytes | 384 bytes | 384 bytes |
| **Legacy ECC** | ECDSA P-256 | 64 bytes | 32 bytes | 64 bytes |
| **PQC Key Encapsulation** | **ML-KEM-768** (FIPS 203) | 1,184 bytes | 2,400 bytes | 1,088 bytes |
| **PQC Digital Signature** | **ML-DSA-65** (FIPS 204) | 1,952 bytes | 4,032 bytes | 3,309 bytes |

### 14.2 Computational Benchmark (Standard Intel Xeon / ARM Neoverse)

| Stage | Operation | CPU Latency (ms) | Memory Impact |
| :--- | :--- | :--- | :--- |
| **Building** | ML-KEM Encapsulation + AES-GCM Encrypt + ML-DSA Sign | ~0.45 ms | Low (< 5 KB stack allocations) |
| **Validation** | Header Check + Replay Lookup + SHA3-512 + ML-DSA Verify | ~0.35 ms | Minimal (< 2 KB) |
| **Decryption** | ML-KEM Decapsulate + AES-GCM Decrypt | ~0.20 ms | Minimal (< 2 KB) |
| **Total Overhead** | **End-to-End Capsule Processing** | **~1.00 ms** | **Sub-5 KB per payload** |

> *Note: Latency impact of 1.0 ms is negligible compared to standard network round-trip times (15–50 ms) in interbank wire transfers.*

---

## 15. Scalability Considerations

### 15.1 High-Throughput Financial Systems (Kafka & IBM MQ)
1. **Stateless Validation:** Capsule validation requires no active session state with the sender. Microservices can scale horizontally behind load balancers without session affinity or sticky connections.
2. **Distributed Replay Token Registry:** Replay prevention tokens are stored in a high-throughput, low-latency distributed cache (e.g., Redis Enterprise Cluster with active-active replication).
3. **Zero Copy Memory Pipeline:** Wire serialization uses CBOR (Concise Binary Object Representation) for low-latency C++/Rust microservices, minimizing payload size.
