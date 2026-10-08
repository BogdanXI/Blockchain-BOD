#!/usr/bin/env python3
"""Run a disposable-runtime continuity experiment for BOD.

The parent process creates only the exported JSON artifact. Verification is
performed by a separate Python process using the independent verifier.
"""

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


def digest(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def main() -> int:
    previous = None
    chain = []
    for index in range(3):
        state = digest(f"public-recovery-state-{index}")
        envelope = create_evidence_envelope(
            project_id="bod-public-recovery",
            protocol_version="v0.1",
            state_root=state,
            predecessor_state_root=previous,
            transition_id=f"transition-{index}",
            evidence=(
                EvidenceReferenceV0_1(
                    "slsa.provenance",
                    digest(f"evidence-{index}"),
                    "application/json",
                    uri=f"urn:bod:evidence:{index}",
                    issuer="example-builder",
                ),
            ),
            capture_boundary="source-build-test",
        )
        chain.append(envelope.to_document())
        previous = state

    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        clean = root / "chain.json"
        clean.write_text(json.dumps({"envelopes": chain}), encoding="utf-8")
        good = subprocess.run(
            [sys.executable, str(ROOT / "scripts/independent_verify.py"), str(clean), "--chain"],
            capture_output=True,
            text=True,
            check=False,
        )
        if good.returncode != 0:
            print(good.stdout)
            print(good.stderr, file=sys.stderr)
            return 1

        mutated = json.loads(clean.read_text(encoding="utf-8"))
        mutated["envelopes"][1]["transition_id"] = "tampered"
        bad = root / "mutated.json"
        bad.write_text(json.dumps(mutated), encoding="utf-8")
        rejected = subprocess.run(
            [sys.executable, str(ROOT / "scripts/independent_verify.py"), str(bad), "--chain"],
            capture_output=True,
            text=True,
            check=False,
        )
        if rejected.returncode == 0:
            return 2

    print(json.dumps({
        "status": "PASS",
        "fresh_process_verification": "PASS",
        "tamper_rejection": "PASS",
        "semantic_truth": "NOT_ASSERTED",
        "external_anchor": "NOT_REQUIRED",
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
