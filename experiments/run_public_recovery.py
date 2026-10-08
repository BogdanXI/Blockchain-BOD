#!/usr/bin/env python3
"""Run a disposable-runtime continuity experiment for BOD portable checkpoints."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bod_evidence_envelope import EvidenceReferenceV0_1, create_evidence_envelope
from bod_portable import create_portable_checkpoint, sha256_bytes, canonical_json


def synthetic_snapshot(index: int) -> dict:
    entry = {
        "path": "state.txt",
        "sha256": hashlib.sha256(f"state-{index}".encode()).hexdigest(),
        "size": len(f"state-{index}"),
    }
    durable = {"schema": "bod-repository-snapshot-v0.1", "files": [entry]}
    return {**durable, "state_root": sha256_bytes(b"BOD-REPOSITORY-SNAPSHOT-V0.1\0" + canonical_json(durable))}


def main() -> int:
    previous = None
    chain = []
    for index in range(3):
        snapshot = synthetic_snapshot(index)
        envelope = create_evidence_envelope(
            project_id="bod-public-recovery",
            protocol_version="v0.1",
            state_root=snapshot["state_root"],
            predecessor_state_root=previous,
            transition_id=f"transition-{index}",
            evidence=(EvidenceReferenceV0_1(
                "slsa.provenance",
                hashlib.sha256(f"evidence-{index}".encode()).hexdigest(),
                "application/json",
                uri=f"urn:bod:evidence:{index}",
                issuer="example-builder",
            ),),
            capture_boundary="source-build-test",
        )
        chain.append(create_portable_checkpoint(snapshot=snapshot, envelope=envelope))
        previous = snapshot["state_root"]

    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        clean = root / "chain.json"
        clean.write_text(json.dumps({"checkpoints": chain}), encoding="utf-8")
        good = subprocess.run(
            [sys.executable, str(ROOT / "scripts/independent_verify.py"), str(clean), "--chain"],
            capture_output=True, text=True, check=False,
        )
        if good.returncode != 0:
            print(good.stdout)
            print(good.stderr, file=sys.stderr)
            return 1

        mutated = json.loads(clean.read_text(encoding="utf-8"))
        mutated["checkpoints"][1]["envelope"]["transition_id"] = "tampered"
        bad = root / "mutated.json"
        bad.write_text(json.dumps(mutated), encoding="utf-8")
        rejected = subprocess.run(
            [sys.executable, str(ROOT / "scripts/independent_verify.py"), str(bad), "--chain"],
            capture_output=True, text=True, check=False,
        )
        if rejected.returncode == 0:
            return 2

    print(json.dumps({
        "status": "PASS",
        "fresh_process_verification": "PASS",
        "tamper_rejection": "PASS",
        "portable_checkpoint": "PASS",
        "semantic_truth": "NOT_ASSERTED",
        "external_anchor": "NOT_REQUIRED",
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
