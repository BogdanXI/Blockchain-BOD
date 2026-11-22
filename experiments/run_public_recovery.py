#!/usr/bin/env python3
"""Run a disposable-runtime, evidence-payload recovery experiment for BOD."""

from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bod_evidence_envelope import EvidenceReferenceV0_1, create_evidence_envelope
from bod_evidence_formats import inspect_evidence_payload
from bod_portable import (
    canonical_json,
    create_evidence_bundle,
    create_portable_checkpoint,
    sha256_bytes,
)


def synthetic_snapshot(index: int) -> dict:
    entry = {
        "path": "state.txt",
        "sha256": hashlib.sha256(f"state-{index}".encode()).hexdigest(),
        "size": len(f"state-{index}"),
    }
    durable = {"schema": "bod-repository-snapshot-v0.1", "files": [entry]}
    return {
        **durable,
        "state_root": sha256_bytes(
            b"BOD-REPOSITORY-SNAPSHOT-V0.1\0" + canonical_json(durable)
        ),
    }


def evidence_payloads(index: int) -> dict[str, tuple[bytes, str, str]]:
    """Return digest -> (payload, evidence type, media type) fixtures."""
    documents = {
        "slsa-provenance": {
            "_type": "https://in-toto.io/Statement/v1",
            "subject": [{"name": f"release-{index}.tar.gz", "digest": {"sha256": f"{index + 1:064x}"}}],
            "predicateType": "https://slsa.dev/provenance/v1",
            "predicate": {
                "buildDefinition": {
                    "buildType": "https://example.invalid/buildtype/v1",
                    "externalParameters": {"release": index},
                },
                "runDetails": {"builder": {"id": "https://example.invalid/builder"}},
            },
        },
        "cyclonedx-sbom": {
            "bomFormat": "CycloneDX",
            "specVersion": "1.6",
            "version": index + 1,
            "components": [],
        },
        "test-report": {
            "schema": "bod-demo-test-report-v1",
            "release": index,
            "tests": {"passed": 42, "failed": 0},
        },
    }
    media_types = {
        "slsa-provenance": "application/vnd.in-toto+json",
        "cyclonedx-sbom": "application/vnd.cyclonedx+json",
        "test-report": "application/json",
    }
    result = {}
    for evidence_type, document in documents.items():
        payload = json.dumps(document, sort_keys=True, separators=(",", ":")).encode()
        result[hashlib.sha256(payload).hexdigest()] = (
            payload,
            evidence_type,
            media_types[evidence_type],
        )
    return result


def run_verifier(path: Path, *flags: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(ROOT / "scripts/independent_verify.py"), str(path), *flags],
        capture_output=True,
        text=True,
        check=False,
    )


def main() -> int:
    previous = None
    chain = []
    payloads_by_state = []
    for index in range(3):
        snapshot = synthetic_snapshot(index)
        payloads = evidence_payloads(index)
        references = [
            EvidenceReferenceV0_1(
                evidence_type=evidence_type,
                digest=digest,
                media_type=media_type,
                uri=f"urn:bod:fixture:{index}:{evidence_type}",
                issuer="synthetic-experiment-fixture",
            )
            for digest, (_, evidence_type, media_type) in payloads.items()
        ]
        envelope = create_evidence_envelope(
            project_id="bod-public-recovery",
            protocol_version="v0.1",
            state_root=snapshot["state_root"],
            predecessor_state_root=previous,
            transition_id=f"transition-{index}",
            evidence=references,
            capture_boundary="synthetic-recovery-fixture",
        )
        chain.append(create_portable_checkpoint(snapshot=snapshot, envelope=envelope))
        payloads_by_state.append(payloads)
        previous = snapshot["state_root"]

    latest_payloads = {
        digest: details[0]
        for digest, details in payloads_by_state[-1].items()
    }
    inspected_formats = set()
    for _, (payload, evidence_type, _) in payloads_by_state[-1].items():
        if evidence_type in {"slsa-provenance", "cyclonedx-sbom"}:
            inspected_formats.add(inspect_evidence_payload(payload)["format"])
    bundle = create_evidence_bundle(checkpoint=chain[-1], payloads=latest_payloads)

    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        chain_path = root / "chain.json"
        chain_path.write_text(
            json.dumps({"checkpoints": chain}), encoding="utf-8"
        )
        bundle_path = root / "release-evidence.bundle.json"
        bundle_path.write_text(json.dumps(bundle), encoding="utf-8")

        original_store = root / "original-evidence-store"
        original_store.mkdir()
        for index, payloads in enumerate(payloads_by_state):
            release_dir = original_store / str(index)
            release_dir.mkdir()
            for digest, (payload, _, _) in payloads.items():
                (release_dir / digest).write_bytes(payload)

        shutil.rmtree(original_store)

        chain_result = run_verifier(chain_path, "--chain")
        bundle_result = run_verifier(bundle_path)
        if chain_result.returncode != 0 or bundle_result.returncode != 0:
            print(chain_result.stdout, chain_result.stderr, file=sys.stderr)
            print(bundle_result.stdout, bundle_result.stderr, file=sys.stderr)
            return 1

        tampered = json.loads(bundle_path.read_text(encoding="utf-8"))
        tampered["objects"][0]["data_base64"] = "eA=="
        from bod_portable import BUNDLE_DOMAIN

        durable = {
            "schema": tampered["schema"],
            "checkpoint": tampered["checkpoint"],
            "objects": tampered["objects"],
        }
        tampered["bundle_id"] = sha256_bytes(
            BUNDLE_DOMAIN + canonical_json(durable)
        )
        tampered_path = root / "tampered.bundle.json"
        tampered_path.write_text(json.dumps(tampered), encoding="utf-8")
        rejected = run_verifier(tampered_path)
        if rejected.returncode == 0:
            return 2

    print(json.dumps({
        "status": "PASS",
        "synthetic_checkpoints": len(chain),
        "latest_evidence_payloads": len(latest_payloads),
        "format_structures_inspected": sorted(inspected_formats),
        "lineage_verification": "PASS",
        "fresh_process_bundle_verification": "PASS",
        "original_evidence_store_removed_before_verification": True,
        "payload_tampering_rejected": True,
        "semantic_truth": "NOT_ASSERTED",
        "real_external_systems": "NOT_TESTED",
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
