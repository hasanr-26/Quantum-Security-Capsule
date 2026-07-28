# Document 01 


## 1. Project Title

### **Quantum Security Capsule (QSC)**
*A Message-Centric Post-Quantum Cryptographic Architecture for Financial Infrastructure*

---

## 2. Vision Statement

To transition Barclays from legacy transport-centric security models to an autonomous, message-centric post-quantum cryptographic paradigm—ensuring that every transaction, payment instruction, API invocation, Kafka event stream, and file object is self-encapsulated, cryptographically bound, and immune to quantum decryption, replay attacks, and channel interception, regardless of the underlying network transport.

> *"We do not merely secure the tunnel; we cryptographically fortify every individual message."*

---

## 3. Problem Statement

### 3.1 The Vulnerability of Transport-Centric Security
Modern banking infrastructure (SWIFT gateways, core banking APIs, enterprise message queues like Apache Kafka and IBM MQ, consumer mobile apps, and confidential document transfers) relies fundamentally on transport-layer security mechanisms such as TLS 1.3, IPSec VPNs, and mTLS. These systems protect data **only while in transit inside an encrypted pipe**.

```
[ Client / App ] <========= TLS Tunnel (RSA-3072 / ECDH P-256) =========> [ API Gateway / WAF ]
                                        │
                             Captured Network Traffic
                    (Harvest Now, Decrypt Later - HNDL)
```

This traditional transport model contains three catastrophic vulnerabilities:

1. **Harvest Now, Decrypt Later (HNDL):** Adversaries and state-sponsored actors are actively intercepting and storing massive volumes of encrypted banking traffic today. Once Cryptographically Relevant Quantum Computers (CRQCs) emerge, attackers will apply **Shor's Algorithm** to crack the underlying RSA and ECC session keys, instantly exposing decades of historical financial records, private payment authorizations, customer PII, and SWIFT instructions.
2. **Channel-Dependent Security Boundaries:** Once a packet leaves the TLS termination proxy (e.g., at an API Gateway, WAF, or ingress load balancer), it travels across internal microservice meshes, Kafka topics, and MQ queues in plaintext or under weaker internal transport security. Security is lost at every middlebox boundary.
3. **Coarse-Granularity Non-Repudiation:** TLS authenticates endpoints (servers/clients), not individual payload messages. Compromise of a session key or gateway decrypts all past, present, and future messages sent over that connection socket.

---

### 3.2 Why Simple RSA-to-PQC Replacement in TLS is Insufficient

Simply swapping RSA/ECDH certificates with Post-Quantum Cryptography (PQC) inside TLS (Hybrid TLS 1.3) solves ephemeral key exchange for the connection socket, but leaves systemic payload vulnerabilities unchanged:
- **Tunnel Lifetime Dependency:** Messages inside the processing pipeline remain dependent on tunnel uptime and gateway integrity.
- **Middlebox High-Value Targets:** API gateways and load balancers remain high-value target points of plaintext exposure.
- **Asynchronous Queue Vulnerability:** Message replay and payload tampering across asynchronous message queues (Kafka/MQ) or long-term file storage cannot be natively prevented by TLS.

---

## 4. The QSC Paradigm Shift

The Quantum Security Capsule architecture directly addresses these limitations by shifting security from the **transport channel** into the **data payload itself**. Every message is wrapped in a self-contained digital container protected by NIST FIPS 203 ([`ML-KEM-768`](file:///c:/Users/hasan/antigravity/QSC/src/crypto/kem.py)) and FIPS 204 ([`ML-DSA-65`](file:///c:/Users/hasan/antigravity/QSC/src/crypto/dsa.py)).

---

## 5. Architectural Comparison Matrix

| Dimension / Metric | Legacy Transport Security (TLS 1.3 / Hybrid TLS) | Quantum Security Capsule (QSC) |
| :--- | :--- | :--- |
| **Security Scope** | Channel / Connection Pipe | Individual Message Payload |
| **Quantum Resilience** | Ephemeral tunnel protection only | Payload remains encrypted for decades regardless of transport |
| **Replay Defense** | Socket session bound | Cryptographically bound per message via SHA3-512 replay tokens |
| **Transport Agnostic** | No (Requires TCP/TLS socket) | Yes (Runs over HTTPS, Kafka, MQ, SWIFT, REST, GRPC, Files) |
| **Middlebox Exposure** | Exposed at TLS termination proxies | Zero exposure (Encrypted end-to-end to target receiver) |
| **Implementation Scope** | Infrastructure socket layer | Microservices, Mobile Apps, Enterprise SDK ([`src/capsule`](file:///c:/Users/hasan/antigravity/QSC/src/capsule)) |
