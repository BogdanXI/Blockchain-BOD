#!/usr/bin/env python3
"""Public adversarial smoke test for BOD Protocol v0.1.

The goal is deliberately narrow: demonstrate that locally plausible state
transitions are rejected when a protocol invariant is violated.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.bod_protocol import BODProtocol, ProtocolError, commitment, fixture_verifier, sign_fixture

KEYS = {"alice": b"requester-key", "agent": b"agent-key", "verifier": b"verifier-key"}


def make_task():
    unsigned = {
        "project_id": "break-state-machine",
        "parent_state_root": "root-0",
        "task_spec_hash": "spec",
        "acceptance_policy_hash": "policy-1",
        "reward_amount_bod": 100,
        "deadline": 1000,
        "requester": "alice",
        "request_nonce": 1,
    }
    payload = {"task_id": commitment("task", unsigned), **unsigned}
    return payload, sign_fixture(KEYS["alice"], "task", payload)


def make_candidate(task_id, *, nonce=1, evidence="evidence-a", parent="root-0"):
    unsigned = {
        "task_id": task_id,
        "parent_state_root": parent,
        "candidate_state_root": "root-1",
        "result_artifact_hash": "artifact-a",
        "execution_manifest_hash": "manifest-a",
        "evidence_root": evidence,
        "executor": "agent",
        "candidate_nonce": nonce,
        "bond_amount_bod": 20,
    }
    payload = {"candidate_id": commitment("candidate", unsigned), **unsigned}
    return payload, sign_fixture(KEYS["agent"], "candidate", payload)


def make_verification(candidate, *, nonce=1, evidence=None, policy="policy-1", result="VALID"):
    unsigned = {
        "candidate_id": candidate["candidate_id"],
        "candidate_hash": candidate["candidate_id"],
        "evidence_root": candidate["evidence_root"] if evidence is None else evidence,
        "acceptance_policy_hash": policy,
        "verification_result": result,
        "verifier": "verifier",
        "verification_epoch": 1,
        "verifier_nonce": nonce,
        "report_hash": "report-a",
    }
    payload = {"verification_id": commitment("verification", unsigned), **unsigned}
    return payload, sign_fixture(KEYS["verifier"], "verification", payload)


def expect(label, fn):
    try:
        fn()
    except ProtocolError:
        print(f"REJECT {label}")
        return
    raise AssertionError(f"attack unexpectedly accepted: {label}")


def main():
    protocol = BODProtocol("root-0", fixture_verifier(KEYS))
    task, task_sig = make_task()
    protocol.create_task(task, task_sig)
    valid, valid_sig = make_candidate(task["task_id"])
    protocol.submit_candidate(valid, valid_sig)
    verification, verification_sig = make_verification(valid)
    protocol.verify_candidate(verification, verification_sig)
    print("PASS candidate-valid")

    bad_sig = make_candidate(task["task_id"], nonce=2)[0]
    expect("invalid-signature", lambda: protocol.submit_candidate(bad_sig, "not-a-signature"))

    evidence_bad, evidence_bad_sig = make_verification(valid, nonce=2, evidence="wrong-evidence")
    expect("wrong-evidence", lambda: protocol.verify_candidate(evidence_bad, evidence_bad_sig))

    replay, replay_sig = make_candidate(task["task_id"], nonce=1)
    expect("replay", lambda: protocol.submit_candidate(replay, replay_sig))

    stale, stale_sig = make_candidate(task["task_id"], nonce=3, parent="old-root")
    expect("state-conflict", lambda: protocol.submit_candidate(stale, stale_sig))

    policy_bad, policy_bad_sig = make_verification(valid, nonce=3, policy="wrong-policy")
    expect("policy-violation", lambda: protocol.verify_candidate(policy_bad, policy_bad_sig))

    no_valid = BODProtocol("root-0", fixture_verifier(KEYS))
    no_valid.create_task(task, task_sig)
    candidate, candidate_sig = make_candidate(task["task_id"])
    no_valid.submit_candidate(candidate, candidate_sig)
    expect("settlement-without-valid-verification", lambda: no_valid.settle(
        task["task_id"], candidate["candidate_id"], "verification-root", "root-1", "economic", 1
    ))


if __name__ == "__main__":
    main()
