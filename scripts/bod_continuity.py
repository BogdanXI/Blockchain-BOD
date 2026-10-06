#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.bod_continuity import capture_from_document, evidence_document, quote_artifact_operation, recover_artifact
from src.bod_economic_operations import OperationPricingPolicyV0_1
from src.bod_repository_adapter import capture_repository


def main() -> None:
    parser = argparse.ArgumentParser(prog='bod-continuity', description='Capture, recover and quote a BOD project-state artifact.')
    sub = parser.add_subparsers(dest='command', required=True)

    capture = sub.add_parser('capture')
    capture.add_argument('input', type=Path)
    capture.add_argument('artifact', type=Path)
    capture.add_argument('--evidence', type=Path)

    capture_repo = sub.add_parser('capture-repo')
    capture_repo.add_argument('repository', type=Path)
    capture_repo.add_argument('artifact', type=Path)
    capture_repo.add_argument('--project-id', required=True)
    capture_repo.add_argument('--next-action', required=True)
    capture_repo.add_argument('--parent-state-root', default='0' * 64)
    capture_repo.add_argument('--active-task-id')
    capture_repo.add_argument('--decision-id', action='append', default=[])
    capture_repo.add_argument('--unresolved-work', action='append', default=[])
    capture_repo.add_argument('--invariant-ref', action='append', default=[])
    capture_repo.add_argument('--context-ref', action='append', default=[])
    capture_repo.add_argument('--evidence', type=Path)

    recover = sub.add_parser('recover')
    recover.add_argument('artifact', type=Path)

    quote = sub.add_parser('quote')
    quote.add_argument('artifact', type=Path)
    quote.add_argument('--operation-id', required=True)
    quote.add_argument('--payer', required=True)
    quote.add_argument('--base-fee', type=int, required=True)
    quote.add_argument('--bytes-fee-per-kib', type=int, required=True)
    quote.add_argument('--artifact-fee', type=int, required=True)
    quote.add_argument('--verification-fee', type=int, required=True)
    quote.add_argument('--state-read-fee-per-kib', type=int, default=0)
    quote.add_argument('--recovery-step-fee', type=int, default=0)
    quote.add_argument('--settlement-unit-fee', type=int, default=0)
    quote.add_argument('--availability-kib-fee', type=int, default=0)
    quote.add_argument('--network-in-fee-per-kib', type=int, default=0)
    quote.add_argument('--network-out-fee-per-kib', type=int, default=0)
    quote.add_argument('--availability-hours', type=int, default=1)
    quote.add_argument('--settlement-units', type=int, default=1)

    args = parser.parse_args()
    if args.command == 'capture':
        document = json.loads(args.input.read_text(encoding='utf-8'))
        artifact, manifest = capture_from_document(document)
        args.artifact.write_bytes(artifact)
        evidence = evidence_document(manifest, artifact)
        if args.evidence:
            args.evidence.write_text(json.dumps(evidence, sort_keys=True, indent=2) + '\n', encoding='utf-8')
        print(json.dumps(evidence, sort_keys=True))
        return
    if args.command == 'capture-repo':
        artifact, manifest, snapshot = capture_repository(
            args.repository,
            project_id=args.project_id,
            next_action=args.next_action,
            parent_state_root=args.parent_state_root,
            active_task_id=args.active_task_id,
            accepted_decision_ids=args.decision_id,
            unresolved_work=args.unresolved_work,
            invariant_refs=args.invariant_ref,
            context_refs=args.context_ref,
        )
        args.artifact.write_bytes(artifact)
        evidence = evidence_document(manifest, artifact)
        evidence['git_head'] = snapshot.head_commit
        evidence['tracked_artifacts'] = len(snapshot.artifact_refs)
        evidence['dependency_lock_hash'] = snapshot.dependency_lock_hash
        if args.evidence:
            args.evidence.write_text(json.dumps(evidence, sort_keys=True, indent=2) + '\n', encoding='utf-8')
        print(json.dumps(evidence, sort_keys=True))
        return
    if args.command == 'recover':
        manifest = recover_artifact(args.artifact)
        print(json.dumps({'state_root': manifest.state_root(), 'project_id': manifest.project_id, 'protocol_version': manifest.protocol_version}, sort_keys=True))
        return
    policy = OperationPricingPolicyV0_1(
        args.base_fee, args.bytes_fee_per_kib, args.artifact_fee, args.verification_fee,
        state_read_fee_bod_per_kib=args.state_read_fee_per_kib,
        recovery_step_fee_bod=args.recovery_step_fee,
        settlement_unit_fee_bod=args.settlement_unit_fee,
        availability_kib_fee_bod=args.availability_kib_fee,
        network_in_fee_bod_per_kib=args.network_in_fee_per_kib,
        network_out_fee_bod_per_kib=args.network_out_fee_per_kib,
    )
    manifest = recover_artifact(args.artifact)
    quote = quote_artifact_operation(manifest, operation_id=args.operation_id, payer=args.payer, policy=policy, availability_hours=args.availability_hours, settlement_units=args.settlement_units)
    print(json.dumps({'operation_id': quote.operation_id, 'payer': quote.payer, 'state_root': manifest.state_root(), 'total_fee_bod': quote.total_fee_bod, 'quote': quote.__dict__}, sort_keys=True))


if __name__ == '__main__':
    main()