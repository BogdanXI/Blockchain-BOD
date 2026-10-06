from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
import subprocess
from typing import Iterable, Sequence

from src.bod_continuity import capture_from_document
from src.bod_project_state import ProjectStateManifestV0_1


class RepositoryCaptureError(ValueError):
    """Repository state cannot be captured deterministically."""


LOCKFILE_NAMES = frozenset(
    {
        "Cargo.lock",
        "Gemfile.lock",
        "Pipfile.lock",
        "composer.lock",
        "go.sum",
        "package-lock.json",
        "pnpm-lock.yaml",
        "poetry.lock",
        "uv.lock",
        "yarn.lock",
    }
)


@dataclass(frozen=True)
class RepositorySnapshot:
    repository_root: Path
    head_commit: str
    branch_name: str
    artifact_refs: tuple[str, ...]
    dependency_lock_hash: str

    def runtime_metadata(self) -> dict[str, str]:
        # Provenance only: deliberately excluded from the durable State Root.
        return {
            "repository_path": str(self.repository_root),
            "git_branch": self.branch_name,
            "capture_adapter": "repository-v0.1",
        }


def _run_git(repository_root: Path, *args: str) -> bytes:
    try:
        completed = subprocess.run(
            ["git", "-C", str(repository_root), *args],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        detail = ""
        if isinstance(exc, subprocess.CalledProcessError):
            detail = exc.stderr.decode("utf-8", errors="replace").strip()
        raise RepositoryCaptureError(detail or f"git command failed: {' '.join(args)}") from exc
    return completed.stdout


def _repository_root(path: str | Path) -> Path:
    candidate = Path(path).expanduser().resolve()
    root = _run_git(candidate, "rev-parse", "--show-toplevel").decode("utf-8").strip()
    resolved = Path(root).resolve()
    if candidate != resolved and resolved not in candidate.parents:
        raise RepositoryCaptureError("path is not inside the resolved Git repository")
    return resolved


def _tracked_paths(repository_root: Path) -> tuple[str, ...]:
    raw = _run_git(repository_root, "ls-files", "-z")
    paths = tuple(item.decode("utf-8") for item in raw.split(b"\0") if item)
    if len(paths) != len(set(paths)):
        raise RepositoryCaptureError("git returned duplicate tracked paths")
    return tuple(sorted(paths))


def _hash_tracked_entry(repository_root: Path, relative_path: str) -> tuple[str, bytes]:
    path = repository_root / relative_path
    try:
        stat_result = path.lstat()
    except FileNotFoundError:
        marker = b"missing\0" + relative_path.encode("utf-8")
        return "missing", marker

    if path.is_symlink():
        target = os.readlink(path)
        payload = b"symlink\0" + target.encode("utf-8")
        return "symlink", payload
    if not path.is_file():
        raise RepositoryCaptureError(f"tracked path is not a regular file or symlink: {relative_path}")
    return "file", path.read_bytes()


def _artifact_refs(repository_root: Path, tracked_paths: Sequence[str]) -> tuple[str, ...]:
    refs: list[str] = []
    for relative_path in tracked_paths:
        kind, payload = _hash_tracked_entry(repository_root, relative_path)
        digest = hashlib.sha256(payload).hexdigest()
        refs.append(f"repo:{kind}:{relative_path}:sha256:{digest}")
    return tuple(refs)


def _dependency_lock_hash(repository_root: Path, tracked_paths: Iterable[str]) -> str:
    records: list[dict[str, str]] = []
    for relative_path in tracked_paths:
        if Path(relative_path).name not in LOCKFILE_NAMES:
            continue
        kind, payload = _hash_tracked_entry(repository_root, relative_path)
        records.append(
            {
                "path": relative_path,
                "kind": kind,
                "sha256": hashlib.sha256(payload).hexdigest(),
            }
        )
    canonical = json.dumps(records, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


def snapshot_repository(path: str | Path) -> RepositorySnapshot:
    repository_root = _repository_root(path)
    head = _run_git(repository_root, "rev-parse", "HEAD").decode("ascii").strip()
    branch = _run_git(repository_root, "rev-parse", "--abbrev-ref", "HEAD").decode("utf-8").strip()
    tracked_paths = _tracked_paths(repository_root)
    if not tracked_paths:
        raise RepositoryCaptureError("repository has no tracked files")
    return RepositorySnapshot(
        repository_root=repository_root,
        head_commit=head,
        branch_name=branch,
        artifact_refs=_artifact_refs(repository_root, tracked_paths),
        dependency_lock_hash=_dependency_lock_hash(repository_root, tracked_paths),
    )


def capture_repository(
    path: str | Path,
    *,
    project_id: str,
    next_action: str,
    parent_state_root: str = "0" * 64,
    active_task_id: str | None = None,
    accepted_decision_ids: Sequence[str] = (),
    unresolved_work: Sequence[str] = (),
    invariant_refs: Sequence[str] = (),
    context_refs: Sequence[str] = (),
    protocol_version: str = "v0.1",
) -> tuple[bytes, ProjectStateManifestV0_1, RepositorySnapshot]:
    snapshot = snapshot_repository(path)
    document = {
        "project_id": project_id,
        "parent_state_root": parent_state_root,
        "active_task_id": active_task_id,
        "accepted_decision_ids": list(accepted_decision_ids),
        "unresolved_work": list(unresolved_work),
        "invariant_refs": list(invariant_refs),
        "artifact_refs": list(snapshot.artifact_refs),
        "dependency_lock_hash": snapshot.dependency_lock_hash,
        "next_action": next_action,
        "context_refs": [*context_refs, f"git-head:{snapshot.head_commit}"],
        "runtime_metadata": snapshot.runtime_metadata(),
        "protocol_version": protocol_version,
    }
    artifact, manifest = capture_from_document(document)
    return artifact, manifest, snapshot
