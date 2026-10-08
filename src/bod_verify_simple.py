from src.bod_evidence_envelope import EvidenceEnvelopeError, EvidenceEnvelopeV0_1, verify_chain

def verify_envelopes(envelopes):
    items=tuple(envelopes)
    if not items: raise EvidenceEnvelopeError('empty evidence set')
    for item in items:
        if item.envelope_id != item.commitment(): raise EvidenceEnvelopeError('envelope commitment mismatch')
    verify_chain(items)
    return {'status':'VALID_INTEGRITY','semantic_truth':'NOT_ASSERTED','availability':'UNKNOWN'}
