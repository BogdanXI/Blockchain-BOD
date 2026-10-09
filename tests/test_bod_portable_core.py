import json
import subprocess
import sys
from pathlib import Path

import pytest

from bod_evidence_envelope import EvidenceEnvelopeError, create_evidence_envelope
from bod_portable import create_portable_checkpoint, parse_portable, repository_snapshot


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
