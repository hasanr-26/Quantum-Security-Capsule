"""
Performance benchmark for the QSC cryptographic pipeline.

Measures the real cost of every primitive on the machine it runs on. No
figures are quoted from a paper - each number below comes from timing the
actual operation in a loop and reporting the median.

    python src/demo/benchmark.py
    python src/demo/benchmark.py --iterations 200
"""

import argparse
import os
import statistics
import sys
import time
from typing import Callable, List

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from src.capsule import CapsuleBuilder, CapsuleValidator, SecureReceiver
from src.capsule.wire import to_wire_bytes
from src.crypto import compute_sha3_512, derive_payload_key, MLDSA65, MLKEM768
from src.crypto.symmetric import encrypt_aes_256_gcm
from src.server.payloads import build_payload

RULE = "=" * 78


def measure(label: str, operation: Callable[[], object], iterations: int) -> dict:
    """Times an operation and returns median, mean and p95 in milliseconds."""
    samples: List[float] = []
    for _ in range(iterations):
        start = time.perf_counter()
        operation()
        samples.append((time.perf_counter() - start) * 1000)

    samples.sort()
    return {
        "label": label,
        "median": statistics.median(samples),
        "mean": statistics.fmean(samples),
        "p95": samples[min(int(len(samples) * 0.95), len(samples) - 1)],
        "ops_per_sec": 1000 / statistics.median(samples) if samples else 0,
    }


def print_table(title: str, rows: List[dict]) -> None:
    print(f"\n{title}")
    print(f"  {'Operation':<40} {'median':>9} {'mean':>9} {'p95':>9} {'ops/s':>9}")
    print(f"  {'-' * 40} {'-' * 9} {'-' * 9} {'-' * 9} {'-' * 9}")
    for row in rows:
        print(
            f"  {row['label']:<40} {row['median']:>8.3f}ms {row['mean']:>8.3f}ms "
            f"{row['p95']:>8.3f}ms {row['ops_per_sec']:>9.1f}"
        )


def main() -> int:
    parser = argparse.ArgumentParser(description="Benchmark the QSC pipeline.")
    parser.add_argument("--iterations", type=int, default=100)
    args = parser.parse_args()
    n = args.iterations

    print(RULE)
    print(" QSC CRYPTOGRAPHIC PERFORMANCE BENCHMARK")
    print(RULE)
    print(f"  Python      {sys.version.split()[0]}")
    print(f"  Platform    {sys.platform}")
    print(f"  Iterations  {n} per operation")

    # ---- Primitives -------------------------------------------------------
    kem_public, kem_private = MLKEM768.generate_keypair()
    dsa_public, dsa_private = MLDSA65.generate_keypair()
    shared_secret, kem_ciphertext = MLKEM768.encapsulate(kem_public)
    digest = compute_sha3_512(b"benchmark digest")
    signature = MLDSA65.sign(dsa_private, digest)
    payload, _ = build_payload("pacs008")

    print_table("POST-QUANTUM PRIMITIVES", [
        measure("ML-KEM-768 keygen (FIPS 203)", MLKEM768.generate_keypair, n),
        measure("ML-KEM-768 encapsulate", lambda: MLKEM768.encapsulate(kem_public), n),
        measure("ML-KEM-768 decapsulate",
                lambda: MLKEM768.decapsulate(kem_private, kem_ciphertext), n),
        measure("ML-DSA-65 keygen (FIPS 204)", MLDSA65.generate_keypair, n),
        measure("ML-DSA-65 sign", lambda: MLDSA65.sign(dsa_private, digest), n),
        measure("ML-DSA-65 verify",
                lambda: MLDSA65.verify(dsa_public, digest, signature), n),
    ])

    print_table("CLASSICAL PRIMITIVES", [
        measure("AES-256-GCM encrypt (payload)",
                lambda: encrypt_aes_256_gcm(shared_secret, payload, b"aad"), n),
        measure("SHA3-512 digest (payload)", lambda: compute_sha3_512(payload), n),
        measure("HKDF-SHA3-512 derive",
                lambda: derive_payload_key(shared_secret, "qsc_bench"), n),
    ])

    # ---- Full pipeline ----------------------------------------------------
    builder = CapsuleBuilder("BARCGB22XXX", dsa_private)

    def build_one():
        return builder.build_capsule("HDFCINBBXXX", kem_public, payload)

    capsule = build_one()

    def validate_one():
        # A fresh validator each time, so the replay cache never short-circuits.
        return CapsuleValidator().validate_detailed(capsule, dsa_public)

    receiver = SecureReceiver("HDFCINBBXXX", kem_private, CapsuleValidator())

    print_table("END-TO-END CAPSULE LIFECYCLE", [
        measure("Build capsule (8-step pipeline)", build_one, n),
        measure("Validate capsule (5 stages)", validate_one, n),
        measure("Decrypt payload", lambda: receiver.decrypt_payload(capsule), n),
    ])

    # ---- Size overhead ----------------------------------------------------
    wire = to_wire_bytes(capsule)
    print("\nSIZE OVERHEAD")
    print(f"  {'Plaintext payload':<40} {len(payload):>8} B")
    print(f"  {'ML-KEM-768 ciphertext':<40} {len(kem_ciphertext):>8} B")
    print(f"  {'ML-DSA-65 signature':<40} {len(signature):>8} B")
    print(f"  {'SHA3-512 integrity hash (hex)':<40} {len(capsule.integrity_hash):>8} B")
    print(f"  {'Replay token (hex)':<40} {len(capsule.replay_token):>8} B")
    print(f"  {'Total capsule on the wire':<40} {len(wire):>8} B")
    print(f"  {'Fixed overhead':<40} {len(wire) - len(payload):>8} B")
    print(f"  {'Expansion ratio':<40} {len(wire) / len(payload):>7.2f}x")

    print(f"\n{RULE}")
    print("  Overhead is fixed, not proportional: the KEM ciphertext and signature")
    print("  are constant sizes, so the ratio falls as payloads grow.")
    print(RULE)
    return 0


if __name__ == "__main__":
    sys.exit(main())
