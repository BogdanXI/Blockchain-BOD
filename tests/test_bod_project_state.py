import pytest

from src.bod_project_state import (
    ProjectStateError,
    ProjectStateManifestV0_1,
    build_manifest,
)


def _manifest(runtime="runtime-A"):
    return build_manifest(
        project_id="project-A",
        parent_state_root="00" * 32,
        active_task_id="task-1",
        accepted_decision_ids=("adr-1", "adr-2"),
        unresolved_work=("implement-recovery",),
        invariant_refs=("inv-state-root",),
        artifact_refs=("aa" * 32, "bb" * 32),
        dependency_lock_hash="cc" * 32,
        next_action="run recovery test",
        context_refs=("context:architecture", "context:economics"),
        runtime_metadata={"execution": runtime, "runtime": "python"},
    )


def test_durable_state_root_survives_execution_environment_replacement():
    first = _manifest("environment-A")
    second = _manifest("environment-B")

    assert first.state_root() == second.state_root()
    assert first.artifact_hash() != second.artifact_hash()


def test_artifact_round_trip_is_deterministic():
    original = _manifest()
    recovered = ProjectStateManifestV0_1.from_artifact(original.to_artifact())

    assert recovered == original
    assert recovered.state_root() == original.state_root()
    assert recovered.artifact_hash() == original.artifact_hash()


def test_durable_context_change_changes_state_root():
    first = _manifest()
    changed = build_manifest(
        project_id=first.project_id,
        parent_state_root=first.parent_state_root,
        active_task_id=first.active_task_id,
        accepted_decision_ids=first.accepted_decision_ids,
        unresolved_work=("different-work",),
        invariant_refs=first.invariant_refs,
        artifact_refs=first.artifact_refs,
        dependency_lock_hash=first.dependency_lock_hash,
        next_action=first.next_action,
        context_refs=first.context_refs,
        runtime_metadata=first.runtime_metadata,
    )

    assert changed.state_root() != first.state_root()


def test_runtime_metadata_is_provenance_not_durable_state():
    first = _manifest("environment-A")
    changed_runtime = build_manifest(
        project_id=first.project_id,
        parent_state_root=first.parent_state_root,
        active_task_id=first.active_task_id,
        accepted_decision_ids=first.accepted_decision_ids,
        unresolved_work=first.unresolved_work,
        invariant_refs=first.invariant_refs,
        artifact_refs=first.artifact_refs,
        dependency_lock_hash=first.dependency_lock_hash,
        next_action=first.next_action,
        context_refs=first.context_refs,
        runtime_metadata={"execution": "environment-C", "runtime": "node"},
    )

    assert changed_runtime.state_root() == first.state_root()


@pytest.mark.parametrize(
    "mutator",
    [
        lambda d: d["durable"].update({"next_action": ""}),
        lambda d: d["durable"].update({"accepted_decision_ids": ["adr-1", "adr-1"]}),
        lambda d: d["durable"].update({"schema_version": 2}),
        lambda d: d["runtime"].update({"schema_version": 2}),
    ],
)
def test_manifest_rejects_invalid_schema(mutator):
    import json

    document = {
        "durable": _manifest().durable_document(),
        "runtime": _manifest().runtime_document(),
    }
    mutator(document)
    data = json.dumps(
        document, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode()

    with pytest.raises(ProjectStateError):
        ProjectStateManifestV0_1.from_artifact(data)


def test_manifest_artifact_is_content_addressed():
    manifest = _manifest()
    assert manifest.artifact_hash() != manifest.state_root()
    assert len(manifest.artifact_hash()) == 64
    assert len(manifest.state_root()) == 64
