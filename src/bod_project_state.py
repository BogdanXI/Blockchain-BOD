"""Deterministic durable project-state manifest for BOD recovery.

The manifest captures the minimum machine-readable project context needed by a
fresh execution environment to resume a project without relying on an earlier session.
Runtime/session metadata is recorded as provenance but is not part of the
durable project-state root.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from typing import Any, Mapping, Sequence


class ProjectStateError(ValueError):
    """Invalid durable project-state input."""


def _canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def _sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


@dataclass(frozen=True)
class ProjectStateManifestV0_1:
    project_id: str
    protocol_version: str
    parent_state_root: str
    active_task_id: str | None
    accepted_decision_ids: tuple[str, ...]
    unresolved_work: tuple[str, ...]
    invariant_refs: tuple[str, ...]
    artifact_refs: tuple[str, ...]
    dependency_lock_hash: str
    next_action: str
    context_refs: tuple[str, ...]
    runtime_metadata: Mapping[str, str]

    def durable_document(self) -> dict[str, Any]:
        """Return only state that must survive execution-environment replacement."""
        return {
            "schema_version": 1,
            "protocol_version": self.protocol_version,
            "project_id": self.project_id,
            "parent_state_root": self.parent_state_root,
            "active_task_id": self.active_task_id,
            "accepted_decision_ids": list(self.accepted_decision_ids),
            "unresolved_work": list(self.unresolved_work),
            "invariant_refs": list(self.invariant_refs),
            "artifact_refs": list(self.artifact_refs),
            "dependency_lock_hash": self.dependency_lock_hash,
            "next_action": self.next_action,
            "context_refs": list(self.context_refs),
        }

    def runtime_document(self) -> dict[str, Any]:
        return {
            "schema_version": 1,
            "runtime_metadata": dict(self.runtime_metadata),
        }

    def canonical_durable_bytes(self) -> bytes:
        return _canonical_bytes(self.durable_document())

    def state_root(self) -> str:
        return _sha256(self.canonical_durable_bytes())

    def canonical_artifact_bytes(self) -> bytes:
        """Serialize the complete manifest for content-addressed recovery."""
        return _canonical_bytes(
            {
                "durable": self.durable_document(),
                "runtime": self.runtime_document(),
            }
        )

    def artifact_hash(self) -> str:
        return _sha256(self.canonical_artifact_bytes())

    def to_artifact(self) -> bytes:
        return self.canonical_artifact_bytes()

    @classmethod
    def from_artifact(cls, data: bytes) -> "ProjectStateManifestV0_1":
        try:
            document = json.loads(data.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ProjectStateError("manifest is not valid UTF-8 JSON") from exc
        if not isinstance(document, dict) or set(document) != {"durable", "runtime"}:
            raise ProjectStateError("manifest top-level schema is invalid")
        if not isinstance(document["durable"], dict) or not isinstance(
            document["runtime"], dict
        ):
            raise ProjectStateError("manifest sections are invalid")
        if _canonical_bytes(document) != data:
            raise ProjectStateError("manifest is not canonically encoded")

        durable = document["durable"]
        runtime = document["runtime"]
        required = {
            "schema_version",
            "protocol_version",
            "project_id",
            "parent_state_root",
            "active_task_id",
            "accepted_decision_ids",
            "unresolved_work",
            "invariant_refs",
            "artifact_refs",
            "dependency_lock_hash",
            "next_action",
            "context_refs",
        }
        if set(durable) != required or durable["schema_version"] != 1:
            raise ProjectStateError("unsupported durable manifest schema")
        if set(runtime) != {"schema_version", "runtime_metadata"} or runtime["schema_version"] != 1:
            raise ProjectStateError("unsupported runtime manifest schema")
        if not isinstance(runtime["runtime_metadata"], dict) or not all(
            isinstance(k, str) and isinstance(v, str)
            for k, v in runtime["runtime_metadata"].items()
        ):
            raise ProjectStateError("runtime metadata must be string key/value pairs")

        sequence_fields = (
            "accepted_decision_ids",
            "unresolved_work",
            "invariant_refs",
            "artifact_refs",
            "context_refs",
        )
        for field in sequence_fields:
            value = durable[field]
            if not isinstance(value, list) or not all(isinstance(item, str) and item for item in value):
                raise ProjectStateError(f"{field} must be a list of non-empty strings")
            if len(value) != len(set(value)):
                raise ProjectStateError(f"{field} contains duplicates")

        scalar_fields = (
            "protocol_version",
            "project_id",
            "parent_state_root",
            "dependency_lock_hash",
            "next_action",
        )
        if any(not isinstance(durable[field], str) or not durable[field] for field in scalar_fields):
            raise ProjectStateError("required durable field is invalid")
        if durable["active_task_id"] is not None and (
            not isinstance(durable["active_task_id"], str) or not durable["active_task_id"]
        ):
            raise ProjectStateError("active_task_id is invalid")

        return cls(
            project_id=durable["project_id"],
            protocol_version=durable["protocol_version"],
            parent_state_root=durable["parent_state_root"],
            active_task_id=durable["active_task_id"],
            accepted_decision_ids=tuple(durable["accepted_decision_ids"]),
            unresolved_work=tuple(durable["unresolved_work"]),
            invariant_refs=tuple(durable["invariant_refs"]),
            artifact_refs=tuple(durable["artifact_refs"]),
            dependency_lock_hash=durable["dependency_lock_hash"],
            next_action=durable["next_action"],
            context_refs=tuple(durable["context_refs"]),
            runtime_metadata=dict(runtime["runtime_metadata"]),
        )


def build_manifest(
    *,
    project_id: str,
    parent_state_root: str,
    active_task_id: str | None,
    accepted_decision_ids: Sequence[str],
    unresolved_work: Sequence[str],
    invariant_refs: Sequence[str],
    artifact_refs: Sequence[str],
    dependency_lock_hash: str,
    next_action: str,
    context_refs: Sequence[str],
    runtime_metadata: Mapping[str, str] | None = None,
    protocol_version: str = "v0.1",
) -> ProjectStateManifestV0_1:
    manifest = ProjectStateManifestV0_1(
        project_id=project_id,
        protocol_version=protocol_version,
        parent_state_root=parent_state_root,
        active_task_id=active_task_id,
        accepted_decision_ids=tuple(accepted_decision_ids),
        unresolved_work=tuple(unresolved_work),
        invariant_refs=tuple(invariant_refs),
        artifact_refs=tuple(artifact_refs),
        dependency_lock_hash=dependency_lock_hash,
        next_action=next_action,
        context_refs=tuple(context_refs),
        runtime_metadata=dict(runtime_metadata or {}),
    )
    # Reuse the parser as the schema/integrity gate for locally-built objects.
    ProjectStateManifestV0_1.from_artifact(manifest.to_artifact())
    return manifest
