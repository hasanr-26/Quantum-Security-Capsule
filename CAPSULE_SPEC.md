# Quantum Security Capsule (QSC) Specification (v1.0)

[![NIST PQC](https://img.shields.io/badge/NIST-FIPS%20203%20%7C%20FIPS%20204-green.svg)](https://csrc.nist.gov/projects/post-quantum-cryptography)
[![Tests](https://img.shields.io/badge/tests-69%20passed%20%7C%20100%25-brightgreen.svg)](tests/)
[![Status](https://img.shields.io/badge/Status-Active%20Production%20Spec-blue.svg)]()

## 1. Overview
The **Quantum Security Capsule (QSC)** is a self-contained, message-level cryptographic object designed for post-quantum financial and enterprise environments. Instead of relying exclusively on transient transport-layer security (TLS 1.3 / VPNs) which terminates at intermediate middleboxes and is vulnerable to "Harvest Now, Decrypt Later" (HNDL) attacks, a QSC encapsulates:
- Message confidentiality (AES-256-GCM)
- Post-quantum shared key encapsulation (ML-KEM-768)
- Key derivation with domain separation (HKDF-SHA3-512)
- Post-quantum non-repudiable origin signatures (ML-DSA-65)
- Deterministic integrity locking (SHA3-512)
- Temporal freshness bounds (UTC ISO-8601 timestamps)
- Single-use replay protection tokens (SHA3-512)
- Governance and policy metadata

---

## 2. Technical Cryptographic Primitives & Theoretical Foundations

| Component | Standard / Algorithm | Role / Purpose | Wire / Memory Size | NIST Standard |
| :--- | :--- | :--- | :--- | :--- |
| **Key Encapsulation Mechanism** | **ML-KEM-768** | Ephemeral post-quantum shared secret establishment per message | Pub: 1,184 B \| Priv: 2,400 B \| CT: 1,088 B | **NIST FIPS 203** |
| **Digital Signatures** | **ML-DSA-65** | Quantum-resistant lattice digital signature over canonical integrity digest | Pub: 1,952 B \| Priv: 4,032 B \| Sig: 3,309 B | **NIST FIPS 204** |
| **Symmetric Payload Encryption** | **AES-256-GCM** | Authenticated Encryption with Associated Data (AEAD); binds `capsule_id` | Key: 32 B \| Nonce: 12 B \| Tag: 16 B | **NIST SP 800-38D** |
| **Key Derivation Function** | **HKDF-SHA3-512** | Derives AES content key from ML-KEM secret; salted with `capsule_id` | Input: 32 B secret \| Output: 32 B key | **NIST SP 800-56C Rev. 2** |
| **Integrity Hashing & Sponge** | **SHA3-512** | Permutation sponge for canonical integrity locking and single-use replay tokens | Digest: 64 B (128 hex chars) | **NIST FIPS 202** |

---

### 2.1 The Post-Quantum Threat Model: Why Classical Primitives Fail

Traditional financial transport systems rely on classical asymmetric schemes:
- **RSA-2048 / RSA-4096:** Hardness rests on integer factorization ($N = p \cdot q$).
- **ECDH / ECDSA (secp256r1, secp256k1, Ed25519):** Hardness rests on the Discrete Logarithm Problem over elliptic curve groups ($Q = d \cdot G$).

#### Shor's Algorithm Breakdown
On a Cryptographically Relevant Quantum Computer (CRQC), Peter Shor's algorithm (1994) solves both prime factorization and discrete logarithms in polynomial time:
$$\mathcal{O}\left((\log N)^3\right)$$
It accomplishes this via the **Quantum Fourier Transform (QFT)**, which discovers the period $r$ of modular exponentiation functions $f(x) = a^x \pmod N$ in polynomial quantum gates. This instantly compromises classical asymmetric keys.

#### The "Harvest Now, Decrypt Later" (HNDL) Threat
Adversaries intercept and archive encrypted interbank TLS 1.3 streams today. Once a CRQC becomes operational, all stored session keys negotiated via classical Diffie-Hellman or RSA will be retroactively extracted, exposing historical account numbers, balances, and wire transfers.

#### Grover's Algorithm on Symmetric Cryptography
Lov Grover's quantum search algorithm (1996) provides a quadratic speedup for searching unstructured spaces of size $N$, running in $\mathcal{O}(\sqrt{N})$ time:
- An adversary attempting to brute-force a 128-bit key requires only $2^{64}$ quantum operations (computationally plausible).
- For a **256-bit key** (such as **AES-256**), Grover's algorithm reduces effective security to $2^{128}$ quantum operations. A search space of $2^{128}$ operations exceeds the thermodynamic energy limits of the observable universe, ensuring that **AES-256 remains secure in the post-quantum era**.

#### The Lattice Hardness Guarantee
Lattice-based cryptography relies on geometric problems in high-dimensional Euclidean vector spaces (such as the Shortest Vector Problem, **SVP**, and Closest Vector Problem, **CVP**). Because multi-dimensional Euclidean lattices possess **no periodic abelian group structure**, Shor's Quantum Fourier Transform cannot identify periodicity, leaving lattice-based schemes resistant to all known quantum algorithms.

---

### 2.2 ML-KEM-768 (NIST FIPS 203) &mdash; Post-Quantum Key Encapsulation Mechanism

Implemented in [`src/crypto/kem.py`](file:///c:/Users/hasan/antigravity/QSC/src/crypto/kem.py) via `kyber-py` and ACVP-validated.

#### 1. What It Really Does
ML-KEM-768 allows a sender to establish a high-entropy, 256-bit symmetric shared secret $K$ with a receiver without transmitting $K$ across the wire and without requiring interactive handshakes. The sender uses only the recipient's static or pre-published encapsulation key. Only the entity holding the matching decapsulation key can recover $K$.

#### 2. Where It Is Used in QSC
- **Capsule Builder ([`src/capsule/builder.py`](file:///c:/Users/hasan/antigravity/QSC/src/capsule/builder.py), Step 2):** Takes the recipient's registered public key (1,184 bytes), runs `MLKEM768.encapsulate()`, generates a fresh 32-byte shared secret $K$, and emits the 1,088-byte `kem_ciphertext` embedded into the capsule wire format.
- **Secure Receiver ([`src/capsule/receiver.py`](file:///c:/Users/hasan/antigravity/QSC/src/capsule/receiver.py), Step 2):** Takes the recipient's private decapsulation key (2,400 bytes) and the received `kem_ciphertext`, runs `MLKEM768.decapsulate()`, and recovers the identical 32-byte shared secret $K$.

#### 3. Mathematical Foundations: Module Learning With Errors (M-LWE)
ML-KEM-768 operates over the cyclotomic polynomial ring:
$$\mathcal{R}_q = \mathbb{Z}_q[X] / (X^n + 1)$$
where:
- Polynomial degree: $n = 256$
- Prime modulus: $q = 3329$ ($q \equiv 1 \pmod{2n}$, enabling rapid Number Theoretic Transform (NTT) multiplications)
- Module rank: $k = 3$ (vectors of 3 polynomials in $\mathcal{R}_q$, effectively dimension $3 \times 256 = 768$)
- Centered Binomial Noise Distribution: $\chi_\eta$ with $\eta_1 = 2, \eta_2 = 2$. Coefficients are sampled as $\sum_{i=1}^\eta (a_i - b_i)$ where $a_i, b_i \in \{0, 1\}$.

The computational hardness stems from the **Module Learning With Errors (M-LWE)** problem: Given a public pseudo-random matrix $\mathbf{A} \in \mathcal{R}_q^{k \times k}$ and a noisy sample $\mathbf{t} = \mathbf{A}\mathbf{s} + \mathbf{e} \pmod q$, it is computationally infeasible to recover secret vector $\mathbf{s}$ or distinguish $\mathbf{t}$ from uniform randomness when $\mathbf{s}, \mathbf{e} \sim \chi_\eta^k$.

#### 4. Algorithmic Mechanics & Noise Cancellation

```
SENDER (Capsule Builder)                             RECIPIENT (Secure Receiver)
────────────────────────                             ───────────────────────────
Has recipient public key:                            Has private key:
  pk = (t, seed_A)                                     sk = (s, pk, H(pk), z)

1. Generate random 256-bit seed m
2. Derive (K, r) = G(m || H(pk))
3. Sample ephemeral r ~ χ₂³, e₁ ~ χ₂³, e₂ ~ χ₂
4. Compute ciphertext (u, v):
     u = Aᵀ·r + e₁ mod q
     v = tᵀ·r + e₂ + ⌈q/2⌋·m mod q
5. Emit kem_ciphertext = (u, v)
   Retain shared_secret = K ──────[ wire ]────────► 1. Decapsulate:
                                                       Compute: v - sᵀ·u mod q
                                                       = ⌈q/2⌋·m + Δ (noise)
                                                    2. Round coefficients -> recovers m
                                                    3. Recompute (K', r') = G(m || H(pk))
                                                    4. Verify u' == u and v' == v
                                                    5. Recover identical shared_secret = K
```

##### Decapsulation Noise Annihilation Math
When the receiver computes $v - \mathbf{s}^T \mathbf{u} \pmod q$:
$$v - \mathbf{s}^T \mathbf{u} = \left(\mathbf{t}^T \mathbf{r} + e_2 + \lceil q/2 \rfloor \cdot m\right) - \mathbf{s}^T \left(\mathbf{A}^T \mathbf{r} + \mathbf{e}_1\right)$$
Since $\mathbf{t} = \mathbf{A}\mathbf{s} + \mathbf{e}$, we have $\mathbf{t}^T = \mathbf{s}^T \mathbf{A}^T + \mathbf{e}^T$:
$$v - \mathbf{s}^T \mathbf{u} = \left(\mathbf{s}^T \mathbf{A}^T \mathbf{r} + \mathbf{e}^T \mathbf{r} + e_2 + \lceil q/2 \rfloor \cdot m\right) - \left(\mathbf{s}^T \mathbf{A}^T \mathbf{r} + \mathbf{s}^T \mathbf{e}_1\right)$$
The large algebraic term $\mathbf{s}^T \mathbf{A}^T \mathbf{r}$ cancels completely:
$$v - \mathbf{s}^T \mathbf{u} = \lceil q/2 \rfloor \cdot m + \underbrace{\left(\mathbf{e}^T \mathbf{r} - \mathbf{s}^T \mathbf{e}_1 + e_2\right)}_{\text{Noise perturbation } \Delta}$$
Because the error polynomials $\mathbf{s}, \mathbf{e}, \mathbf{r}, \mathbf{e}_1, e_2$ have small coefficients ($\le 2$), the magnitude of each coefficient in the noise term satisfies $\|\Delta\|_\infty < q/4$. When each coefficient is rounded to the nearest multiple of $\lceil q/2 \rfloor$, the noise $\Delta$ is completely eliminated, yielding message bits $m$ with zero error.

#### 5. Fujisaki-Okamoto (FO) Transform & Implicit Rejection
To protect against chosen-ciphertext attacks (IND-CCA2), ML-KEM uses the **Fujisaki-Okamoto transform**:
- After decoding $m'$, the decapsulator re-encrypts $m'$ using the public key to check whether $\mathbf{u}' = \mathbf{u}$ and $v' = v$.
- **Implicit Rejection:** If an attacker tampers with `kem_ciphertext`, ML-KEM **does not raise an exception or abort**. Raising an error would create a timing oracle. Instead, it deterministically outputs a pseudo-random key derived from a secret rejection seed $z$ stored in the private key:
  $$K_{\text{invalid}} = \text{J}(z \,\|\, c)$$
- This bogus key cascades into HKDF and AES-256-GCM, causing the GCM authentication tag verification to fail closed without leaking whether the KEM ciphertext was structurally malformed.

---

### 2.3 ML-DSA-65 (NIST FIPS 204) &mdash; Post-Quantum Digital Signatures

Implemented in [`src/crypto/dsa.py`](file:///c:/Users/hasan/antigravity/QSC/src/crypto/dsa.py) via `dilithium-py` and ACVP-validated.

#### 1. What It Really Does
ML-DSA-65 provides quantum-resistant cryptographic non-repudiation and origin authenticity. It proves that the capsule payload, headers, expiry, and policies were generated and authorized by the institutional sender possessing the private signing key, and guarantees that no intermediary could alter even one bit without invalidating the signature.

#### 2. Where It Is Used in QSC
- **Capsule Builder ([`src/capsule/builder.py`](file:///c:/Users/hasan/antigravity/QSC/src/capsule/builder.py), Step 8):** The sender computes the SHA3-512 canonical `integrity_hash` of the capsule, signs it using `MLDSA65.sign()`, and populates the 3,309-byte `signature` field (Base64 encoded).
- **Capsule Validator ([`src/capsule/validator.py`](file:///c:/Users/hasan/antigravity/QSC/src/capsule/validator.py), Stage 5):** The receiver takes the sender's registered public key (1,952 bytes), the re-computed `integrity_hash`, and the decoded signature bytes, then verifies them using `MLDSA65.verify()`.

#### 3. Mathematical Foundations: Module-SIS & Module-LWE
ML-DSA-65 operates over the polynomial ring:
$$\mathcal{R}_q = \mathbb{Z}_q[X] / (X^n + 1)$$
where:
- Polynomial degree: $n = 256$
- Prime modulus: $q = 8380417 = 2^{23} - 2^{13} + 1$ ($q \equiv 1 \pmod{2n}$)
- Matrix dimensions: $(k, \ell) = (6, 5)$. The matrix $\mathbf{A} \in \mathcal{R}_q^{6 \times 5}$ expands pseudo-randomly from a 32-byte public seed $\rho$.
- Hardness Assumptions:
  - **Module Short Integer Solution (M-SIS):** Finding a short non-zero polynomial vector $\mathbf{v}$ such that $\mathbf{A}\mathbf{v} = \mathbf{0} \pmod q$ with $\|\mathbf{v}\|_\infty \le \beta$.
  - **Module Learning With Errors (M-LWE):** Distinguishing $(\mathbf{A}, \mathbf{A}\mathbf{s}_1 + \mathbf{s}_2)$ from uniform distribution over $\mathcal{R}_q^k$.

#### 4. Fiat-Shamir with Aborts & Rejection Sampling
In classical Schnorr-style digital signatures, the signer computes a response $z = y + c \cdot x$, where $x$ is the private key, $y$ is a random nonce, and $c$ is the challenge hash. In lattice cryptography, secret key polynomials have small coefficients ($\le \eta = 4$). If $z = y + c \cdot s_1$ were published directly, **the distribution of $z$ would depend on the secret key $s_1$**. By collecting several hundred signatures, an adversary could average out $y$ and solve for $s_1$.

ML-DSA resolves this via Vadim Lyubashevsky's **Rejection Sampling (Fiat-Shamir with Aborts)**:
- The signer picks a masking vector $\mathbf{y}$ with coefficients uniformly distributed in $[-\gamma_1+1, \gamma_1-1]$, where $\gamma_1 = 2^{19}$.
- After computing candidate response $\mathbf{z} = \mathbf{y} + c \mathbf{s}_1$:
  $$\text{If } \|\mathbf{z}\|_\infty \ge \gamma_1 - \beta, \quad \text{the signer ABORTS, discards } \mathbf{y}, \text{ and restarts.}$$
  where $\beta = 196$.
- This rejection step ensures that any published signature $\mathbf{z}$ falls strictly within a central bounding box whose probability density function is **completely independent of the private key** $\mathbf{s}_1$.

#### 5. Step-by-Step Algebraic Mechanics

##### Key Generation
1. Expand matrix $\mathbf{A} \in \mathcal{R}_q^{6 \times 5}$ from 32-byte seed $\rho$.
2. Sample secret vectors with small coefficients $\mathbf{s}_1 \in S_\eta^5$ and $\mathbf{s}_2 \in S_\eta^6$ ($\eta = 4$).
3. Compute $\mathbf{t} = \mathbf{A}\mathbf{s}_1 + \mathbf{s}_2 \pmod q$.
4. Decompose $\mathbf{t}$ into high and low bits: $\mathbf{t} = \mathbf{t}_1 \cdot 2^d + \mathbf{t}_0$ using `Power2Round` ($d = 13$).
5. **Public Key:** $(\rho, \mathbf{t}_1)$ &mdash; 1,952 bytes.
6. **Private Key:** $(\rho, K, tr, \mathbf{s}_1, \mathbf{s}_2, \mathbf{t}_0)$ &mdash; 4,032 bytes.

##### Signature Generation
Given message digest $\mu$ (in QSC: the 512-bit canonical `integrity_hash`):
1. Sample masking vector $\mathbf{y} \in [-\gamma_1 + 1, \gamma_1 - 1]^5$.
2. Compute $\mathbf{w} = \mathbf{A}\mathbf{y} \pmod q$.
3. Decompose $\mathbf{w}_1 = \text{HighBits}(\mathbf{w}, 2\gamma_2)$ where $\gamma_2 = (q-1)/32 = 261888$.
4. Hash challenge polynomial: $c = \mathcal{H}(\mu \,\|\, \mathbf{w}_1) \in \mathcal{R}_q$ (a sparse polynomial with exactly $\tau = 49$ non-zero coefficients in $\{-1, +1\}$).
5. Compute response $\mathbf{z} = \mathbf{y} + c \mathbf{s}_1$.
6. **Rejection Checks:**
   - If $\|\mathbf{z}\|_\infty \ge \gamma_1 - \beta$, abort and resample $\mathbf{y}$.
   - Compute low bits $\mathbf{r}_0 = \text{LowBits}(\mathbf{w} - c\mathbf{s}_2, 2\gamma_2)$. If $\|\mathbf{r}_0\|_\infty \ge \gamma_2 - \beta$, abort and resample $\mathbf{y}$.
7. Compute hint vector $\mathbf{h} = \text{MakeHint}(-c\mathbf{s}_2, \mathbf{w} - c\mathbf{s}_2 + c\mathbf{t}_0, 2\gamma_2)$.
8. Output signature $\sigma = (\mathbf{z}, \mathbf{h}, c)$ &mdash; 3,309 bytes.

---

### 2.4 Deep Dive: Signature Verification Mechanics, Identification & Non-Identity

```
SIGNER                                                      VERIFIER
──────                                                      ────────
Message: μ = integrity_hash                                 Message: μ = integrity_hash
Secret: s₁, s₂  |  Public: (A, t₁)                          Public: (A, t₁)  |  Sig: (z, h, c)

1. w = A·y mod q                                            1. Check bounds:
2. w₁ = HighBits(w)                                              ||z||∞ < γ₁ - β  and  weight(h) ≤ 55
3. c = H(μ || w₁)                                           2. Recompute intermediate:
4. z = y + c·s₁                                                  w' = A·z - c·t₁·2ᵈ mod q
5. h = MakeHint(-c·s₂, w - c·s₂ + c·t₀)                     3. Recover high bits with hint:
                                                                 w₁' = UseHint(h, w')
                                                            4. Recompute challenge:
                                                                 c' = H(μ || w₁')
                                                            5. Verify:
                                                                 c' == c  ?  VALID : REJECT
```

#### 1. How Does the Verifier Identify Validity Without the Private Key?
The verifier does not have access to $\mathbf{s}_1$, $\mathbf{s}_2$, or the random nonce $\mathbf{y}$. How can it determine that $(\mathbf{z}, \mathbf{h}, c)$ is genuine?

The verifier uses the signer's public key $(\mathbf{A}, \mathbf{t}_1)$ to reconstruct the signer's internal vector $\mathbf{w}_1'$:
$$\mathbf{w}' = \mathbf{A}\mathbf{z} - c \mathbf{t}_1 \cdot 2^d \pmod q$$
Substituting $\mathbf{z} = \mathbf{y} + c \mathbf{s}_1$ and $\mathbf{t}_1 \cdot 2^d = \mathbf{t} - \mathbf{t}_0 = \mathbf{A}\mathbf{s}_1 + \mathbf{s}_2 - \mathbf{t}_0$:
$$\mathbf{w}' = \mathbf{A}(\mathbf{y} + c \mathbf{s}_1) - c\left(\mathbf{A}\mathbf{s}_1 + \mathbf{s}_2 - \mathbf{t}_0\right)$$
$$\mathbf{w}' = \mathbf{A}\mathbf{y} + c\mathbf{A}\mathbf{s}_1 - c\mathbf{A}\mathbf{s}_1 - c\mathbf{s}_2 + c\mathbf{t}_0$$
$$\mathbf{w}' = \mathbf{A}\mathbf{y} - c\mathbf{s}_2 + c\mathbf{t}_0 = \mathbf{w} - c\mathbf{s}_2 + c\mathbf{t}_0$$

Notice the structure of $\mathbf{w}'$:
- The dominant term is $\mathbf{w} = \mathbf{A}\mathbf{y}$, which generated the original high bits $\mathbf{w}_1$.
- The perturbation term is $-c\mathbf{s}_2 + c\mathbf{t}_0$. Because $c$, $\mathbf{s}_2$, and $\mathbf{t}_0$ are strictly bounded and small, this perturbation alters only the lowest bits of $\mathbf{w}$.
- In cases where the perturbation causes a carry rollover across the rounding boundary, the 1-bit hints in $\mathbf{h}$ instruct the algorithm whether to round up or down.
- Thus, the verifier's routine `UseHint(h, w')` reconstructs **the exact polynomial vector** $\mathbf{w}_1$:
  $$\mathbf{w}_1' = \mathbf{w}_1$$
- Finally, the verifier computes:
  $$c' = \mathcal{H}\left(\mu \,\|\, \mathbf{w}_1'\right)$$
- If $c' == c$, the algebraic identity holds. Because $\mathcal{H}$ is a cryptographic random oracle, the probability of an adversary guessing a matching challenge $c$ without satisfying the lattice equation is bounded by:
  $$\frac{1}{|\mathcal{C}|} = \frac{1}{\binom{256}{49} \cdot 2^{49}} < 2^{-256}$$

#### 2. Signature Non-Identity: Why Signatures for the Same Message Differ
A common misconception is that signing the same message twice must yield the same signature bytes. In ML-DSA-65:
- **Randomized Signing:** The masking vector $\mathbf{y}$ is sampled using fresh system entropy each time `MLDSA65.sign()` executes.
- Even for identical transaction payloads, two subsequent signing operations produce completely distinct vectors $\mathbf{y}^{(1)} \neq \mathbf{y}^{(2)}$, distinct challenge hashes $c^{(1)} \neq c^{(2)}$, and distinct signature bytes $\sigma^{(1)} \neq \sigma^{(2)}$.
- **Both signatures are 100% valid**: each satisfies the algebraic identity $c' == c$ against the sender's public key.
- The verifier **never identifies signatures by checking string/byte equality against prior signatures**. It identifies authenticity by proving the signature satisfies the lattice equation for the message digest $\mu$.

#### 3. Deterministic Binding via Canonical Integrity Locking
How does QSC guarantee that the signature binds every header, policy, and ciphertext?
1. The capsule fields are normalized into a canonical dictionary (excluding `signature` and `integrity_hash` to eliminate circular reference).
2. The dictionary is canonically formatted: keys sorted alphabetically, separators without whitespace (`","`, `":"`), UTF-8 encoded.
3. The SHA3-512 sponge computes the 512-bit `integrity_hash`.
4. **Avalanche Effect:** Altering even a single bit in any field (e.g. changing `"max_hops": 3` to `"max_hops": 4`, modifying the recipient BIC, or altering 1 byte of AES ciphertext) completely scrambles the 512-bit digest $\mu$.
5. Because $\mu$ is input into $c = \mathcal{H}(\mu \,\|\, \mathbf{w}_1)$, an altered $\mu$ yields a totally uncorrelated challenge $c'$, causing immediate rejection at Stage 4 and Stage 5.

#### 4. Replay Attacks vs Signature Re-use
Even though an authentic signature is mathematically valid forever, an adversary cannot capture a valid capsule and resend it to duplicate a financial debit. QSC defends against this at **Stage 3** (before signature verification):
- Every capsule contains a single-use `replay_token = SHA3-512(capsule_id || issued_at || sender_id || nonce)`.
- The validator tracks consumed tokens in a high-speed cache (`_seen_replay_tokens`).
- Re-transmitting an identical valid capsule is intercepted at Stage 3 (~2 µs), aborting the pipeline before expensive lattice verification executes.

---

### 2.5 AES-256-GCM (NIST SP 800-38D) &mdash; Authenticated Symmetric Encryption

Implemented in [`src/crypto/symmetric.py`](file:///c:/Users/hasan/antigravity/QSC/src/crypto/symmetric.py) using OpenSSL AEAD primitives.

#### 1. What It Really Does
AES-256-GCM (Galois/Counter Mode) provides **Authenticated Encryption with Associated Data (AEAD)**. It guarantees both confidentiality (preventing unauthorized reading of transaction amounts and account numbers) and authenticity/integrity (preventing unauthorized modification of ciphertext or associated cleartext headers).

#### 2. Where It Is Used in QSC
- **Capsule Builder ([`src/capsule/builder.py`](file:///c:/Users/hasan/antigravity/QSC/src/capsule/builder.py), Step 4):** Encrypts plaintext payload bytes using the derived 256-bit `content_key`, a fresh 96-bit random `nonce`, and binds `associated_data = capsule_id.encode('utf-8')`. Emits `payload_ciphertext`, `payload_tag` (16 bytes), and `nonce` (12 bytes).
- **Secure Receiver ([`src/capsule/receiver.py`](file:///c:/Users/hasan/antigravity/QSC/src/capsule/receiver.py), Step 4):** Decrypts `payload_ciphertext` and verifies `payload_tag` against `associated_data = capsule_id`. If even 1 bit of ciphertext, tag, or `capsule_id` is modified, OpenSSL throws an authentication failure and refuses to output decrypted plaintext.

#### 3. Mathematical Foundations: Rijndael SPN & Finite Field $GF(2^8)$
AES is a Substitution-Permutation Network (SPN) operating on a $4 \times 4$ byte state matrix over 14 rounds for 256-bit keys:
1. **SubBytes:** Non-linear byte substitution using the Rijndael S-box. Each byte is inverted in the Galois Field $GF(2^8) = \mathbb{Z}_2[X] / (X^8 + X^4 + X^3 + X + 1)$, followed by an affine transformation over $\mathbb{Z}_2$.
2. **ShiftRows:** Cyclic byte shifts in rows 1, 2, and 3 by offsets of 1, 2, and 3 bytes respectively.
3. **MixColumns:** Column-mixing linear diffusion via matrix multiplication over $GF(2^8)$ using Maximum Distance Separable (MDS) polynomials:
   $$c(x) = \{03\}x^3 + \{01\}x^2 + \{01\}x + \{02\}$$
4. **AddRoundKey:** Bitwise XOR of the state with the 128-bit round key expanded from the 256-bit master key via the Rijndael key schedule.

#### 4. Galois Counter Mode (GHASH) & Tag Authentication in $GF(2^{128})$
Confidentiality is achieved via Counter Mode ($CTR$):
$$C_i = P_i \oplus \text{AES}_K(\text{nonce} \,\|\, i)$$

Authentication is computed via polynomial evaluation over the binary Galois field:
$$GF(2^{128}) = \mathbb{Z}_2[X] / (X^{128} + X^7 + X^2 + X + 1)$$
The hash key $H$ is computed as $H = \text{AES}_K(0^{128})$. Given associated data blocks $A_1, \dots, A_u$ (`capsule_id`) and ciphertext blocks $C_1, \dots, C_v$:
$$S = \text{GHASH}_H(A, C) = \sum_{i=1}^u A_i \cdot H^{u+v+1-i} + \sum_{j=1}^v C_j \cdot H^{v+1-j} + L \cdot H$$
where $L = \text{len}(A)_{64} \,\|\, \text{len}(C)_{64}$ encodes bit lengths.
The final 128-bit authentication tag is:
$$T = S \oplus \text{AES}_K(\text{nonce} \,\|\, 0^{31} \,\|\, 1)$$
Binding `capsule_id` into the Associated Data guarantees that a ciphertext cannot be transplanted from one capsule into another without tag validation failing.

---

### 2.6 HKDF-SHA3-512 (NIST SP 800-56C Rev. 2) &mdash; Key Derivation with Domain Separation

Implemented in [`src/crypto/kdf.py`](file:///c:/Users/hasan/antigravity/QSC/src/crypto/kdf.py).

#### 1. What It Really Does
Extracts uniform entropy from the raw ML-KEM shared secret and expands it into a cryptographically strong 256-bit symmetric encryption key, while cryptographically binding the key to a specific capsule identifier and protocol domain.

#### 2. Where It Is Used in QSC
- **Capsule Builder ([`src/capsule/builder.py`](file:///c:/Users/hasan/antigravity/QSC/src/capsule/builder.py), Step 3):** Transforms the 32-byte ML-KEM shared secret $K$ into the 32-byte AES content key.
- **Secure Receiver ([`src/capsule/receiver.py`](file:///c:/Users/hasan/antigravity/QSC/src/capsule/receiver.py), Step 3):** Re-derives the identical AES content key from the decapsulated secret.

#### 3. Mathematical Foundations: Extract-then-Expand
Conforming to NIST SP 800-56C Rev. 2:
```
Raw ML-KEM-768 Secret (32 bytes) + Salt (capsule_id)
                      │
                      ▼
            [ HKDF-Extract Step ]  ──► PRK = HMAC-SHA3-512(salt, secret)
                      │
                      ▼
     [ HKDF-Expand Step with Domain Info ]
       info = "QSC-1.0 ML-KEM-768 -> AES-256-GCM payload key"
                      │
                      ▼
           AES-256-GCM Content Key (32 bytes)
```

1. **Extract Step:** Compresses entropy and breaks input correlations:
   $$\text{PRK} = \text{HMAC-SHA3-512}(\text{salt}=\text{capsule\_id}, \text{IKM}=K)$$
2. **Expand Step:** Produces desired output key material ($OKM$):
   $$\text{OKM} = \text{HMAC-SHA3-512}(\text{PRK}, \text{info} \,\|\, 0x01)[0:32]$$

#### Why Domain Separation Matters
The domain separation string (`QSC-1.0 ML-KEM-768 -> AES-256-GCM payload key`) mathematically ensures that even if an attacker reused an ML-KEM shared secret across different protocols, cipher suites, or capsule versions, the derived keys would remain statistically independent and zero information would leak.

---

### 2.7 SHA3-512 (NIST FIPS 202) &mdash; Permutation Sponge & Integrity Locking

Implemented in [`src/crypto/hashing.py`](file:///c:/Users/hasan/antigravity/QSC/src/crypto/hashing.py).

#### 1. What It Really Does
Provides collision-resistant, 512-bit cryptographic digests based on the Keccak-$f[1600]$ permutation sponge construction. It powers both deterministic integrity locking and single-use replay protection tokens.

#### 2. Where It Is Used in QSC
- **Stage 3 & Builder Step 5:** Generates `replay_token = SHA3-512(capsule_id || issued_at || sender_id || nonce)`.
- **Stage 4 & Builder Step 7:** Generates `integrity_hash = SHA3-512(canonical_json)`.
- **Internal PRF:** Serves as the underlying primitive for HKDF-SHA3-512.

#### 3. Mathematical Foundations: The Keccak Sponge Construction
SHA3-512 operates on an internal state of $b = 1600$ bits arranged as a $5 \times 5 \times 64$ three-dimensional array of lanes:
- **Bitrate ($r$):** 576 bits (the data absorption capacity per block)
- **Capacity ($c$):** 1024 bits (the security parameter against structural attacks)
- **State size ($b$):** $r + c = 576 + 1024 = 1600$ bits

The permutation function $f$ consists of **24 rounds**, each applying five algebraic operations:
1. $\theta$ (Theta): Column parity mixing & diffusion across slices.
2. $\rho$ (Rho): Cyclic bit rotation of each lane by fixed offsets.
3. $\pi$ (Pi): Fixed spatial permutation of the 25 lanes.
4. $\chi$ (Chi): Non-linear row mapping: $A[x, y] \leftarrow A[x, y] \oplus (\neg A[x+1, y] \land A[x+2, y])$. Provides non-linearity without traditional S-boxes.
5. $\iota$ (Iota): Addition of round constants to break symmetry between rounds.

#### Quantum Collision Resistance
Against classical attacks, SHA3-512 provides 256 bits of collision resistance and 512 bits of pre-image resistance. Against quantum adversaries using Grover search or Brassard-Høyer-Tapp claw-finding algorithms, pre-image resistance is $\mathcal{O}(2^{256})$ and collision resistance is $\mathcal{O}(2^{c/3}) = \mathcal{O}(2^{341})$, establishing a massive quantum security margin.

---

## 3. Data Schema & Wire Format

The reference implementation defines the schema in [`src/capsule/models.py`](src/capsule/models.py) and serializes it in [`src/capsule/wire.py`](src/capsule/wire.py).

### 3.1 JSON Wire Representation
```json
{
  "version": "QSC-1.0",
  "capsule_id": "qsc_7f2b918a3e0c45d1",
  "issued_at": "2026-09-13T01:30:00Z",
  "expires_at": "2026-09-13T01:35:00Z",
  "replay_token": "a4f89b12... (128 hex chars SHA3-512 digest)",
  "sender_id": "BARCGB22XXX",
  "recipient_id": "HDFCINBBXXX",
  "kem_ciphertext": "7c12d... (Base64 ML-KEM-768 ciphertext, 1088 bytes raw)",
  "payload_ciphertext": "e8810... (Base64 AES-256-GCM encrypted payload)",
  "payload_tag": "33f01... (Base64 16-byte GCM authentication tag)",
  "nonce": "91a2b... (Base64 12-byte GCM initialization vector)",
  "integrity_hash": "b9012... (128 hex chars canonical SHA3-512 digest)",
  "signature": "d2218... (Base64 ML-DSA-65 lattice signature, 3309 bytes raw)",
  "policy": {
    "classification": "CONFIDENTIAL",
    "jurisdiction": "UK",
    "max_hops": 3,
    "allowed_channels": ["HTTPS", "KAFKA", "MQ", "SWIFT"]
  }
}
```

### 3.2 Canonical Wire Encoding
To ensure deterministic verification and honest byte-level packet inspection:
1. Serialization uses canonical JSON formatting: keys sorted alphabetically, no insignificant whitespace (`separators=(',', ':')`), UTF-8 encoded.
2. The byte sequence transmitted over the wire is identical to the byte stream mapped by the Wireshark-style Hex Inspector in [`src/capsule/wire.py`](src/capsule/wire.py).

---

## 4. Field Specifications

### 4.1 Header & Metadata Fields
- **`version`**: `string` &mdash; Protocol specification identifier (`QSC-1.0`). Verified at Stage 1.
- **`capsule_id`**: `string` &mdash; Globally unique 64-bit hex token prefixed with `qsc_`. Serves as the unique message identifier, HKDF salt, and AEAD associated data.
- **`issued_at`**: `string (ISO-8601 UTC)` &mdash; Timestamp of capsule construction (e.g., `2026-09-13T01:30:00Z`).
- **`expires_at`**: `string (ISO-8601 UTC)` &mdash; Hard expiry deadline. Validated at Stage 2. Default validity window: 300 seconds (5 minutes).
- **`replay_token`**: `string (hex, 128 characters)` &mdash; Cryptographic binding derived via `SHA3-512(capsule_id || issued_at || sender_id || nonce)`. Validated at Stage 3.
- **`sender_id`**: `string` &mdash; Institutional BIC or service identifier of the origin client (e.g., `BARCGB22XXX`).
- **`recipient_id`**: `string` &mdash; Institutional BIC or service identifier of the destination receiver (e.g., `HDFCINBBXXX`).
- **`policy`**: `object` &mdash; Mandatory governance parameters:
  - `classification`: Data classification level (`RESTRICTED`, `CONFIDENTIAL`, `SECRET`).
  - `jurisdiction`: Regulatory territory (`UK`, `EU`, `US`).
  - `max_hops`: Maximum allowed proxy/queue hops.
  - `allowed_channels`: Permitted transport routes (`["HTTPS", "KAFKA", "MQ", "SWIFT"]`).

### 4.2 Cryptographic Payloads
- **`kem_ciphertext`**: `string (base64)` &mdash; ML-KEM-768 ciphertext (1088 bytes decoded) encapsulating the 256-bit shared secret.
- **`payload_ciphertext`**: `string (base64)` &mdash; AES-256-GCM encrypted financial payload.
- **`payload_tag`**: `string (base64)` &mdash; 16-byte authentication tag produced by AES-256-GCM.
- **`nonce`**: `string (base64)` &mdash; 12-byte (96-bit) cryptographically random initialization vector.

### 4.3 Verification & Authenticity
- **`integrity_hash`**: `string (hex, 128 characters)` &mdash; SHA3-512 digest computed over canonical representation of all fields except `signature` and `integrity_hash`.
- **`signature`**: `string (base64)` &mdash; ML-DSA-65 post-quantum digital signature (3309 bytes decoded) over `integrity_hash`, verified with the sender's registered public key.

---

## 5. Capsule Construction Pipeline (8 Steps)

Implemented in [`CapsuleBuilder.build_capsule()`](src/capsule/builder.py):

```
[ Step 1: Identifiers & Timestamps ]
   └── Generate unique capsule_id (qsc_<hex>), issued_at, and expires_at (now + 300s)

[ Step 2: ML-KEM-768 Key Encapsulation ]
   └── Encapsulate 256-bit shared secret (K) against recipient's ML-KEM public key
   └── Output: shared_secret, kem_ciphertext (1088 bytes)

[ Step 3: Key Derivation via HKDF-SHA3-512 (SP 800-56C) ]
   └── content_key = HKDF-SHA3-512(secret=K, salt=capsule_id, info="QSC-1.0/AES-256-GCM")
   └── Ensures K is never used directly as an encryption key and binds key to capsule_id

[ Step 4: AES-256-GCM Authenticated Encryption ]
   └── Encrypt payload bytes using content_key, fresh 96-bit nonce, and associated_data=capsule_id
   └── Output: payload_ciphertext, payload_tag (16 bytes), nonce (12 bytes)

[ Step 5: Single-Use Replay Token Generation ]
   └── replay_token = SHA3-512(capsule_id + issued_at + sender_id + nonce)

[ Step 6: Canonical Field Serialization ]
   └── Populate pre-capsule object with header, ciphertexts, and policy
   └── Extract canonical dictionary (excluding signature and integrity_hash)

[ Step 7: SHA3-512 Canonical Integrity Digest ]
   └── Compute 512-bit hash over canonical UTF-8 JSON bytes -> integrity_hash

[ Step 8: ML-DSA-65 Lattice Signature ]
   └── Sign integrity_hash with sender's private ML-DSA-65 key -> signature
   └── Assemble complete QuantumSecurityCapsule object
```

---

## 6. 5-Stage Zero-Trust Validation Pipeline

Implemented in [`CapsuleValidator.validate_detailed()`](src/capsule/validator.py).

Every capsule must traverse all five stages in strict sequence, cheapest first. The validator **fails closed** at the earliest failed stage, shielding expensive lattice signature calculations from malformed, expired, or replayed denial-of-service traffic:

```
┌──────────────────────────────────────────────────────────────────────────────┐
│ STAGE 1: Protocol Version Check (~1 µs)                                      │
│ Checks version == "QSC-1.0". Rejects incompatible wire versions instantly.   │
└──────────────────────────────────────┬───────────────────────────────────────┘
                                       │ PASS
                                       ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│ STAGE 2: Freshness Window Enforcement (~7 µs)                                │
│ Validates current_time <= expires_at. Rejects expired capsules without crypto.│
└──────────────────────────────────────┬───────────────────────────────────────┘
                                       │ PASS
                                       ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│ STAGE 3: Replay Cache Verification (~2 µs)                                   │
│ Queries replay registry. If replay_token seen, reject immediately.          │
└──────────────────────────────────────┬───────────────────────────────────────┘
                                       │ PASS
                                       ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│ STAGE 4: Integrity Lock (SHA3-512) (~60 µs)                                  │
│ Re-computes canonical digest. Fails if even 1 bit in headers/ciphertexts flipped.│
└──────────────────────────────────────┬───────────────────────────────────────┘
                                       │ PASS
                                       ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│ STAGE 5: Origin Authenticity Verification (ML-DSA-65) (~17 ms)               │
│ Verifies lattice signature against sender's public key. Non-repudiation lock.│
└──────────────────────────────────────┬───────────────────────────────────────┘
                                       │ ALL PASS
                                       ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│ COMMIT REPLAY TOKEN & RELEASE TO SETTLEMENT ENGINE                           │
│ Replay token committed to registry ONLY after all 5 stages succeed.          │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## 7. Decapsulation & Settlement Pipeline

Implemented in [`SecureReceiver.settle_with_report()`](src/capsule/receiver.py):
1. **Validation Prerequisite:** Capsule must achieve `ValidationReport.accepted == True` across all 5 stages.
2. **ML-KEM-768 Decapsulation:** Recipient decapsulates `kem_ciphertext` with its private ML-KEM key to recover the 256-bit shared secret $K$.
3. **Content Key Reconstruction:** Re-derives the identical 256-bit AES key via `HKDF-SHA3-512(secret=K, salt=capsule_id)`.
4. **AES-256-GCM Authenticated Decryption:** Decrypts `payload_ciphertext` using recovered `content_key`, `nonce`, `payload_tag`, and `associated_data=capsule_id`.
5. **Execution & Audit Dispatch:** Passes verified plaintext payload to core settlement ledger and records telemetry.
