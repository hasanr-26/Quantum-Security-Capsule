import base64
import time
from dataclasses import dataclass, field, asdict
from typing import Set, Tuple, Dict, Any, List

from src.crypto import (
    compute_sha3_512,
    canonicalize_json,
    MLDSA65
)
from src.utils import is_expired
from src.capsule.models import QuantumSecurityCapsule


@dataclass
class StageResult:
    """Outcome of a single zero-trust validation stage."""
    stage: int
    name: str
    control: str
    status: str  # PASS | FAIL | SKIPPED
    detail: str
    elapsed_us: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ValidationReport:
    """Full diagnostic trace of a capsule passing through the validator."""
    accepted: bool
    reason: str
    stages: List[StageResult] = field(default_factory=list)
    total_us: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "accepted": self.accepted,
            "reason": self.reason,
            "total_us": round(self.total_us, 2),
            "stages": [s.to_dict() for s in self.stages],
        }


# The fixed zero-trust pipeline. Order matters: cheap structural checks run
# before expensive lattice verification, so a malformed capsule is discarded
# without ever touching the signature verifier.
STAGE_DEFINITIONS = [
    (1, "Protocol Version", "Schema conformance"),
    (2, "Freshness Window", "TTL / expiry enforcement"),
    (3, "Replay Token", "SHA3-512 single-use token"),
    (4, "Integrity Lock", "SHA3-512 canonical digest"),
    (5, "Origin Signature", "ML-DSA-65 verification (FIPS 204)"),
]


class CapsuleValidator:
    """
    Validates Quantum Security Capsules before decryption.

    Verifies, in order:
    1. Version match & schema integrity
    2. Expiry & freshness timestamps
    3. Replay protection token has not been consumed
    4. Deterministic SHA3-512 integrity hash
    5. Post-Quantum ML-DSA-65 digital signature against the sender's public key

    Every stage must pass. The pipeline fails closed at the first failure and
    the replay token is only consumed once the capsule is fully accepted.
    """

    def __init__(self):
        # Replay protection store (In-memory registry; production would use Redis / Distributed KV)
        self._seen_replay_tokens: Set[str] = set()

    @property
    def replay_cache_size(self) -> int:
        """Number of replay tokens consumed so far."""
        return len(self._seen_replay_tokens)

    def validate_capsule(
        self,
        capsule: QuantumSecurityCapsule,
        sender_public_dsa_key: bytes
    ) -> Tuple[bool, str]:
        """
        Runs the complete 5-stage validation pipeline.

        Returns (is_valid, reason).
        """
        report = self.validate_detailed(capsule, sender_public_dsa_key)
        return report.accepted, report.reason

    def validate_detailed(
        self,
        capsule: QuantumSecurityCapsule,
        sender_public_dsa_key: bytes
    ) -> ValidationReport:
        """
        Runs the pipeline and returns a per-stage diagnostic trace with timings.

        Stages after a failure are reported as SKIPPED rather than silently
        omitted, so the caller can see exactly where the capsule was stopped.
        """
        stages: List[StageResult] = []
        pipeline_start = time.perf_counter()

        def record(index: int, status: str, detail: str, elapsed_us: float = 0.0) -> StageResult:
            num, name, control = STAGE_DEFINITIONS[index]
            result = StageResult(num, name, control, status, detail, round(elapsed_us, 2))
            stages.append(result)
            return result

        def skip_remaining(from_index: int) -> None:
            for i in range(from_index, len(STAGE_DEFINITIONS)):
                record(i, "SKIPPED", "Not evaluated - pipeline already failed closed.")

        def finish(accepted: bool, reason: str) -> ValidationReport:
            total_us = (time.perf_counter() - pipeline_start) * 1_000_000
            return ValidationReport(accepted, reason, stages, total_us)

        # Stage 1: Version Check
        t0 = time.perf_counter()
        if capsule.version != "QSC-1.0":
            reason = f"Unsupported QSC version: {capsule.version}"
            record(0, "FAIL", reason, (time.perf_counter() - t0) * 1e6)
            skip_remaining(1)
            return finish(False, reason)
        record(0, "PASS", f"Capsule declares {capsule.version}.", (time.perf_counter() - t0) * 1e6)

        # Stage 2: Timestamp & Expiry Check
        t0 = time.perf_counter()
        if is_expired(capsule.expires_at):
            reason = f"Capsule expired at {capsule.expires_at}"
            record(1, "FAIL", reason, (time.perf_counter() - t0) * 1e6)
            skip_remaining(2)
            return finish(False, reason)
        record(
            1, "PASS",
            f"Within validity window, expires {capsule.expires_at}.",
            (time.perf_counter() - t0) * 1e6,
        )

        # Stage 3: Replay Protection Check
        t0 = time.perf_counter()
        if capsule.replay_token in self._seen_replay_tokens:
            reason = (
                f"Replay attack detected! Token {capsule.replay_token[:16]}... "
                "already consumed."
            )
            record(2, "FAIL", reason, (time.perf_counter() - t0) * 1e6)
            skip_remaining(3)
            return finish(False, reason)
        record(
            2, "PASS",
            f"Token {capsule.replay_token[:16]}... unseen "
            f"({self.replay_cache_size} in cache).",
            (time.perf_counter() - t0) * 1e6,
        )

        # Stage 4: Integrity Lock Verification (SHA3-512)
        t0 = time.perf_counter()
        canonical_bytes = canonicalize_json(capsule.get_canonical_fields())
        computed_hash = compute_sha3_512(canonical_bytes)
        elapsed = (time.perf_counter() - t0) * 1e6
        if computed_hash != capsule.integrity_hash:
            reason = "Integrity Lock failure: Capsule contents modified in transit."
            record(
                3, "FAIL",
                f"{reason} Expected {capsule.integrity_hash[:16]}..., "
                f"recomputed {computed_hash[:16]}...",
                elapsed,
            )
            skip_remaining(4)
            return finish(False, reason)
        record(3, "PASS", f"Digest matches: {computed_hash[:16]}...", elapsed)

        # Stage 5: PQC Digital Signature Verification (ML-DSA-65)
        t0 = time.perf_counter()
        try:
            signature_bytes = base64.b64decode(capsule.signature)
        except Exception:
            reason = "Malformed signature encoding."
            record(4, "FAIL", reason, (time.perf_counter() - t0) * 1e6)
            return finish(False, reason)

        is_sig_valid = MLDSA65.verify(
            public_key=sender_public_dsa_key,
            message_digest=capsule.integrity_hash,
            signature=signature_bytes
        )
        elapsed = (time.perf_counter() - t0) * 1e6
        if not is_sig_valid:
            reason = "Digital Signature Verification failed: Invalid ML-DSA signature."
            record(4, "FAIL", reason, elapsed)
            return finish(False, reason)
        record(
            4, "PASS",
            f"ML-DSA-65 signature verified ({len(signature_bytes)} bytes).",
            elapsed,
        )

        # Register replay token only after every control has passed.
        self._seen_replay_tokens.add(capsule.replay_token)
        return finish(True, "Validation successful")
