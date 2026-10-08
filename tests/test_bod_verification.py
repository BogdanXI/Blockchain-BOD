import json
import subprocess
import sys
from pathlib import Path

import pytest

from src.bod_evidence_envelope import EvidenceEnvelopeError, EvidenceReferenceV0_1, create_evidence_envelope
from src.bod_verification import EvidencePolicy, verify_envelopes


ROOT_A = "11" * 32
ROOT_B = "22" * 32
DIGEST = "aa" * 32


def env(root, predecessor=None, transition="t", issuer="trusted"):
    return create_evidence_envelope(
        project_id="project-A",
        protocol_version="v0.1",
        state_root=root,
        predecessor_state_root=predecessor,
        transition_id=transition,
        evidence=(
            EvidenceReferenceV0_1(
                "slsa.provenance",
                DIGEST,
                "application/vnd.in-toto+json",
                uri="https://example.invalid/evidence",
                issuer=issuer,
            ),
        ),
        capture_boundary="source-to-build",
    )


def test_integrity_does_not_claim_semantic_truth():
    report = verify_envelopes([env(ROOT_A)])
    assert report.status == "VALID_INTEGRITY"
    assert report.semantic_truth == "NOT_ASSERTED"
    assert report.availability == "UNKNOWN"


def test_policy_can_require_evidence_and_trusted_issuer():
    report = verify_envelopes(
        [env(ROOT_A)],
        policy=EvidencePolicy(
            required_types=frozenset({"slsa.provenance"}),
            trusted_issuers=frozenset({"trusted"}),
            require_uri=True,
        ),
    )
    assert report.valid


def test_policy_rejects_untrusted_issuer():
    report = verify_envelopes(
        [env(ROOT_A, issuer="attacker")],
        policy=EvidencePolicy(trusted_issuers=frozenset({"trusted"})),
    )
    assert not report.valid
    assert any("untrusted evidence issuer" in reason for reason in report.reasons)


def test_policy_rejects_missing_required_evidence():
    report = verify_envelopes(
        [create_evidence_envelope(
            project_id="project-A",
            protocol_version="v0.1",
            state_root=ROOT_A,
            predecessor_state_root=None,
            transition_id="genesis",
            evidence=(),
            capture_boundary="source",
        )],
        policy=EvidencePolicy(required_types=frozenset({"slsa.provenance"})),
    )
    assert not report.valid


def test_chain_integrity_report_is_valid():
    report = verify_envelopes([env(ROOT_A, transition="genesis"), env(ROOT_B, ROOT_A)])
    assert report.status == "VALID_INTEGRITY"
    assert report.lineage == "VALID"


@pytest.mark.parametrize("mutator", [
    lambda d: {**d, "state_root": "ff" * 32},
    lambda d: {**d, "transition_id": "attacker-transition"},
])
def test_mutation_fails_closed(mutator):
    document = mutator(env(ROOT_A).to_document())
    with pytest.raises(EvidenceEnvelopeError):
        from src.bod_evidence_envelope import EvidenceEnvelopeV0_1
        EvidenceEnvelopeV0_1.from_document(document)


def test_independent_verifier_accepts_reference_document(tmp_path: Path):
    document = env(ROOT_A).to_document()
    path = tmp_path / "envelope.json"
    path.write_text(json.dumps(document), encoding="utf-8")
    result = subprocess.run(
        [sys.executable, "scripts/independent_verify.py", str(path)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert '"status": "VALID_INTEGRITY"' in result.stdout


def test_independent_verifier_rejects_mutation(tmp_path: Path):
    document = env(ROOT_A).to_document()
    document["transition_id"] = "mutated"
    path = tmp_path / "envelope.json"
    path.write_text(json.dumps(document), encoding="utf-8")
    result = subprocess.run(
        [sys.executable, "scripts/independent_verify.py", str(path)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode != 0
