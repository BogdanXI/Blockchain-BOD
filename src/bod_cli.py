from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any

from src.bod_evidence_envelope import (
    EvidenceEnvelopeError,
    EvidenceEnvelopeV0_1,
    EvidenceReferenceV0_1,
    create_evidence_envelope,
    verify_chain,
)

def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def canonical_json(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")

def repository_snapshot(root: Path) -> dict[str, Any]:
    root = root.resolve()
    try:
        paths = subprocess.check_output(["git", "-C", str(root), "ls-files", "-z"], text=False).split(b"\0")
        files = [Path(p.decode("utf-8")) for p in paths if p]
    except (subprocess.CalledProcessError, FileNotFoundError):
        files = sorted(p.relative_to(root) for p in root.rglob("*") if p.is_file() and ".git" not in p.parts)
    entries = []
    for rel in sorted(files, key=lambda p: p.as_posix()):
        data = (root / rel).read_bytes()
        entries.append({"path": rel.as_posix(), "sha256": sha256_bytes(data), "size": len(data)})
    durable = {"schema": "bod-repository-snapshot-v0.1", "files": entries}
    root_hash = sha256_bytes(b"BOD-REPOSITORY-SNAPSHOT-V0.1\0" + canonical_json(durable))
    return {**durable, "state_root": root_hash}

def load_json(path: str) -> Any:
    return json.loads(Path(path).read_text(encoding="utf-8"))

def write_json(path: str, value: Any) -> None:
    Path(path).write_text(json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")

def cmd_snapshot(args: argparse.Namespace) -> int:
    result = repository_snapshot(Path(args.path))
    if args.out:
        write_json(args.out, result)
    print(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2))
    return 0

def cmd_create(args: argparse.Namespace) -> int:
    evidence = []
    if args.evidence:
        for item in load_json(args.evidence):
            evidence.append(EvidenceReferenceV0_1.from_document(item))
    envelope = create_evidence_envelope(
        project_id=args.project,
        protocol_version="0.1",
        state_root=args.state_root,
        predecessor_state_root=args.predecessor,
        transition_id=args.transition,
        evidence=evidence,
        capture_boundary=args.capture_boundary,
    )
    document = envelope.to_document()
    if args.out:
        write_json(args.out, document)
    print(json.dumps(document, ensure_ascii=False, sort_keys=True, indent=2))
    return 0

def _envelopes(value: Any) -> list[EvidenceEnvelopeV0_1]:
    if isinstance(value, dict) and "envelopes" in value:
        value = value["envelopes"]
    if isinstance(value, dict):
        value = [value]
    if not isinstance(value, list):
        raise EvidenceEnvelopeError("expected an envelope object or an envelopes array")
    return [EvidenceEnvelopeV0_1.from_document(item) for item in value]

def cmd_verify(args: argparse.Namespace) -> int:
    try:
        envelopes = _envelopes(load_json(args.file))
        if args.chain:
            verify_chain(envelopes)
        elif len(envelopes) != 1:
            raise EvidenceEnvelopeError("verify without --chain requires exactly one envelope")
        print(json.dumps({"status": "VALID", "envelopes": len(envelopes), "commitments": [e.commitment() for e in envelopes]}, indent=2))
        return 0
    except (EvidenceEnvelopeError, OSError, json.JSONDecodeError) as exc:
        print(json.dumps({"status": "INVALID", "reason": str(exc)}, indent=2))
        return 1

def cmd_demo(args: argparse.Namespace) -> int:
    previous = None
    chain = []
    for index in range(3):
        state = sha256_bytes(f"BOD-demo-state-{index}".encode())
        env = create_evidence_envelope(
            project_id="bod-demo",
            protocol_version="0.1",
            state_root=state,
            predecessor_state_root=previous,
            transition_id=f"demo-transition-{index}",
            evidence=[EvidenceReferenceV0_1("demo", sha256_bytes(f"evidence-{index}".encode()), "text/plain")],
            capture_boundary="demo",
        )
        chain.append(env)
        previous = state
    verify_chain(chain)
    result = {"status": "VALID", "product": "BOD Evidence Fabric", "states": len(chain), "head": chain[-1].state_root, "envelope_ids": [e.envelope_id for e in chain]}
    print(json.dumps(result, indent=2))
    return 0

def main() -> int:
    parser = argparse.ArgumentParser(prog="bod", description="BOD Evidence Fabric — create, verify and recover durable evidence.")
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("snapshot", help="create a deterministic repository state root")
    p.add_argument("path", nargs="?", default=".")
    p.add_argument("--out")
    p.set_defaults(func=cmd_snapshot)
    p = sub.add_parser("evidence-create", help="create a versioned evidence envelope")
    p.add_argument("--project", required=True)
    p.add_argument("--state-root", required=True)
    p.add_argument("--transition", required=True)
    p.add_argument("--predecessor")
    p.add_argument("--capture-boundary", default="repository-state")
    p.add_argument("--evidence", help="JSON array of digest-only evidence references")
    p.add_argument("--out")
    p.set_defaults(func=cmd_create)
    p = sub.add_parser("verify", help="verify one envelope or an entire chain")
    p.add_argument("file")
    p.add_argument("--chain", action="store_true")
    p.set_defaults(func=cmd_verify)
    p = sub.add_parser("demo", help="run a complete local evidence-chain demonstration")
    p.set_defaults(func=cmd_demo)
    args = parser.parse_args()
    return args.func(args)

if __name__ == "__main__":
    raise SystemExit(main())
