import json
import subprocess
import sys
from pathlib import Path

import pytest

from bod_evidence_envelope import EvidenceEnvelopeError, create_evidence_envelope
from bod_portable import (
    SNAPSHOT_DOMAIN,
    SNAPSHOT_SCHEMA,
    canonical_json,
    create_evidence_bundle,
    create_portable_checkpoint,
    parse_portable,
    repository_snapshot,
    sha256_bytes,
    verify_evidence_bundle,
    verify_portable_chain,
    verify_portable_graph,
    verify_snapshot,
)


def test_capture_verify_recover_cli(tmp_path):
    artifact = tmp_path / "checkpoint.json"
    capture = subprocess.run(
        [sys.executable, "-m", "src.bod_cli", "capture", ".", "--project", "bod-test", "--out", str(artifact)],
        capture_output=True, text=True, check=False,
    )
    assert capture.returncode == 0, capture.stdout + capture.stderr
    verify = subprocess.run(
        [sys.executable, "-m", "src.bod_cli", "verify", str(artifact), "--portable"],
        capture_output=True, text=True, check=False,
    )
    assert verify.returncode == 0, verify.stdout + verify.stderr
    recover = subprocess.run(
        [sys.executable, "-m", "src.bod_cli", "recover", str(artifact)],
        capture_output=True, text=True, check=False,
    )
    assert recover.returncode == 0, recover.stdout + recover.stderr
    assert json.loads(recover.stdout)["status"] == "RECOVERY_VERIFIED"


def test_portable_checkpoint_binds_snapshot_and_envelope():
    snapshot = repository_snapshot(Path("."))
    envelope = create_evidence_envelope(
        project_id="p", protocol_version="0.1", state_root=snapshot["state_root"],
        predecessor_state_root=None, transition_id="t", evidence=(), capture_boundary="test",
    )
    checkpoint = create_portable_checkpoint(snapshot=snapshot, envelope=envelope)
    parse_portable(checkpoint)
    checkpoint["snapshot"]["files"][0]["size"] += 1
    with pytest.raises(EvidenceEnvelopeError):
        parse_portable(checkpoint)


def test_cli_rejects_mutation(tmp_path):
    artifact = tmp_path / "checkpoint.json"
    subprocess.run(
        [sys.executable, "-m", "src.bod_cli", "capture", ".", "--project", "bod-test", "--out", str(artifact)],
        check=True,
    )
    value = json.loads(artifact.read_text())
    value["envelope"]["transition_id"] = "tampered"
    artifact.write_text(json.dumps(value))
    verify = subprocess.run(
        [sys.executable, "-m", "src.bod_cli", "verify", str(artifact), "--portable"],
        capture_output=True, text=True, check=False,
    )
    assert verify.returncode != 0


def test_snapshot_rejects_unsafe_paths_and_noncanonical_entries():
    snapshot = repository_snapshot(Path("."))
    unsafe = json.loads(json.dumps(snapshot))
    unsafe["files"][0]["path"] = "../outside"
    with pytest.raises(EvidenceEnvelopeError):
        verify_snapshot(unsafe)

    boolean_size = json.loads(json.dumps(snapshot))
    boolean_size["files"][0]["size"] = True
    with pytest.raises(EvidenceEnvelopeError):
        verify_snapshot(boolean_size)

    unsorted = json.loads(json.dumps(snapshot))
    unsorted["files"] = list(reversed(unsorted["files"]))
    with pytest.raises(EvidenceEnvelopeError):
        verify_snapshot(unsorted)


def test_snapshot_hashes_symlink_target_not_external_file_contents(tmp_path):
    import hashlib
    import os

    repository = tmp_path / "repository"
    repository.mkdir()
    external_file = tmp_path / "outside.txt"
    external_file.write_text("external payload must not be read", encoding="utf-8")
    link = repository / "linked.txt"
    link.symlink_to(external_file)

    subprocess.run(["git", "-C", str(repository), "init"], check=True, capture_output=True)
    subprocess.run(["git", "-C", str(repository), "add", "--", "linked.txt"], check=True, capture_output=True)

    snapshot = repository_snapshot(repository)
    entry = snapshot["files"][0]
    link_target = os.fsencode(os.readlink(link))

    assert entry["path"] == "linked.txt"
    assert entry["sha256"] == hashlib.sha256(link_target).hexdigest()
    assert entry["size"] == len(link_target)
    assert entry["sha256"] != hashlib.sha256(external_file.read_bytes()).hexdigest()


def _synthetic_snapshot(label: str) -> dict:
    files = [{"path": "state.txt", "sha256": sha256_bytes(label.encode()), "size": len(label)}]
    durable = {"schema": SNAPSHOT_SCHEMA, "files": files}
    return {**durable, "state_root": sha256_bytes(SNAPSHOT_DOMAIN + canonical_json(durable))}


def test_portable_graph_verifies_forks_and_independent_cli(tmp_path):
    from bod_evidence_envelope import create_evidence_envelope

    snapshots = [_synthetic_snapshot(name) for name in ("genesis", "branch-b", "branch-c")]
    genesis = create_evidence_envelope(
        project_id="graph-project", protocol_version="0.1", state_root=snapshots[0]["state_root"],
        predecessor_state_root=None, transition_id="genesis", evidence=(), capture_boundary="test",
    )
    children = [
        create_evidence_envelope(
            project_id="graph-project", protocol_version="0.1", state_root=snapshot["state_root"],
            predecessor_state_root=snapshots[0]["state_root"], transition_id=f"branch-{index}",
            evidence=(), capture_boundary="test",
        )
        for index, snapshot in enumerate(snapshots[1:], start=1)
    ]
    checkpoints = [
        create_portable_checkpoint(snapshot=snapshot, envelope=envelope)
        for snapshot, envelope in [(snapshots[0], genesis), *zip(snapshots[1:], children)]
    ]

    graph = verify_portable_graph(checkpoints)
    assert graph["fork_points"] == (snapshots[0]["state_root"],)
    assert set(graph["heads"]) == {snapshot["state_root"] for snapshot in snapshots[1:]}
    with pytest.raises(EvidenceEnvelopeError, match="verify it as a graph"):
        verify_portable_chain(checkpoints)

    artifact = tmp_path / "forked-checkpoints.json"
    artifact.write_text(json.dumps({"checkpoints": checkpoints}), encoding="utf-8")
    independent = subprocess.run(
        [sys.executable, "scripts/independent_verify.py", str(artifact), "--graph"],
        capture_output=True, text=True, check=False,
    )
    assert independent.returncode == 0, independent.stdout + independent.stderr
    assert json.loads(independent.stdout)["status"] == "VALID_INTEGRITY"

    cli = subprocess.run(
        [sys.executable, "-m", "src.bod_cli", "verify", str(artifact), "--portable", "--graph"],
        capture_output=True, text=True, check=False,
    )
    assert cli.returncode == 0, cli.stdout + cli.stderr
    assert json.loads(cli.stdout)["canonical_head"] is None


def test_self_contained_evidence_bundle_round_trip_and_tamper_detection(tmp_path):
    import hashlib

    from bod_evidence_envelope import EvidenceReferenceV0_1

    payload = b'{"predicateType":"https://slsa.dev/provenance/v1","subject":[]}'
    digest = hashlib.sha256(payload).hexdigest()
    snapshot = _synthetic_snapshot("bundle-state")
    envelope = create_evidence_envelope(
        project_id="bundle-project", protocol_version="0.1",
        state_root=snapshot["state_root"], predecessor_state_root=None,
        transition_id="release-1",
        evidence=[EvidenceReferenceV0_1(
            evidence_type="slsa-provenance",
            digest=digest,
            media_type="application/vnd.in-toto+json",
        )],
        capture_boundary="test",
    )
    checkpoint = create_portable_checkpoint(snapshot=snapshot, envelope=envelope)
    bundle = create_evidence_bundle(checkpoint=checkpoint, payloads={digest: payload})
    result = verify_evidence_bundle(bundle)
    assert result["payloads_complete"] is True
    assert result["evidence_objects"] == 1
    assert result["payload_bytes"] == len(payload)
    assert result["semantic_truth"] == "NOT_ASSERTED"
    assert result["bundle_authenticity"] == "NOT_ASSERTED"

    tampered = json.loads(json.dumps(bundle))
    tampered["objects"][0]["data_base64"] = "eA=="
    # Recompute outer commitment to exercise payload-level digest validation.
    from bod_portable import BUNDLE_DOMAIN
    tampered["bundle_id"] = sha256_bytes(BUNDLE_DOMAIN + canonical_json({
        "schema": tampered["schema"],
        "checkpoint": tampered["checkpoint"],
        "objects": tampered["objects"],
    }))
    with pytest.raises(EvidenceEnvelopeError, match="size mismatch|digest mismatch"):
        verify_evidence_bundle(tampered)


def test_self_contained_evidence_bundle_requires_every_referenced_payload():
    from bod_evidence_envelope import EvidenceReferenceV0_1
    payload = b"missing evidence"
    digest = sha256_bytes(payload)
    snapshot = _synthetic_snapshot("missing-payload")
    envelope = create_evidence_envelope(
        project_id="bundle-project", protocol_version="0.1",
        state_root=snapshot["state_root"], predecessor_state_root=None,
        transition_id="release-1",
        evidence=[EvidenceReferenceV0_1(
            evidence_type="test-report", digest=digest, media_type="text/plain",
        )],
        capture_boundary="test",
    )
    checkpoint = create_portable_checkpoint(snapshot=snapshot, envelope=envelope)
    with pytest.raises(EvidenceEnvelopeError, match="payload set must exactly match"):
        create_evidence_bundle(checkpoint=checkpoint, payloads={})


def test_bundle_cli_round_trip(tmp_path):
    import hashlib

    from bod_evidence_envelope import EvidenceReferenceV0_1
    payload = b"fixture evidence"
    digest = hashlib.sha256(payload).hexdigest()
    payload_path = tmp_path / "evidence.json"
    payload_path.write_bytes(payload)
    snapshot = _synthetic_snapshot("bundle-cli")
    envelope = create_evidence_envelope(
        project_id="bundle-cli", protocol_version="0.1",
        state_root=snapshot["state_root"], predecessor_state_root=None,
        transition_id="release-1",
        evidence=[EvidenceReferenceV0_1(
            evidence_type="test-fixture", digest=digest, media_type="application/json",
        )],
        capture_boundary="test",
    )
    checkpoint_path = tmp_path / "checkpoint.json"
    checkpoint_path.write_text(json.dumps(create_portable_checkpoint(snapshot=snapshot, envelope=envelope)))
    bundle_path = tmp_path / "bundle.json"
    create = subprocess.run(
        [sys.executable, "-m", "src.bod_cli", "bundle-create", str(checkpoint_path),
         "--payload", f"{digest}={payload_path}", "--out", str(bundle_path)],
        capture_output=True, text=True, check=False,
    )
    assert create.returncode == 0, create.stdout + create.stderr
    verify = subprocess.run(
        [sys.executable, "-m", "src.bod_cli", "bundle-verify", str(bundle_path)],
        capture_output=True, text=True, check=False,
    )
    assert verify.returncode == 0, verify.stdout + verify.stderr
    assert json.loads(verify.stdout)["status"] == "VALID_SELF_CONTAINED_BUNDLE"

    independent = subprocess.run(
        [sys.executable, "scripts/independent_verify.py", str(bundle_path)],
        capture_output=True, text=True, check=False,
    )
    assert independent.returncode == 0, independent.stdout + independent.stderr
    assert json.loads(independent.stdout)["status"] == "VALID_SELF_CONTAINED_BUNDLE"
