# Quantum Security Capsule (QSC)

[![Barclays Innovation Lab](https://img.shields.io/badge/Barclays-Innovation%20Lab-blue.svg)](https://www.barclays.com)
[![NIST PQC](https://img.shields.io/badge/NIST-FIPS%20203%20%7C%20FIPS%20204-green.svg)](https://csrc.nist.gov/projects/post-quantum-cryptography)
[![License](https://img.shields.io/badge/License-MIT-purple.svg)](LICENSE)

> **Message-Centric Post-Quantum Cryptographic Communication Architecture for Financial Infrastructure**

---

## 📌 Executive Summary

Today's financial communication protocols (TLS, IPSec, VPNs, REST APIs, gRPC) encrypt the **connection channel**. If an adversary records encrypted network traffic today ("Harvest Now, Decrypt Later"), a future Cryptographically Relevant Quantum Computer (CRQC) will break the tunnel session keys and expose all historic payloads.

The **Quantum Security Capsule (QSC)** shifts security from *protecting the communication channel* to *protecting every individual message*. Each payload becomes a self-contained, post-quantum encrypted, signed, time-bounded, and tamper-proof digital capsule.

---

## 🏛️ Architectural Overview

```
                 Client App / Originator
                           │
             ┌─────────────┴─────────────┐
             ▼                           ▼
      Message Payload              Policy Metadata
             │                           │
             └─────────────┬─────────────┘
                           │
                Quantum Capsule Builder
     ┌─────────────────────┼─────────────────────┐
     │                     │                     │
 Encrypt (AES-256-GCM) Sign (ML-DSA-65) Key Encapsulation (ML-KEM-768)
     │                     │                     │
     └─────────────────────┼─────────────────────┘
                           │
                Quantum Security Capsule (QSC)
                           │
     ┌─────────────────────┴─────────────────────┐
     │  Transmitted via REST / Kafka / MQ / TLS  │
     └─────────────────────┬─────────────────────┘
                           │
                Capsule Validator & Receiver
     ┌─────────────────────┼─────────────────────┐
  Verify Sig           Verify Hash          Decapsulate & Decrypt
     └─────────────────────┼─────────────────────┘
                           │
                     Core Banking Engine
```

---

## 🛠️ Cryptographic Stack (NIST PQC Compliant)

| Security Property | Standard / Primitive | Purpose |
| :--- | :--- | :--- |
| **Key Encapsulation Mechanism** | **ML-KEM-768** (NIST FIPS 203) | Post-quantum shared secret generation per message |
| **Digital Signature** | **ML-DSA-65** (NIST FIPS 204) | Post-quantum lattice signature for non-repudiation |
| **Symmetric Encryption** | **AES-256-GCM** (NIST SP 800-38D) | Confidentiality and authenticated payload encryption |
| **Integrity Digest** | **SHA3-512** (NIST FIPS 202) | Full capsule binding and replay token calculation |

---

## 🚀 Quick Start

### 1. Installation

```bash
git clone https://github.com/hasanr-26/Quantum-Security-Capsule.git
cd Quantum-Security-Capsule
pip install -r requirements.txt
```

### 2. Run Interactive Demos

```bash
# High-Value Interbank Wire Transfer Demo
python src/demo/banking_transfer.py

# Replay Attack & Network Tampering Mitigation Demo
python src/demo/replay_attack_demo.py
```

### 3. Run Test Suite

```bash
pytest tests/ -v
```

---

## 📂 Project Structure

```
QSC/
├── CAPSULE_SPEC.md                   # Formal Wire Format Specification
├── README.md                         # Project Overview & Quick Start
├── requirements.txt                  # Dependencies
├── docs/                             # Comprehensive Innovation Deliverables (1-23)
│   ├── 01_vision_and_problem.md      # Deliverables 1–3 (Title, Vision, Problem)
│   ├── 02_architecture.md            # Deliverables 4–8 (Architecture & Components)
│   ├── 03_diagrams.md                # Deliverables 9–10 (ASCII & Sequence Diagrams)
│   ├── 04_security_analysis.md       # Deliverables 11–12 (Security & Threat Model)
│   ├── 05_advantages_performance.md  # Deliverables 13–15 (Advantages & Latency Metrics)
│   ├── 06_compliance_deployment.md   # Deliverables 16–18 (NIST Compliance & Banking Use Cases)
│   ├── 07_comparison_roadmap.md      # Deliverables 19–20 (vs Hybrid TLS & Future Roadmap)
│   └── 08_presentation.md            # Deliverables 21–23 (Pitch Deck, Elevator & 5-min Script)
├── src/                              # Source Implementation
│   ├── crypto/                       # Cryptographic Primitives (ML-KEM, ML-DSA, AES-GCM, SHA3)
│   ├── capsule/                      # Builder, Validator, Receiver, Data Models
│   ├── demo/                         # Executable Banking Demos
│   └── utils/                        # Timestamping & Replay Token Utilities
└── tests/                            # PyTest Verification Suite
```

---

## 📑 Complete Innovation Deliverables Index

All 23 requested deliverables are systematically covered across the `docs/` folder:

1. **Project Title** (`docs/01_vision_and_problem.md`)
2. **Vision Statement** (`docs/01_vision_and_problem.md`)
3. **Problem Statement** (`docs/01_vision_and_problem.md`)
4. **Existing Communication Architecture** (`docs/02_architecture.md`)
5. **Proposed QSC Architecture** (`docs/02_architecture.md`)
6. **End-to-End Communication Workflow** (`docs/02_architecture.md`)
7. **Detailed Component Descriptions** (`docs/02_architecture.md`)
8. **Internal Structure of a QSC** (`docs/02_architecture.md` & `CAPSULE_SPEC.md`)
9. **Architecture Diagram (Text)** (`docs/03_diagrams.md`)
10. **Sequence Diagram** (`docs/03_diagrams.md`)
11. **Security Analysis** (`docs/04_security_analysis.md`)
12. **Threat Model** (`docs/04_security_analysis.md`)
13. **Advantages** (`docs/05_advantages_performance.md`)
14. **Performance Analysis** (`docs/05_advantages_performance.md`)
15. **Scalability Considerations** (`docs/05_advantages_performance.md`)
16. **Compliance with NIST PQC Standards** (`docs/06_compliance_deployment.md`)
17. **Barclays Deployment Strategy** (`docs/06_compliance_deployment.md`)
18. **Real-World Banking Use Cases** (`docs/06_compliance_deployment.md`)
19. **Comparison with Hybrid TLS** (`docs/07_comparison_roadmap.md`)
20. **Future Roadmap** (`docs/07_comparison_roadmap.md`)
21. **Presentation-Ready Diagrams** (`docs/08_presentation.md`)
22. **30-Second Elevator Pitch** (`docs/08_presentation.md`)
23. **5-Minute Presentation Script** (`docs/08_presentation.md`)

---

## 📄 License
Released under the MIT License. Developed for Barclays Post-Quantum Cryptography Innovation Challenge.
