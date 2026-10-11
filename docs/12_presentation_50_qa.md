# 12 — 50 Presentation & Defense Questions and Answers

[![NIST PQC](https://img.shields.io/badge/NIST-FIPS%20203%20%7C%20FIPS%20204-green.svg)](https://csrc.nist.gov/projects/post-quantum-cryptography)
[![Tests](https://img.shields.io/badge/tests-70%20passed%20%7C%20100%25-brightgreen.svg)](../tests/)

> **How to use this guide:** These are 50 anticipated questions asked by judges, professors, evaluators, and audience members. The answers are written in **clear, simple, non-jargon English** so you can easily speak them during your presentation or Q&A session.

---

## Table of Contents

- [Part 1: General Project & Big Picture (Q1 &ndash; Q8)](#part-1-general-project--big-picture-q1--q8)
- [Part 2: The Quantum Threat & HNDL (Q9 &ndash; Q14)](#part-2-the-quantum-threat--hndl-q9--q14)
- [Part 3: Tab 01 &mdash; Settlement Workbench (Q15 &ndash; Q22)](#part-3-tab-01--settlement-workbench-q15--q22)
- [Part 4: Tab 02 &mdash; Packet Inspector & Tamper Defense (Q23 &ndash; Q29)](#part-4-tab-02--packet-inspector--tamper-defense-q23--q29)
- [Part 5: Tab 03 &mdash; 3D Visualizer (Q30 &ndash; Q36)](#part-5-tab-03--3d-visualizer-q30--q36)
- [Part 6: Tab 04 &mdash; Interception Lab (Q37 &ndash; Q42)](#part-6-tab-04--interception-lab-q37--q42)
- [Part 7: Tab 05 &mdash; Cryptography & Performance (Q43 &ndash; Q46)](#part-7-tab-05--cryptography--performance-q43--q46)
- [Part 8: Architecture, APIs & Real-World Banking (Q47 &ndash; Q50)](#part-8-architecture-apis--real-world-banking-q47--q50)

---

## Part 1: General Project & Big Picture (Q1 &ndash; Q8)

### 1. What is the Quantum Security Capsule (QSC) project in one simple sentence?
**Answer:**  
QSC turns sensitive financial messages into self-protecting, quantum-resistant digital safes so they stay safe even if the network is intercepted or recorded.

### 2. Why did you build this project?
**Answer:**  
Because modern financial security only protects the network connection, not the data itself. When encrypted network traffic is intercepted today or passes through intermediate servers, the financial data is at serious risk.

### 3. What is the main difference between traditional TLS and QSC?
**Answer:**  
TLS secures the **pipe** between two immediate computers. QSC secures the **message itself**. Even if someone breaks the pipe or intercepts the data along the way, the message remains locked and unreadable.

### 4. What is the core flaw with internet security today?
**Answer:**  
Internet encryption (like HTTPS and TLS) terminates at the first proxy, gateway, or load balancer. Once it arrives there, the data is decrypted into plaintext memory before moving to the next system.

### 5. What does "Message-Centric Security" mean?
**Answer:**  
It means putting the armor directly on the data package rather than relying on the road it travels on. The message carries its own post-quantum encryption, integrity lock, and digital signature wherever it goes.

### 6. Does QSC replace TLS or work with it?
**Answer:**  
QSC works **with** TLS as defense-in-depth. TLS provides basic transport privacy, while QSC guarantees end-to-end post-quantum safety across all hops and databases.

### 7. What types of financial messages does QSC protect?
**Answer:**  
It protects standard global banking formats, including ISO 20022 interbank transfers (`pacs.008`), SWIFT wire messages (`MT103`), and PCI-DSS credit card payment authorizations.

### 8. What is the main benefit for a bank or financial institution?
**Answer:**  
Banks can guarantee that multi-million pound transfers, customer account numbers, and SWIFT instructions recorded today can never be decrypted by future quantum computers.

---

## Part 2: The Quantum Threat & HNDL (Q9 &ndash; Q14)

### 9. What does "Harvest Now, Decrypt Later" (HNDL) mean?
**Answer:**  
Hostile organizations are intercepting and saving petabytes of encrypted banking traffic today. They cannot read it now, but they will decrypt it years later when powerful quantum computers become available.

### 10. What is a "Cryptographically Relevant Quantum Computer" (CRQC)?
**Answer:**  
It is a future quantum computer large and stable enough to run Shor's algorithm and break RSA and Elliptic Curve encryption in minutes.

### 11. How does a quantum computer break today's encryption?
**Answer:**  
Current security relies on mathematical problems that are hard for regular computers (like factoring large numbers). Quantum computers use Shor's algorithm, which solves these specific mathematical problems almost instantly.

### 12. Why should banks worry today if quantum computers aren't here yet?
**Answer:**  
Because financial data has a long shelf life. Mortgages, trade secrets, sovereign debts, and customer identities need to stay confidential for 10 to 30 years. If captured today, they will be exposed during their secrecy lifetime.

### 13. Why can't we just wait until quantum computers are built?
**Answer:**  
Because traffic captured *today* will already be in adversarial archives. Waiting means everything sent between now and the quantum era is permanently compromised.

### 14. Why isn't updating TLS certificates to Post-Quantum (Hybrid TLS) enough?
**Answer:**  
Hybrid TLS only protects the active wire. As soon as traffic reaches an API gateway, cloud load balancer, or internal Kafka message queue, TLS is stripped away and the data sits in plaintext.

---

## Part 3: Tab 01 &mdash; Settlement Workbench (Q15 &ndash; Q22)

### 15. What does the "Settlement" tab demonstrate?
**Answer:**  
It demonstrates an originating bank building a real post-quantum capsule for a £50,000,000 transfer and transmitting it to a clearing house that verifies it through a 5-stage zero-trust gate.

### 16. What does the "Rotate Keys" button do?
**Answer:**  
It generates brand new, genuine NIST post-quantum keypairs for ML-KEM-768 and ML-DSA-65 on the spot, showing that the system uses real live cryptography.

### 17. What does the "Build Capsule" button do?
**Answer:**  
It takes the financial payment, encrypts it with AES-256-GCM using a key derived from post-quantum ML-KEM-768, locks it with SHA3-512, signs it with ML-DSA-65, and assigns a unique capsule ID.

### 18. What does the "Transmit & Settle" button do?
**Answer:**  
It sends the completed capsule over real HTTPS to the settlement node, which runs all 5 validation checks in real time and releases the decrypted funds.

### 19. What is the "Validity Window (TTL)" field?
**Answer:**  
It is a countdown timer (in seconds) that defines how long the capsule is valid. If a capsule arrives even 1 second after its deadline, it is rejected immediately.

### 20. What are the 5 stages of the Zero-Trust Validation Pipeline?
**Answer:**  
1. **Stage 1: Format & Schema:** Checks if headers and fields are valid.  
2. **Stage 2: Expiry & TTL:** Checks if the capsule is still inside its time limit.  
3. **Stage 3: Anti-Replay:** Verifies that this exact token has never been used before.  
4. **Stage 4: SHA3-512 Digest:** Checks that no bytes have been tampered with.  
5. **Stage 5: ML-DSA-65 Signature:** Mathematically verifies the sender's post-quantum signature.

### 21. Why are the 5 validation stages arranged in that specific order?
**Answer:**  
To stop Denial-of-Service attacks. It runs the fastest checks first (taking microseconds) so invalid or fake requests are thrown out before spending computer power on heavy post-quantum math.

### 22. What does the "Decrypted Payload" screen prove at the end?
**Answer:**  
It proves that only the authentic destination node holding the private key was able to unlock the capsule and read the financial instruction.

---

## Part 4: Tab 02 &mdash; Packet Inspector & Tamper Defense (Q23 &ndash; Q29)

### 23. What does the "Packet Inspector" tab show?
**Answer:**  
It shows the exact binary layout of the capsule down to every single byte, with color codes showing the header, post-quantum ciphertext, payload, and signature.

### 24. What are "wire bytes"?
**Answer:**  
Wire bytes are the raw 1s and 0s (displayed in hex format) that actually travel across network cables and internet routers.

### 25. What do the different colored byte blocks represent?
**Answer:**  
- **Blue:** Magic header, Capsule ID, and routing info.  
- **Purple:** ML-KEM-768 post-quantum key encapsulation bytes (1,088 bytes).  
- **Green:** Encrypted payment payload and AES tag.  
- **Yellow:** SHA3-512 integrity lock hash.  
- **Orange:** ML-DSA-65 post-quantum digital signature (3,309 bytes).

### 26. What happens when you press the "Flip Bit & Resubmit" button?
**Answer:**  
It flips just one single binary bit (a 0 to a 1) in the capsule and sends it to the server. The server immediately catches the change and rejects it.

### 27. Why does the system fail at Stage 4 when you flip a single bit?
**Answer:**  
Because the SHA3-512 cryptographic hash produces a completely different result if even one bit changes. The server detects the mismatch and blocks the transaction.

### 28. What happens when you press "Replay Capsule Verbatim"?
**Answer:**  
It sends the exact same, valid capsule a second time. The server catches it at **Stage 3 (Anti-Replay)** and rejects it because the token was already consumed.

### 29. Why is replay protection important in banking?
**Answer:**  
Without it, an attacker who intercepts an untouched £1,000,000 transfer could re-send it 100 times to drain an account. QSC makes every capsule strictly single-use.

---

## Part 5: Tab 03 &mdash; 3D Visualizer (Q30 &ndash; Q36)

### 30. What does the 3D visualizer show?
**Answer:**  
It provides an interactive 3D model comparing how a payment travels across a realistic 5-node banking network under standard TLS versus under QSC.

### 31. What are the 5 hops in the 3D visualizer?
**Answer:**  
1. Originating Bank  
2. Edge Gateway (CDN)  
3. Reverse Proxy / API Gateway  
4. Message Broker (Kafka / MQ)  
5. Clearing House

### 32. What should I press first when presenting the 3D visualizer?
**Answer:**  
Leave it on **`Mode A — TLS 1.3`** and click **`▶ Run Full Process`** to show the weakness of existing technology first.

### 33. What happens in Mode A (TLS 1.3)?
**Answer:**  
The payment travels through the network. When it reaches Node 3 (Reverse Proxy), the node turns **RED** because the proxy terminates TLS, exposing the payment in plaintext memory.

### 34. Why does the Reverse Proxy turn RED in Mode A?
**Answer:**  
Because reverse proxies, firewalls, and gateways have to decrypt TLS traffic to inspect headers. Anyone with access to that server can see account numbers, balances, and passwords.

### 35. What happens in Mode B (QSC Capsule)?
**Answer:**  
The bank seals the payment in green lattice particles. When the capsule hits the Reverse Proxy, the node stays **GREEN** because the proxy only sees opaque ciphertext. It routes the capsule without ever seeing the money or account details.

### 36. What happens when you click "Run Quantum Attack"?
**Answer:**  
In Mode A, an attacker with a quantum computer cracks the captured TLS session keys and steals the plaintext. In Mode B, the quantum attack fails completely because lattice mathematics cannot be solved by Shor's algorithm.

---

## Part 6: Tab 04 &mdash; Interception Lab (Q37 &ndash; Q42)

### 37. What is the Interception Lab on Tab 04?
**Answer:**  
It is a live middlebox attack lab that proves the difference between channel security and message security using a real intercepting proxy running on port 8444.

### 38. What is running on port 8444?
**Answer:**  
A genuine TLS-terminating forward proxy that intercepts, logs, and relays real network traffic, exactly like a corporate inspection appliance or malicious wiretap.

### 39. What happens when you click "Send Payment via TLS Only"?
**Answer:**  
The payment is sent over standard TLS. The proxy decrypts it and displays the full credit card number (PAN), CVV code, and cardholder name in cleartext on the screen.

### 40. What happens when you click "Send Payment as QSC Capsule"?
**Answer:**  
The payment is sent as a QSC capsule. The proxy captures the transmission, but all sensitive data appears as garbled ciphertext. A simulated quantum attack against it fails.

### 41. Is the proxy intercepting real network traffic or is it fake?
**Answer:**  
It is 100% real network traffic. The proxy opens real TCP sockets and TLS connections on port 8444, intercepts genuine HTTP requests, and stores the captured bytes.

### 42. Why can't the proxy decrypt the QSC capsule?
**Answer:**  
Because the decryption key never touches the proxy. Only the final settlement node holds the post-quantum ML-KEM private key needed to unlock the capsule.

---

## Part 7: Tab 05 &mdash; Cryptography & Performance (Q43 &ndash; Q46)

### 43. What post-quantum algorithms does QSC use?
**Answer:**  
It uses NIST's official post-quantum standards finalized in August 2024: **ML-KEM-768** (FIPS 203) for key exchange and **ML-DSA-65** (FIPS 204) for digital signatures.

### 44. In simple terms, what is Lattice-based Cryptography and what do the "Lattice Parameters" on the 3D screen mean?
**Answer:**  
Instead of relying on prime numbers (which quantum computers easily break), it hides secrets inside multidimensional geometric grids (lattices). Finding the secret point in a high-dimensional lattice is mathematically impossible for both classical and quantum computers to solve.

The **Lattice Parameters** box in the 3D visualizer displays the NIST FIPS 203 settings for ML-KEM-768:
- **Ring $\mathbb{Z}_q[X]/(X^{256}+1)$:** The mathematical rules where math is done on polynomials with 256 terms that wrap around like clock hands.
- **Modulus $q = 3329$:** The number clock &mdash; all numbers wrap around at 3329, enabling ultra-fast microsecond multiplication.
- **Module rank $k = 3$:** The security dimension ($3 \times 3$ polynomial grid) giving NIST Category 3 (AES-192 equivalent).
- **Shared secret: 256 bit:** The final 32-byte secret key agreed upon by both sides, which is used to encrypt the payment with AES-256-GCM.


### 45. What is the difference between ML-KEM-768 and ML-DSA-65?
**Answer:**  
- **ML-KEM-768** is for **encryption and key exchange** (making sure only the recipient can read the message).  
- **ML-DSA-65** is for **digital signatures** (proving who sent the message and that it wasn't modified).

### 46. Is post-quantum encryption slow? How fast is QSC?
**Answer:**  
No, it is very fast. Creating a capsule takes under **3 milliseconds**, and verifying it takes under **1.5 milliseconds**. The entire round trip is almost instantaneous.

---

## Part 8: Architecture, APIs & Real-World Banking (Q47 &ndash; Q50)

### 47. How do you prove this works on a real API and isn't just a UI animation?
**Answer:**  
Open `https://127.0.0.1:8443/api/docs` to see the live Swagger / OpenAPI documentation, or open browser DevTools (`F12` Network tab) to see genuine HTTP POST requests returning status 200 with cryptographic payloads.

### 48. How do you prove real TLS 1.3 is running?
**Answer:**  
Click the browser padlock icon or check endpoint `/api/v1/network/tls`. It shows live OpenSSL handshake parameters negotiated directly with the server.

### 49. Can QSC work over Apache Kafka, RabbitMQ, or message brokers?
**Answer:**  
Yes. Because QSC capsules are self-contained byte packages, they can be placed into Kafka message topics, cloud buckets, or SWIFT networks without needing any changes to the network.

### 50. What is your 10-second closing statement for judges or evaluators?
**Answer:**  
*"QSC makes the network irrelevant. By shifting post-quantum security from the transient connection pipe directly into the message itself, we guarantee that financial transactions remain safe from quantum decryption today, tomorrow, and decades into the future."*
