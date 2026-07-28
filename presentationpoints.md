PART 1: How to Show & Run Backend Scripts (Real Use Cases)
While the web dashboard (python src/visualizer/app.py) visualizes the cryptographic process interactively, the backend scripts execute the raw NIST post-quantum primitives natively in Python.

1. File Encryption & Decryption Use Case (NEW CLI DEMO)
We created a dedicated file encryption demo in 

src/demo/file_encrypt_demo.py
. It creates a sensitive payload (confidential_wire_instructions.pdf), encrypts it into a serialized .qsc file, and decrypts it back on the receiver side.

Run in terminal:

bash
python src/demo/file_encrypt_demo.py
What this demonstrates to judges:

Reading raw files/bytes.
Encapsulating file contents with ML-KEM-768 key exchange and AES-256-GCM authenticated payload encryption.
Digitally signing the payload hash with ML-DSA-65.
Writing a self-contained .qsc file to disk that can be safely stored or sent over untrusted channels.

2. High-Value Interbank Wire Transfer Demo
Demonstrates an end-to-end banking transaction workflow (e.g., £50,000,000 interbank settlement).

Run in terminal:

bash
python src/demo/banking_transfer.py
What this demonstrates to judges:

How a client/mobile application packages financial transactions into QSC objects.
How the settlement server validates and decrypts payloads.

3. Replay Attack & Tampering Mitigation Demo
Demonstrates defense against network adversaries, altered ciphertexts, and rogue public keys.

Run in terminal:

bash
python src/demo/replay_attack_demo.py
What this demonstrates to judges:

Replay Protection: Rejecting duplicated payloads via SHA3-512 replay tokens.
Tamper Resistance: Catching single-bit ciphertext modifications in transit.
Signature Forgery Resistance: Blocking unverified public keys.

4. Running the Automated Test Suite
To demonstrate enterprise code quality and validation:

Run in terminal:

bash
pytest tests/ -v
PART 2: Complete Codebase Walkthrough (Mathematical & Technical Pitch)
Use this guide when walking through the codebase file-by-file during a pitch, demo, or code audit.

🏛️ Executive Summary & Problem Statement
The Problem (Harvest Now, Decrypt Later - HNDL): Traditional transport layer security (TLS 1.3, IPSec, VPNs) protects the channel, not the message. Adversaries today passively intercept and record encrypted network traffic. When a Cryptographically Relevant Quantum Computer (CRQC) emerges, Shor's Algorithm will factor RSA/ECC keys in seconds, compromising all recorded historic traffic.

The Solution (Quantum Security Capsule - QSC): QSC transitions security from channel encryption to message-level post-quantum encapsulation. Every payload becomes a self-contained digital capsule protected by NIST FIPS 203 (ML-KEM-768) and FIPS 204 (ML-DSA-65).

🧮 Mathematical Foundations of the Cryptographic Stack
1. Key Encapsulation: ML-KEM-768 (NIST FIPS 203)
Mathematical Basis: Module Learning With Errors (M-LWE) over polynomial rings $\mathcal{R}_q = \mathbb{Z}_q[X]/(X^n + 1)$ with degree $n=256$ and modulus $q=3329$.
Hardness: Finding a secret vector $s$ given $A \cdot s + e = b \pmod q$, where $A$ is a random matrix, $s$ is the secret, and $e$ is a small error polynomial.
Purpose in QSC: Generates a 256-bit ephemeral shared secret per message without vulnerable Diffie-Hellman key exchanges.
Code File: 

src/crypto/kem.py
 (

MLKEM768
)
2. Digital Signatures: ML-DSA-65 (NIST FIPS 204)
Mathematical Basis: Module Learning With Errors (M-LWE) and Module Short Integer Solution (M-SIS).
Hardness: Finding small non-zero vectors $z$ such that $A \cdot z = 0 \pmod q$.
Purpose in QSC: Provides non-repudiation and origin verification, replacing RSA and ECDSA.
Code File: 

src/crypto/dsa.py
 (

MLDSA65
)
3. Symmetric Encryption: AES-256-GCM (NIST SP 800-38D)
Mathematical Basis: Galois Counter Mode over finite field $GF(2^{128})$.
Purpose in QSC: Authenticated Encryption with Associated Data (AEAD). Provides confidentiality and authenticates the Capsule ID (associated_data).
Code File: 

src/crypto/symmetric.py
 (

encrypt_aes_256_gcm
)
4. Integrity Locking: SHA3-512 (NIST FIPS 202)
Mathematical Basis: Keccak-f[1600] permutation using a sponge construction.
Purpose in QSC: Cryptographic binding of headers, policy metadata, ciphertexts, and replay tokens into a deterministic 512-bit hash.
Code File: 

src/crypto/hashing.py
 (

compute_sha3_512
)
📁 File-by-File Codebase Architecture
src/
├── crypto/           # Primitives layer (NIST Standards)
│   ├── kem.py        # ML-KEM-768 Key Encapsulation (FIPS 203)
│   ├── dsa.py        # ML-DSA-65 Digital Signature (FIPS 204)
│   ├── symmetric.py  # AES-256-GCM AEAD Symmetric Encryption
│   └── hashing.py    # SHA3-512 Digest & Canonical JSON Serializer
├── capsule/          # High-level QSC lifecycle orchestration
│   ├── models.py     # Data structures (QuantumSecurityCapsule, PolicyMetadata)
│   ├── builder.py    # 7-Step Capsule Creation Pipeline
│   ├── validator.py  # 5-Stage Zero-Trust Validation Pipeline
│   └── receiver.py   # Secure Decryption Engine
├── utils/            # Timestamping & replay prevention
│   ├── timestamp.py  # ISO-8601 formatting & TTL checks
│   └── token.py      # SHA3-512 Replay Token generation
├── demo/             # Executable use-case scripts
│   ├── banking_transfer.py
│   ├── replay_attack_demo.py
│   └── file_encrypt_demo.py
└── visualizer/       # Interactive HTTP server & UI
    ├── app.py
    └── index.html
🔄 End-to-End Execution Flow (Step-by-Step)
[Sender / Client App]                                            [Receiver / Banking Engine]
   │                                                                       │
   ├── 1. Generate Capsule ID & Timestamps (TTL: 300s)                     │
   ├── 2. ML-KEM-768 Encapsulate ➔ Ephemeral Key + KEM Ciphertext          │
   ├── 3. AES-256-GCM Encrypt ➔ Payload Ciphertext + Auth Tag + Nonce      │
   ├── 4. Generate Replay Token (SHA3-512 binding)                         │
   ├── 5. Canonicalize Header Fields (Deterministic JSON)                   │
   ├── 6. Compute Integrity Hash (SHA3-512)                                 │
   ├── 7. Sign Integrity Hash (ML-DSA-65 Signature)                        │
   │                                                                       │
   └──────────────────── Transmitted via REST / Kafka ─────────────────────►│
                                                                           │
                                                                           ├── Stage 1: Check Version (QSC-1.0)
                                                                           ├── Stage 2: Check Timestamp (Expires At)
                                                                           ├── Stage 3: Check Replay Cache
                                                                           ├── Stage 4: Re-compute SHA3-512 Integrity Hash
                                                                           ├── Stage 5: Verify ML-DSA-65 Signature
                                                                           ├── ML-KEM-768 Decapsulate Shared Secret
                                                                           └── AES-256-GCM Decrypt Payload
PART 3: Presentation Pitch Scripts
🎤 30-Second Elevator Pitch
"TLS and VPNs encrypt the wire, not the data. If an attacker records traffic today, a future quantum computer will break the session key and expose years of sensitive financial data. Our Quantum Security Capsule shifts security directly into the payload. Every message is encapsulated with NIST-standardized ML-KEM-768 lattice encryption and ML-DSA-65 digital signatures. Even across untrusted networks or compromised proxies, each message remains mathematically immune to quantum decryption."

🎤 3-Minute Technical Deep-Dive Talk
Introduction & The Quantum Threat:

"Good morning/afternoon. Today, financial institutions rely heavily on channel security like TLS 1.3. However, Harvest Now, Decrypt Later attacks mean encrypted data collected today can be decrypted when quantum hardware matures. To protect high-value operations, we need message-level post-quantum security."

How QSC Works:

"The Quantum Security Capsule (QSC) wraps payloads into self-contained security objects. In 

src/capsule/builder.py
, when a client creates a transaction, QSC executes a 7-step process:

First, we encapsulate an ephemeral symmetric key using ML-KEM-768 (NIST FIPS 203).
Second, we encrypt the payload using AES-256-GCM authenticated encryption.
Third, we bind the capsule metadata, expiry timestamp, and nonces using SHA3-512 into a canonical integrity hash.
Finally, we sign the integrity hash using ML-DSA-65 (NIST FIPS 204) lattice digital signatures."
Zero-Trust Validation & Resilience:

"On the receiving end in 

src/capsule/receiver.py
 and 

src/capsule/validator.py
, the engine enforces strict zero-trust rules. It validates the expiration window, verifies the ML-DSA signature, checks the SHA3-512 hash, and verifies against replay attacks before decapsulating the ML-KEM key and decrypting the payload."

Conclusion:

"As demonstrated by our live CLI scripts and web visualizer, QSC delivers end-to-end quantum security for banking transfers, message queues (Kafka/MQ), and critical file storage today."

❓ Anticipated Questions & Answers for Judges
Question	Answer
Why not just use Hybrid TLS 1.3?	Hybrid TLS protects data in transit through a single channel tunnel. If a middlebox, gateway, or proxy terminates TLS, the plaintext payload is exposed in memory. QSC secures the payload end-to-end through storage, Kafka queues, microservices, and databases.
What is the performance overhead?	ML-KEM key generation and encapsulation take less than 1 millisecond. Memory footprint increases by ~1.1 KB for public keys and ~3.3 KB for signatures, which is minimal for financial transactions.
How does QSC prevent replay attacks?	Each capsule generates a unique replay_token derived from SHA3-512(capsule_id + issued_at + sender_id + nonce). Receivers track consumed replay tokens within a short expiration window (e.g., 300s).