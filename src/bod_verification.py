"""Trust-aware verification reports for BOD Evidence Fabric.

The verifier deliberately separates cryptographic integrity from the truth of an
external claim. A valid digest proves only that the referenced bytes match the
declared digest; it does not prove that the producer's statement is true.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, Mapping

from bod_evidence_envelope import EvidenceEnvelopeError, EvidenceEnvelopeV0_1, verify_chain


@dataclass(frozen=True)
class EvidencePolicy:
    """Optional policy for what evidence a verifier is willing to accept.

    This is a trust policy, not a truth oracle. It constrains accepted evidence
    references but cannot establish the semantic correctness of the referenced
    claim.
    """

    required_types: frozenset[str] = frozenset()
    trusted_issuers: frozenset[str] = frozenset()
    require_uri: bool = False

    def evaluate(self, envelope: EvidenceEnvelopeV0_1) -> tuple[str, ...]:
        types = {item.evidence_type for item in envelope.evidence}
        missing = sorted(self.required_types - types)
        failures: list[str] = [f"missing required evidence type: {item}" for item in missing]

        if self.trusted_issuers:
            for item in envelope.evidence:
                if item.issuer is not None and item.issuer not in self.trusted_issuers:
                    failures.append(f"untrusted evidence issuer: {item.issuer}")

        if self.require_uri:
            for item in envelope.evidence:
                if item.uri is None:
                    failures.append(f"evidence reference has no retrieval URI: {item.evidence_type}")

        return tuple(failures)


@dataclass(frozen=True)
class VerificationReport:
    """Machine-readable verification result with explicit trust boundaries."""

    status: str
    integrity: str
    lineage: str
    evidence_binding: str
    semantic_truth: str
    availability: str
    policy: str
    reasons: tuple[str, ...] = field(default_factory=tuple)

    @property
    def valid(self) -> bool:
        return self.status == "VALID_INTEGRITY"

    def to_document(self) -> dict:
        return {
            "schema": "bod-verification-report-v0.1",
            "status": self.status,
            "integrity": self.integrity,
            "lineage": self.lineage,
            "evidence_binding": self.evidence_binding,
            "semantic_truth": self.semantic_truth,
            "availability": self.availability,
            "policy": self.policy,
            "reasons": list(self.reasons),
        }


def verify_envelopes(
    envelopes: Iterable[EvidenceEnvelopeV0_1],
    *,
    policy: EvidencePolicy | None = None,
) -> VerificationReport:
    items = tuple(envelopes)
    if not items:
        return VerificationReport(
            "INVALID", "INVALID", "NOT_CHECKED", "NOT_CHECKED",
            "NOT_ASSERTED", "UNKNOWN", "NOT_CHECKED", ("empty evidence set",)
        )

    reasons: list[str] = []
    integrity = "VALID"
    try:
        for item in items:
            if item.envelope_id != item.commitment():
                raise EvidenceEnvelopeError("envelope commitment mismatch")
    except EvidenceEnvelopeError as exc:
        return VerificationReport(
            "INVALID", "INVALID", "NOT_CHECKED", "NOT_CHECKED",
            "NOT_ASSERTED", "UNKNOWN", "NOT_CHECKED", (str(exc),)
        )

    try:
        verify_chain(items)
        lineage = "VALID"
    except EvidenceEnvelopeError as exc:
        lineage = "INVALID"
        reasons.append(str(exc))

    binding = "VALID"
    active_policy = policy or EvidencePolicy()
    policy_failures = list(
        failure for item in items for failure in active_policy.evaluate(item)
    )
    if policy_failures:
        policy_status = "REJECTED"
        reasons.extend(policy_failures)
    else:
        policy_status = "ACCEPTED"

    if lineage != "VALID" or policy_failures:
        return VerificationReport(
            "INVALID", integrity, lineage, binding,
            "NOT_ASSERTED", "UNKNOWN", policy_status, tuple(reasons)
        )

    return VerificationReport(
        "VALID_INTEGRITY",
        integrity,
        lineage,
        binding,
        "NOT_ASSERTED",
        "UNKNOWN",
        policy_status,
        tuple(reasons),
    )
