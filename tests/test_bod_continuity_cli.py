import json
import subprocess
import sys
from pathlib import Path

from src.bod_continuity import capture_from_document, quote_artifact_operation, recover_artifact
from src.bod_economic_operations import OperationPricingPolicyV0_1


def sample_document(runtime='alpha'):
    return {
        'project_id': 'demo-project', 'parent_state_root': '0' * 64, 'active_task_id': 'task-1',
        'accepted_decision_ids': ['ADR-1'], 'unresolved_work': ['continue'],
        'invariant_refs': ['root-stable'], 'artifact_refs': ['artifact-1'],
        'dependency_lock_hash': '1' * 64, 'next_action': 'resume', 'context_refs': ['boot-1'],
        'runtime_metadata': {'runtime': runtime},
    }


def test_capture_recover_preserves_state_root_across_runtime_change(tmp_path: Path) -> None:
    a, ma = capture_from_document(sample_document('alpha'))
    b, mb = capture_from_document(sample_document('beta'))
    assert ma.state_root() == mb.state_root()
    assert a != b
    p = tmp_path / 'artifact.json'
    p.write_bytes(a)
    recovered = recover_artifact(p)
    assert recovered.state_root() == ma.state_root()


def test_quote_binds_full_continuity_workload(tmp_path: Path) -> None:
    artifact, manifest = capture_from_document(sample_document())
    p = tmp_path / 'artifact.json'; p.write_bytes(artifact)
    quote = quote_artifact_operation(
        manifest, operation_id='op-1', payer='alice',
        policy=OperationPricingPolicyV0_1(10, 2, 5, 7, state_read_fee_bod_per_kib=3, recovery_step_fee_bod=11, settlement_unit_fee_bod=13, availability_kib_fee_bod=17, network_in_fee_bod_per_kib=19, network_out_fee_bod_per_kib=23),
    )
    assert quote.total_fee_bod > quote.base_fee_bod
    assert quote.network_in_bytes == len(artifact)
    assert quote.network_out_bytes == len(manifest.canonical_durable_bytes())


def test_cli_capture_recover_and_quote(tmp_path: Path) -> None:
    source = tmp_path / 'state.json'; artifact = tmp_path / 'state.artifact.json'; evidence = tmp_path / 'evidence.json'
    source.write_text(json.dumps(sample_document()), encoding='utf-8')
    base = [sys.executable, 'scripts/bod_continuity.py']
    capture = subprocess.run(base + ['capture', str(source), str(artifact), '--evidence', str(evidence)], check=True, capture_output=True, text=True)
    captured = json.loads(capture.stdout)
    recovered = subprocess.run(base + ['recover', str(artifact)], check=True, capture_output=True, text=True)
    assert json.loads(recovered.stdout)['state_root'] == captured['state_root']
    quoted = subprocess.run(base + ['quote', str(artifact), '--operation-id', 'op-1', '--payer', 'alice', '--base-fee', '10', '--bytes-fee-per-kib', '2', '--artifact-fee', '5', '--verification-fee', '7'], check=True, capture_output=True, text=True)
    assert json.loads(quoted.stdout)['total_fee_bod'] > 0
    assert json.loads(evidence.read_text())['artifact_sha256'] == captured['artifact_sha256']