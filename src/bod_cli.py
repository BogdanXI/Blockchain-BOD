from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any

try:
    from bod_evidence_envelope import (
        EvidenceEnvelopeError,
        EvidenceEnvelopeV0_1,
        EvidenceReferenceV0_1,
        create_evidence_envelope,
        verify_chain,
    )
    from bod_verification import EvidencePolicy, verify_envelopes
except ImportError:
    from src.bod_evidence_envelope import (
        EvidenceEnvelopeError,
        EvidenceEnvelopeV0_1,
        EvidenceReferenceV0_1,
        create_evidence_envelope,
        verify_chain,
    )
    from src.bod_verification import EvidencePolicy, verify_envelopes


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_json(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def repository_snapshot(root: Path) -> dict[str, Any]:
    root = root.resolve()
    raw = subprocess.check_output(["git", "-C", str(root), "ls-files", "-z"])
    files = [Path(p.decode()) for p in raw.split(b"\0") if p]
    entries = [
        {
            "path": rel.as_posix(),
            "sha256": sha256_bytes((root / rel).read_bytes()),
            "size": (root / rel).stat().st_size,
        }
        for rel in sorted(files, key=lambda p: p.as_posix())
    ]
    durable = {"schema": "bod-repository-snapshot-v0.1", "files": entries}
    return {
        **durable,
        "state_root": sha256_bytes(
            b"BOD-REPOSITORY-SNAPSHOT-V0.1\0" + canonical_json(durable)
        ),
    }


def load(path: str | Path) -> Any:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def save(path: str | Path, value: Any) -> None:
    Path(path).write_text(
        json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )


def cmd_snapshot(args) -> int:
    value = repository_snapshot(Path(args.path))
    if args.out:
        save(args.out, value)
    print(json.dumps(value, indent=2))
    return 0


def cmd_create(args) -> int:
    refs = (
        [EvidenceReferenceV0_1.from_document(x) for x in load(args.evidence)]
        if args.evidence
        else []
    )
    envelope = create_evidence_envelope(
        project_id=args.project,
        protocol_version="0.1",
        state_root=args.state_root,
        predecessor_state_root=args.predecessor,
        transition_id=args.transition,
        evidence=refs,
        capture_boundary=args.capture_boundary,
    )
    value = envelope.to_document()
    if args.out:
        save(args.out, value)
    print(json.dumps(value, indent=2))
    return 0


def parse_envelopes(value: Any) -> list[EvidenceEnvelopeV0_1]:
    if isinstance(value, dict) and "envelopes" in value:
        value = value["envelopes"]
    if isinstance(value, dict):
        value = [value]
    if not isinstance(value, list):
        raise EvidenceEnvelopeError("expected envelope object or envelopes array")
    return [EvidenceEnvelopeV0_1.from_document(x) for x in value]


def cmd_verify(args) -> int:
    try:
        envs = parse_envelopes(load(args.file))
        if not args.chain and len(envs) != 1:
            raise EvidenceEnvelopeError("verify without --chain requires exactly one envelope")
        report = verify_envelopes(envs, policy=EvidencePolicy())
        print(json.dumps({
            **report.to_document(),
            "envelopes": len(envs),
            "commitments": [e.commitment() for e in envs],
        }, indent=2))
        return 0 if report.valid else 1
    except (EvidenceEnvelopeError, OSError, json.JSONDecodeError) as exc:
        print(json.dumps({
            "schema": "bod-verification-report-v0.1",
            "status": "INVALID",
            "integrity": "INVALID",
            "lineage": "NOT_CHECKED",
            "evidence_binding": "NOT_CHECKED",
            "semantic_truth": "NOT_ASSERTED",
            "availability": "UNKNOWN",
            "policy": "NOT_CHECKED",
            "reasons": [str(exc)],
        }, indent=2))
        return 1


def cmd_demo(args) -> int:
    previous = None
    chain = []
    for i in range(3):
        state = sha256_bytes(f"BOD-demo-state-{i}".encode())
        envelope = create_evidence_envelope(
            project_id="bod-demo",
            protocol_version="0.1",
            state_root=state,
            predecessor_state_root=previous,
            transition_id=f"demo-transition-{i}",
            evidence=[
                EvidenceReferenceV0_1(
                    "demo",
                    sha256_bytes(f"evidence-{i}".encode()),
                    "text/plain",
                )
            ],
            capture_boundary="demo",
        )
        chain.append(envelope)
        previous = state
    report = verify_envelopes(chain)
    print(json.dumps({
        "status": report.status,
        "meaning": "cryptographic integrity and lineage only; semantic truth is not asserted",
        "product": "BOD Evidence Fabric",
        "states": len(chain),
        "head": chain[-1].state_root,
        "envelope_ids": [e.envelope_id for e in chain],
    }, indent=2))
    return 0 if report.valid else 1


def main() -> int:
    parser = argparse.ArgumentParser(prog="bod", description="BOD Evidence Fabric")
    sub = parser.add_subparsers(dest="command", required=True)

    x = sub.add_parser("snapshot")
    x.add_argument("path", nargs="?", default=".")
    x.add_argument("--out")
    x.set_defaults(func=cmd_snapshot)

    x = sub.add_parser("evidence-create")
    x.add_argument("--project", required=True)
    x.add_argument("--state-root", required=True)
    x.add_argument("--transition", required=True)
    x.add_argument("--predecessor")
    x.add_argument("--capture-boundary", default="repository-state")
    x.add_argument("--evidence")
    x.add_argument("--out")
    x.set_defaults(func=cmd_create)

    x = sub.add_parser("verify")
    x.add_argument("file")
    x.add_argument("--chain", action="store_true")
    x.set_defaults(func=cmd_verify)

    x = sub.add_parser("demo")
    x.set_defaults(func=cmd_demo)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
