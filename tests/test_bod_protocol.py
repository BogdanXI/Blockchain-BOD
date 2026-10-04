import hmac
import pytest

from src.bod_protocol import (
    BODProtocol,
    ProtocolError,
    commitment,
    fixture_verifier,
    sign_fixture,
    canonical_bytes,
)


def make_task(key=b"requester-key"):
    unsigned = {
        "project_id": "project-1",
        "parent_state_root": "root-0",
        "task_spec_hash": "spec-hash",
        "acceptance_policy_hash": "policy-1",
        "reward_amount_bod": 100,
        "deadline": 1000,
        "requester": "alice",
        "request_nonce": 1,
    }
    task_id = commitment("task", unsigned)
    payload = {"task_id": task_id, **unsigned}
    return payload, sign_fixture(key, "task", payload)


def make_candidate(task_id, key=b"agent-key", nonce=1, artifact="artifact-a"):
    unsigned = {
        "task_id": task_id,
        "parent_state_root": "root-0",
        "candidate_state_root": "root-1",
        "result_artifact_hash": artifact,
        "execution_manifest_hash": "manifest-a",
        "evidence_root": "evidence-a",
        "executor": "agent",
        "candidate_nonce": nonce,
        "bond_amount_bod": 20,
    }
    candidate_id = commitment("candidate", unsigned)
    payload = {"candidate_id": candidate_id, **unsigned}
    return payload, sign_fixture(key, "candidate", payload)


def make_verification(candidate, key=b"verifier-key", nonce=1):
    candidate_hash = candidate["candidate_id"]
    unsigned = {
        "candidate_id": candidate["candidate_id"],
        "candidate_hash": candidate_hash,
        "evidence_root": candidate["evidence_root"],
        "acceptance_policy_hash": "policy-1",
        "verification_result": "VALID",
        "verifier": "verifier",
        "verification_epoch": 1,
        "verifier_nonce": nonce,
        "report_hash": "report-a",
    }
    verification_id = commitment("verification", unsigned)
    payload = {"verification_id": verification_id, **unsigned}
    return payload, sign_fixture(key, "verification", payload)


def test_canonical_bytes_are_stable_and_order_independent():
    assert canonical_bytes({"b": 2, "a": 1}) == canonical_bytes({"a": 1, "b": 2})


def test_signed_field_mutation_changes_commitment():
    task, _ = make_task()
    mutated = dict(task)
    mutated["reward_amount_bod"] += 1
    assert commitment("task", task) != commitment("task", mutated)


def test_invalid_signature_is_rejected():
    task, _ = make_task()
    verifier = fixture_verifier({"alice": b"requester-key"})
    protocol = BODProtocol("root-0", verifier)
    with pytest.raises(ProtocolError, match="invalid signature"):
        protocol.create_task(task, "bad")


def test_full_lifecycle_and_two_candidates():
    keys = {
        "alice": b"requester-key",
        "agent": b"agent-key",
        "verifier": b"verifier-key",
    }
    protocol = BODProtocol("root-0", fixture_verifier(keys))
    task, task_sig = make_task()
    protocol.create_task(task, task_sig)

    c1, s1 = make_candidate(task["task_id"], artifact="artifact-a")
    c2, s2 = make_candidate(task["task_id"], nonce=2, artifact="artifact-b")
    protocol.submit_candidate(c1, s1)
    protocol.submit_candidate(c2, s2)

    v1, vs1 = make_verification(c1)
    v2, vs2 = make_verification(c2, nonce=2)
    protocol.verify_candidate(v1, vs1)
    protocol.verify_candidate(v2, vs2)

    settlement = protocol.settle(
        task["task_id"], c1["candidate_id"], "verification-root",
        "root-1", "economic-outcome", 1
    )
    assert settlement in protocol.state.settlements
    assert protocol.state.current_state_root == "root-1"
    assert protocol.state.candidates[c1["candidate_id"]]["status"] == "SELECTED"
    assert protocol.state.candidates[c2["candidate_id"]]["status"] == "REJECTED"


def test_wrong_parent_candidate_is_rejected():
    keys = {"alice": b"requester-key", "agent": b"agent-key"}
    protocol = BODProtocol("root-0", fixture_verifier(keys))
    task, sig = make_task()
    protocol.create_task(task, sig)
    candidate, _ = make_candidate(task["task_id"])
    candidate["parent_state_root"] = "other-root"
    candidate["candidate_id"] = commitment(
        "candidate", {k: v for k, v in candidate.items() if k != "candidate_id"}
    )
    sig = sign_fixture(b"agent-key", "candidate", candidate)
    with pytest.raises(ProtocolError, match="candidate parent"):
        protocol.submit_candidate(candidate, sig)


def test_replayed_candidate_nonce_is_rejected():
    keys = {"alice": b"requester-key", "agent": b"agent-key"}
    protocol = BODProtocol("root-0", fixture_verifier(keys))
    task, sig = make_task()
    protocol.create_task(task, sig)
    c1, s1 = make_candidate(task["task_id"])
    protocol.submit_candidate(c1, s1)
    c2, s2 = make_candidate(task["task_id"])
    c2["candidate_id"] = commitment("candidate", {k: v for k, v in c2.items() if k != "candidate_id"})
    s2 = sign_fixture(b"agent-key", "candidate", c2)
    with pytest.raises(ProtocolError, match="replayed candidate nonce"):
        protocol.submit_candidate(c2, s2)


def test_evidence_mismatch_is_rejected():
    keys = {"alice": b"requester-key", "agent": b"agent-key", "verifier": b"verifier-key"}
    protocol = BODProtocol("root-0", fixture_verifier(keys))
    task, sig = make_task()
    protocol.create_task(task, sig)
    candidate, csig = make_candidate(task["task_id"])
    protocol.submit_candidate(candidate, csig)
    verification, vsig = make_verification(candidate)
    verification["evidence_root"] = "different"
    verification["verification_id"] = commitment("verification", {k: v for k, v in verification.items() if k != "verification_id"})
    vsig = sign_fixture(b"verifier-key", "verification", verification)
    with pytest.raises(ProtocolError, match="evidence root"):
        protocol.verify_candidate(verification, vsig)


def test_settlement_requires_valid_verification():
    keys = {"alice": b"requester-key", "agent": b"agent-key", "verifier": b"verifier-key"}
    protocol = BODProtocol("root-0", fixture_verifier(keys))
    task, sig = make_task()
    protocol.create_task(task, sig)
    candidate, csig = make_candidate(task["task_id"])
    protocol.submit_candidate(candidate, csig)
    with pytest.raises(ProtocolError, match="lacks valid verification"):
        protocol.settle(task["task_id"], candidate["candidate_id"], "vr", "root-1", "eo", 1)
