# Document 01: Vision and Problem Statement

**Barclays Innovation Lab Proposal**  
**Author**: Principal Security Architect, Barclays Innovation Lab  
**Target Domain**: Financial Infrastructure Post-Quantum Transformation  

---

## 1. Project Title

### **Quantum Security Capsule (QSC)**
*A Message-Centric Post-Quantum Cryptographic Architecture for Financial Infrastructure*

---

## 2. Vision Statement

To transition Barclays from legacy transport-centric security models to an autonomous, message-centric post-quantum cryptographic paradigm—ensuring that every transaction, payment instruction, API invocation, and interbank message is self-encapsulated, cryptographically bound, and immune to quantum decryption, replay attacks, and channel interception, regardless of the underlying network transport.

> *"We do not merely secure the tunnel; we cryptographically fortify every individual message."*

---

## 3. Problem Statement

### 3.1 The Vulnerability of Transport-Centric Security
Modern banking infrastructure (SWIFT gateways, core banking APIs, enterprise message queues, and consumer mobile apps) relies fundamentally on transport-layer security mechanisms such as TLS 1.3, IPSec VPNs, and mTLS. These systems protect data **only while in transit inside an encrypted pipe**. 

```
[ Client ]  <========= TLS Tunnel (RSA/ECC) =========>  [ Server ]
                       ▲
                       │
             Captured Network Traffic
            (Harvest Now, Decrypt Later)
```

This model contains three catastrophic vulnerabilities:

1. **Harvest Now, Decrypt Later (HNDL):** Adversaries and state actors are passively intercepting and storing massive volumes of encrypted banking traffic today. Once Cryptographically Relevant Quantum Computers (CRQCs) emerge, attackers will crack the underlying RSA/ECDHE session keys and instantly expose decades of historical financial records, private authentication keys, and transaction history.
2. **Channel-Dependent Security Boundaries:** Once a packet leaves the TLS termination point (e.g., at an API Gateway, WAF, or load balancer), it travels across internal service meshes, Kafka topics, and MQ queues in plaintext or under weaker internal controls. Security is lost at every middlebox boundary.
3. **Coarse-Granularity Non-Repudiation:** TLS authenticates endpoints (servers/clients), not individual payload messages. A compromise of a session key or gateway decrypts all past, present, and future messages sent over that connection.

### 3.2 Why Simple RSA-to-PQC Replacement in TLS is Insufficient
Replacing RSA/ECC certificates with PQC algorithms inside TLS (Hybrid TLS) solves key exchange for the tunnel, but leaves payload vulnerability unchanged:
- Messages inside the pipeline remain dependent on tunnel state.
- Middlebox decryption points remain high-value targets.
- Message replay across queue boundaries or asynchronous processing pipelines cannot be natively prevented by TLS.

---

## Summary Matrix

| Metric / Dimension | Transport Security (TLS 1.3 / Hybrid TLS) | Quantum Security Capsule (QSC) |
| :--- | :--- | :--- |
| **Security Scope** | Channel / Pipe | Individual Message Payload |
| **Quantum Resilience** | Ephemeral tunnel protection only | Payload remains encrypted for decades regardless of transport |
| **Replay Defense** | Connection session bound | Cryptographically bound per message via SHA3-512 replay tokens |
| **Transport Agnostic** | No (Requires TCP/TLS socket) | Yes (Runs over HTTPS, Kafka, MQ, SWIFT, REST, GRPC) |
| **Middlebox Exposure** | Exposed at TLS termination proxies | Zero exposure (Encrypted end-to-end to target receiver) |
