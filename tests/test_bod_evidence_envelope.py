import hashlib
import json

import pytest

from src.bod_evidence_envelope import (
    EvidenceEnvelopeError,
    EvidenceEnvelopeV0_1,
    EvidenceReferenceV0_1,
    create_evidence_envelope,
    verify_chain,
)


ROOT_A = "11" * 32
ROOT_B = "22" * 32
ROOT_C = "33" * 32
DIGEST_A = "aa" * 32
DIGEST_B = "bb" * 32


def _ref(digest=DIGEST_A):
    return EvidenceReferenceV0_1(
        evidence_type="slsa.provenance",
        digest=digest,
        media_type="application/vnd.in-toto+json",
        uri="https://example.invalid/provenance.json",
        issuer="example-issuer",
    )


def _envelope(root, predecessor, transition, refs=(_ref(),), project="project-A"):
    return create_evidence_envelope(
        project_id=project,
        protocol_version="v0.1",
        state_root=root,
        predecessor_state_root=predecessor,
        transition_id=transition,
        evidence=refs,
        capture_boundary="git-checkout-to-test-report",
    )


def test_commitment_is_deterministic_across_evidence_order():
    first = _envelope(ROOT_A, None, "genesis", (_ref(DIGEST_A), _ref(DIGEST_B)))
    second = _envelope(ROOT_A, None, "genesis", (_ref(DIGEST_B), _ref(DIGEST_A)))
    assert first.commitment() == second.commitment()


def test_domain_separation_is_not_plain_document_hash():
    envelope = _envelope(ROOT_A, None, "genesis")
    plain = hashlib.sha256(envelope.canonical_bytes()).hexdigest()
    assert envelope.commitment() != plain


def test_round_trip_validates_envelope_id():
    envelope = _envelope(ROOT_A, None, "genesis")
    recovered = EvidenceEnvelopeV0_1.from_document(envelope.to_document())
    assert recovered.envelope_id == envelope.envelope_id
    assert recovered.commitment() == envelope.commitment()


def test_mutation_changes_commitment_and_is_rejected():
    envelope = _envelope(ROOT_A, None, "genesis")
    document = envelope.to_document()
    document["transition_id"] = "mutated"
    with pytest.raises(EvidenceEnvelopeError):
        EvidenceEnvelopeV0_1.from_document(document)


def test_external_reference_contains_digest_not_payload():
    envelope = _envelope(ROOT_A, None, "genesis")
    reference = envelope.to_document()["evidence"][0]
    assert reference["digest"] == f"sha256:{DIGEST_A}"
    assert "payload" not in reference


def test_single_genesis_chain_is_valid():
    verify_chain([
        _envelope(ROOT_A, None, "genesis"),
        _envelope(ROOT_B, ROOT_A, "t1"),
        _envelope(ROOT_C, ROOT_B, "t2"),
    ])


@pytest.mark.parametrize(
    "chain",
    [
        lambda: [_envelope(ROOT_A, None, "genesis"), _envelope(ROOT_C, ROOT_B, "gap")],
        lambda: [_envelope(ROOT_A, None, "genesis"), _envelope(ROOT_B, ROOT_A, "t1"), _envelope(ROOT_C, ROOT_A, "fork")],
        lambda: [_envelope(ROOT_A, None, "g1"), _envelope(ROOT_B, None, "g2")],
        lambda: [_envelope(ROOT_A, None, "g"), _envelope(ROOT_B, ROOT_A, "t1"), _envelope(ROOT_C, ROOT_B, "t2"), _envelope("44" * 32, "55" * 32, "orphan")],
    ],
)
def test_adversarial_chain_is_rejected(chain):
    with pytest.raises(EvidenceEnvelopeError):
        verify_chain(chain())


def test_project_boundary_is_rejected():
    verify = [
        _envelope(ROOT_A, None, "genesis"),
        _envelope(ROOT_B, ROOT_A, "cross-project", project="project-B"),
    ]
    with pytest.raises(EvidenceEnvelopeError):
        verify_chain(verify)


def test_canonical_document_is_stable():
    envelope = _envelope(ROOT_A, None, "genesis")
    encoded = envelope.canonical_bytes()
    assert encoded == json.dumps(
        envelope.durable_document(), ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


@pytest.mark.parametrize(
    "document",
    [
        lambda e: {**e.to_document(), "envelope_id": "00" * 32},
        lambda e: {**e.to_document(), "state_root": "not-a-hash"},
        lambda e: {**e.to_document(), "evidence": [{**e.to_document()["evidence"][0], "digest": "sha256:not-a-hash"}]},
        lambda e: {**e.to_document(), "schema": "bod-evidence-envelope-v0.2"},
    ],
)
def test_unsupported_or_mutated_documents_are_rejected(document):
    envelope = _envelope(ROOT_A, None, "genesis")
    with pytest.raises(EvidenceEnvelopeError):
        EvidenceEnvelopeV0_1.from_document(document(envelope))
