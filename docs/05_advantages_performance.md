# 05 — Advantages, Performance and Scalability

## 1. Advantages of Message-Centric Security

### 1.1 Protection survives the hop

TLS 1.3 is strong cryptography, and nothing in this project disputes that. Its
limitation is structural rather than mathematical: **the protection ends where
the tunnel ends.** In a real payments estate, a wire message terminates TLS
several times before it settles — at the CDN edge, the WAF, the API gateway, the
service mesh sidecar, the message broker, the corporate inspection appliance.
At every one of those points the payload exists as plaintext in a process's
memory.

A capsule is sealed before it reaches the wire and is opened only by the
settlement engine holding the ML-KEM private key. Intermediaries route it
without being able to read it.

### 1.2 Harvest Now, Decrypt Later is neutralised

An adversary recording TLS traffic today is betting on a future
Cryptographically Relevant Quantum Computer. When one arrives, Shor's algorithm
recovers the ECDHE session keys of every archived handshake, and the recorded
plaintext becomes readable retroactively.

Shor's algorithm solves the hidden subgroup problem over abelian groups — that
is what makes integer factorisation and discrete logarithms fall. Module-LWE,
the problem underneath ML-KEM and ML-DSA, exposes no such structure. The best
known quantum attack is Grover-accelerated lattice sieving, which delivers a
sub-quadratic speed-up and is answered by parameter selection.

The practical consequence: traffic captured today stays sealed tomorrow.

### 1.3 Security properties travel with the message

Because every control is bound into the capsule itself, the guarantees hold on
any transport — HTTPS, Kafka, IBM MQ, SWIFT FIN, a file on disk, a USB stick:

| Property | Mechanism | Enforced at |
| :--- | :--- | :--- |
| Confidentiality | AES-256-GCM under an ML-KEM-768 established key | Receiver |
| Origin authenticity | ML-DSA-65 signature over the integrity hash | Stage 5 |
| Integrity | SHA3-512 over all canonical fields | Stage 4 |
| Freshness | Explicit `expires_at` bound | Stage 2 |
| Replay resistance | Single-use SHA3-512 replay token | Stage 3 |
| Policy binding | Jurisdiction and hop limit inside the hashed region | Stage 4 |

### 1.4 Incremental adoption

QSC runs *inside* the existing TLS estate rather than replacing it. No network
re-architecture, no certificate authority migration, no coordinated flag day.
A single endpoint pair can adopt capsules while every other route is untouched.

---

## 2. Measured Performance

All figures below were produced by `src/demo/benchmark.py` on the development
machine, timing the real primitives — not quoted from literature.

```
Python 3.12.8 / win32 / 60 iterations per operation
Payload: ISO 20022 pacs.008, 2142 bytes
```

### 2.1 Post-quantum primitives

| Operation | Median | Mean | p95 | ops/sec |
| :--- | ---: | ---: | ---: | ---: |
| ML-KEM-768 keygen | 5.07 ms | 5.25 ms | 7.31 ms | 197 |
| ML-KEM-768 encapsulate | 6.25 ms | 6.27 ms | 8.10 ms | 160 |
| ML-KEM-768 decapsulate | 9.05 ms | 8.92 ms | 10.48 ms | 111 |
| ML-DSA-65 keygen | 14.27 ms | 14.32 ms | 16.67 ms | 70 |
| ML-DSA-65 sign | 75.47 ms | 93.82 ms | 255.14 ms | 13 |
| ML-DSA-65 verify | 17.23 ms | 16.92 ms | 18.93 ms | 58 |

### 2.2 Classical primitives

| Operation | Median | ops/sec |
| :--- | ---: | ---: |
| AES-256-GCM encrypt | 0.005 ms | ~204,000 |
| SHA3-512 digest | 0.013 ms | ~78,700 |
| HKDF-SHA3-512 derive | 0.013 ms | ~75,500 |

The symmetric layer is effectively free. All cost sits in the lattice
operations.

### 2.3 End-to-end lifecycle

| Stage | Median |
| :--- | ---: |
| Build capsule (8-step pipeline) | 73.4 ms |
| Validate capsule (5 stages) | 16.8 ms |
| Decrypt payload | 8.6 ms |

Within validation, the stage timings differ by three orders of magnitude:

| Stage | Control | Typical cost |
| :--- | :--- | ---: |
| 1 | Protocol version | ~1 µs |
| 2 | Freshness window | ~7 µs |
| 3 | Replay token | ~2 µs |
| 4 | Integrity lock (SHA3-512) | ~60 µs |
| 5 | Origin signature (ML-DSA-65) | ~17 ms |

This ordering is deliberate. The cheap structural checks run first, so a
malformed or replayed capsule is discarded for microseconds and never reaches
the expensive lattice verifier. Under a flood of junk traffic, the node spends
almost nothing rejecting it.

### 2.4 An honest caveat on these numbers

**These timings measure a pure-Python implementation, and they are dominated by
that choice rather than by the algorithms.** `kyber-py` and `dilithium-py` are
correctness-focused reference implementations validated against the NIST ACVP
test vectors — ideal for a system whose purpose is to be inspected and trusted,
but one to two orders of magnitude slower than optimised native code.

ML-DSA signing is the clearest case. Its 75 ms median and 255 ms p95 reflect
FIPS 204's rejection-sampling loop: signing retries until it finds a signature
with acceptable norms, so the iteration count — and the runtime — varies per
call. In an AVX2-optimised C implementation the same operation costs well under
a millisecond.

For production deployment the primitives would be backed by `liboqs`,
AWS-LC or an equivalent, which the `MLKEM768` / `MLDSA65` wrapper classes are
structured to allow as a drop-in change. Nothing above those classes would move.

---

## 3. Size Overhead

| Component | Size |
| :--- | ---: |
| ML-KEM-768 ciphertext | 1088 B |
| ML-DSA-65 signature | 3309 B |
| SHA3-512 integrity hash (hex) | 128 B |
| Replay token (hex) | 128 B |
| Headers, timestamps, policy | ~250 B |
| **Fixed overhead (base64 encoded)** | **~7.3 KB** |

The overhead is **constant, not proportional**. Base64 transport encoding
inflates the binary components by 4/3, which accounts for most of the total.

| Payload | Capsule size | Expansion |
| :--- | ---: | ---: |
| 258 B card authorisation | ~7.6 KB | 29x |
| 2.1 KB ISO 20022 pacs.008 | 9.5 KB | 4.4x |
| 100 KB batch file | ~107 KB | 1.07x |
| 1 MB document | ~1.007 MB | 1.007x |

For a CHAPS payment of tens of millions of pounds, 7 KB of armour is not a
meaningful cost. For high-frequency small messages it matters, and the mitigation
is well understood: switch the wire encoding from base64 JSON to CBOR or raw
binary, which removes the 33% encoding penalty outright.

---

## 4. Scalability

### 4.1 The pipeline parallelises cleanly

Capsule construction and validation are **stateless per message** — no shared
mutable state, no coordination between messages. Throughput scales horizontally
with settlement nodes. The only shared component is the replay cache.

### 4.2 Replay cache

The reference implementation holds replay tokens in an in-process set. In
production this becomes a distributed store:

- **Redis / Valkey** with TTL set to the capsule validity window, so entries
  expire automatically and the cache stays bounded rather than growing forever.
- Memory cost is ~64 bytes per in-flight token. At 10,000 messages/sec with a
  300-second TTL, the working set is roughly 3 million tokens — under 200 MB,
  trivially shardable by token prefix.
- The correctness requirement is atomic test-and-set; `SET NX` provides it.

### 4.3 Where to spend optimisation effort

1. **Native primitives.** The single highest-leverage change, worth one to two
   orders of magnitude on the lattice operations.
2. **Signature batching.** ML-DSA verification of many capsules from one sender
   can be amortised.
3. **Key reuse.** ML-KEM keypairs are long-lived; only the encapsulation is
   per-message. Keygen cost does not appear on the hot path.
4. **Binary wire format.** CBOR removes the base64 penalty.
5. **Hardware isolation.** Private keys belong in an HSM or enclave; the
   architecture already confines them to the receiver boundary.

---

## 5. Reproducing These Figures

```bash
python src/demo/benchmark.py --iterations 100
```

Numbers will differ by machine. The relationships — symmetric operations being
effectively free, lattice operations dominating, overhead staying fixed as
payloads grow — hold regardless.
