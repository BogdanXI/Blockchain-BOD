import json
from pathlib import Path
import subprocess
import sys

import pytest

from src.bod_project_state import ProjectStateManifestV0_1
from src.bod_repository_adapter import RepositoryCaptureError, capture_repository, snapshot_repository


def git(repo: Path, *args: str) -> str:
    result = subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True, text=True)
    return result.stdout.strip()


def make_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "project"
    repo.mkdir()
    git(repo, "init")
    git(repo, "config", "user.email", "test@example.invalid")
    git(repo, "config", "user.name", "Test")
    (repo / "src").mkdir()
    (repo / "src" / "app.py").write_text("print('v1')\n", encoding="utf-8")
    (repo / "package-lock.json").write_text('{"lockfileVersion":3}\n', encoding="utf-8")
    (repo / "ignored.tmp").write_text("untracked", encoding="utf-8")
    git(repo, "add", "src/app.py", "package-lock.json")
    git(repo, "commit", "-m", "initial")
    return repo


def test_snapshot_uses_tracked_content_and_lockfiles(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    snapshot = snapshot_repository(repo)
    assert snapshot.head_commit == git(repo, "rev-parse", "HEAD")
    assert len(snapshot.artifact_refs) == 2
    assert all("ignored.tmp" not in ref for ref in snapshot.artifact_refs)
    assert len(snapshot.dependency_lock_hash) == 64


def test_working_tree_change_changes_state_root_but_untracked_file_does_not(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    a, ma, _ = capture_repository(repo, project_id="demo", next_action="continue")
    (repo / "ignored.tmp").write_text("different untracked data", encoding="utf-8")
    b, mb, _ = capture_repository(repo, project_id="demo", next_action="continue")
    assert ma.state_root() == mb.state_root()
    assert a == b

    (repo / "src" / "app.py").write_text("print('v2')\n", encoding="utf-8")
    c, mc, _ = capture_repository(repo, project_id="demo", next_action="continue")
    assert mc.state_root() != ma.state_root()
    assert c != a


def test_repository_location_and_branch_are_runtime_only(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    artifact_a, manifest_a, _ = capture_repository(repo, project_id="demo", next_action="continue")
    clone = tmp_path / "relocated"
    subprocess.run(["git", "clone", str(repo), str(clone)], check=True, capture_output=True)
    git(clone, "checkout", "-b", "runtime-branch")
    artifact_b, manifest_b, _ = capture_repository(clone, project_id="demo", next_action="continue")
    assert manifest_a.state_root() == manifest_b.state_root()
    assert artifact_a != artifact_b
    assert manifest_a.runtime_metadata["repository_path"] != manifest_b.runtime_metadata["repository_path"]
    assert manifest_a.runtime_metadata["git_branch"] != manifest_b.runtime_metadata["git_branch"]


def test_cli_capture_repo_round_trip(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    artifact = tmp_path / "state.artifact.json"
    evidence = tmp_path / "evidence.json"
    cmd = [
        sys.executable,
        "scripts/bod_continuity.py",
        "capture-repo",
        str(repo),
        str(artifact),
        "--project-id",
        "demo",
        "--next-action",
        "resume",
        "--evidence",
        str(evidence),
    ]
    captured = subprocess.run(cmd, check=True, capture_output=True, text=True)
    payload = json.loads(captured.stdout)
    recovered = ProjectStateManifestV0_1.from_artifact(artifact.read_bytes())
    assert recovered.state_root() == payload["state_root"]
    assert payload["tracked_artifacts"] == 2
    assert json.loads(evidence.read_text())["git_head"] == git(repo, "rev-parse", "HEAD")


def test_non_git_path_is_rejected(tmp_path: Path) -> None:
    with pytest.raises(RepositoryCaptureError):
        snapshot_repository(tmp_path)
