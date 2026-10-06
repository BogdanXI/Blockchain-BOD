from __future__ import annotations

from dataclasses import asdict
import json
from pathlib import Path
from typing import Any, Mapping

from src.bod_economic_operations import OperationPricingPolicyV0_1, OperationQuote, quote_project_operation
from src.bod_project_state import ProjectStateManifestV0_1, build_manifest


def capture_from_document(document: Mapping[str, Any]) -> tuple[bytes, ProjectStateManifestV0_1]:
    required = {
        'project_id', 'parent_state_root', 'active_task_id', 'accepted_decision_ids',
        'unresolved_work', 'invariant_refs', 'artifact_refs', 'dependency_lock_hash',
        'next_action', 'context_refs',
    }
    missing = sorted(required - set(document))
    if missing:
        raise ValueError(f'missing project-state fields: {", ".join(missing)}')
    manifest = build_manifest(
        project_id=document['project_id'],
        parent_state_root=document['parent_state_root'],
        active_task_id=document['active_task_id'],
        accepted_decision_ids=document['accepted_decision_ids'],
        unresolved_work=document['unresolved_work'],
        invariant_refs=document['invariant_refs'],
        artifact_refs=document['artifact_refs'],
        dependency_lock_hash=document['dependency_lock_hash'],
        next_action=document['next_action'],
        context_refs=document['context_refs'],
        runtime_metadata=document.get('runtime_metadata', {}),
        protocol_version=document.get('protocol_version', 'v0.1'),
    )
    return manifest.to_artifact(), manifest


def recover_artifact(path: str | Path) -> ProjectStateManifestV0_1:
    return ProjectStateManifestV0_1.from_artifact(Path(path).read_bytes())


def quote_artifact_operation(
    manifest: ProjectStateManifestV0_1,
    *,
    operation_id: str,
    payer: str,
    policy: OperationPricingPolicyV0_1,
    availability_hours: int = 1,
    settlement_units: int = 1,
) -> OperationQuote:
    if availability_hours < 0 or settlement_units < 0:
        raise ValueError('availability_hours and settlement_units must be non-negative')
    artifact_bytes = len(manifest.to_artifact())
    durable_bytes = len(manifest.canonical_durable_bytes())
    return quote_project_operation(
        operation_id=operation_id,
        payer=payer,
        payload_bytes=durable_bytes,
        artifact_count=1,
        verification_count=1,
        state_read_bytes=artifact_bytes,
        recovery_steps=1,
        settlement_units=settlement_units,
        availability_kib=((artifact_bytes + 1023) // 1024) * availability_hours,
        network_in_bytes=artifact_bytes,
        network_out_bytes=durable_bytes,
        policy=policy,
    )


def evidence_document(manifest: ProjectStateManifestV0_1, artifact: bytes) -> dict[str, Any]:
    import hashlib
    return {
        'schema': 'bod-continuity-evidence-v0.1',
        'project_id': manifest.project_id,
        'state_root': manifest.state_root(),
        'artifact_sha256': hashlib.sha256(artifact).hexdigest(),
        'artifact_bytes': len(artifact),
        'durable_bytes': len(manifest.canonical_durable_bytes()),
        'protocol_version': manifest.protocol_version,
    }