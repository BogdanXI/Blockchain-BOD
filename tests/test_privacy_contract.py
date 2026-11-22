"""Automated checks for the public checkpoint privacy contract."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

from bod_evidence_envelope import create_evidence_envelope
from bod_portable import create_portable_checkpoint, repository_snapshot


def test_portable_checkpoint_contains_only_documented_top_level_fields(tmp_path: Path) -> None:
    repo = tmp_path / "private-workspace-name"
    repo.mkdir()
    (repo / "README.md").write_text("public test fixture\n", encoding="utf-8")
    subprocess.run(["git", "-C", str(repo), "init", "-q"], check=True)
    subprocess.run(["git", "-C", str(repo), "add", "README.md"], check=True)

    snapshot = repository_snapshot(repo)
    envelope = create_evidence_envelope(
        project_id="privacy-test-project",
        protocol_version="0.1",
        state_root=snapshot["state_root"],
        predecessor_state_root=None,
        transition_id="privacy-test-transition",
        evidence=(),
        capture_boundary="tracked-files",
    )
    checkpoint = create_portable_checkpoint(snapshot=snapshot, envelope=envelope)
    serialized = json.dumps(checkpoint, sort_keys=True)

    assert set(checkpoint) == {"schema", "snapshot", "envelope", "checkpoint_id"}
    assert set(checkpoint["snapshot"]) == {"schema", "files", "state_root"}
    assert all(set(entry) == {"path", "sha256", "size"} for entry in checkpoint["snapshot"]["files"])
    assert str(tmp_path) not in serialized
    assert str(repo) not in serialized
    assert "private-workspace-name" not in serialized


def test_eas_schema_is_a_fixed_commitment_allowlist() -> None:
    schema_source = (Path(__file__).resolve().parents[1] / "tools/eas/schema.mjs").read_text(encoding="utf-8")
    expected = (
        "bytes32 projectId, bytes32 checkpointId, bytes32 gitCommit, bytes32 stateRoot, "
        "bytes32 manifestHash, bytes32 evidenceRoot, uint64 sequence"
    )
    assert expected in schema_source
