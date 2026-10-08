from src.bod_evidence_envelope import EvidenceReferenceV0_1, create_evidence_envelope
from src.bod_verify_simple import verify_envelopes

ROOT = '11' * 32
DIGEST = 'aa' * 32


def make_envelope():
    return create_evidence_envelope(
        project_id='project-A', protocol_version='v0.1', state_root=ROOT,
        predecessor_state_root=None, transition_id='genesis',
        evidence=(EvidenceReferenceV0_1('slsa.provenance', DIGEST, 'application/json'),),
        capture_boundary='source-to-build',
    )


def test_integrity_report_is_explicit():
    report = verify_envelopes([make_envelope()])
    assert report['status'] == 'VALID_INTEGRITY'
    assert report['semantic_truth'] == 'NOT_ASSERTED'
    assert report['availability'] == 'UNKNOWN'


def test_mutation_fails_closed():
    envelope = make_envelope()
    document = envelope.to_document()
    document['transition_id'] = 'mutated'
    try:
        from src.bod_evidence_envelope import EvidenceEnvelopeV0_1
        EvidenceEnvelopeV0_1.from_document(document)
    except Exception:
        return
    raise AssertionError('mutated envelope was accepted')
