from __future__ import annotations

import argparse
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
        verify_lineage_graph,
    )
    from bod_evidence_formats import (
        EvidenceFormatError,
        EvidenceVerificationError,
        inspect_evidence_payload,
        run_sigstore_verification,
    )
    from bod_portable import (
        create_evidence_bundle,
        create_portable_checkpoint,
        extract_evidence_bundle,
        parse_portable,
        repository_snapshot,
        verify_evidence_bundle,
        verify_portable_chain,
        verify_portable_graph,
    )
except ImportError:
    from src.bod_evidence_envelope import (
        EvidenceEnvelopeError,
        EvidenceEnvelopeV0_1,
        EvidenceReferenceV0_1,
        create_evidence_envelope,
        verify_chain,
        verify_lineage_graph,
    )
    from src.bod_evidence_formats import (
        EvidenceFormatError,
        EvidenceVerificationError,
        inspect_evidence_payload,
        run_sigstore_verification,
    )
    from src.bod_portable import (
        create_evidence_bundle,
        create_portable_checkpoint,
        extract_evidence_bundle,
        parse_portable,
        repository_snapshot,
        verify_evidence_bundle,
        verify_portable_chain,
        verify_portable_graph,
    )


def load(path: str | Path) -> Any:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def save(path: str | Path, value: Any) -> None:
    Path(path).write_text(json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")


def parse_envelopes(value: Any) -> list[EvidenceEnvelopeV0_1]:
    if isinstance(value, dict) and "envelopes" in value:
        value = value["envelopes"]
    if isinstance(value, dict):
        value = [value]
    if not isinstance(value, list):
        raise EvidenceEnvelopeError("expected envelope object or envelopes array")
    return [EvidenceEnvelopeV0_1.from_document(x) for x in value]


def parse_checkpoints(value: Any) -> list[dict[str, Any]]:
    if isinstance(value, dict) and "checkpoints" in value:
        value = value["checkpoints"]
    if isinstance(value, dict):
        value = [value]
    if not isinstance(value, list):
        raise EvidenceEnvelopeError("expected checkpoint object or checkpoints array")
    return value


def cmd_snapshot(args) -> int:
    value = repository_snapshot(Path(args.path))
    if args.out:
        save(args.out, value)
    print(json.dumps(value, indent=2))
    return 0


def cmd_capture(args) -> int:
    root = Path(args.path).resolve()
    snapshot = repository_snapshot(root)
    predecessor = None
    if args.predecessor:
        previous = parse_checkpoints(load(args.predecessor))
        if not previous:
            raise EvidenceEnvelopeError("predecessor file is empty")
        _, previous_envelope = parse_portable(previous[-1])
        predecessor = previous_envelope.state_root

    refs = []
    if args.evidence:
        refs = [EvidenceReferenceV0_1.from_document(x) for x in load(args.evidence)]
    transition = args.transition
    if not transition:
        transition = subprocess.check_output(["git", "-C", str(root), "rev-parse", "HEAD"], text=True).strip()
    envelope = create_evidence_envelope(
        project_id=args.project,
        protocol_version="0.1",
        state_root=snapshot["state_root"],
        predecessor_state_root=predecessor,
        transition_id=transition,
        evidence=refs,
        capture_boundary=args.capture_boundary,
    )
    checkpoint = create_portable_checkpoint(snapshot=snapshot, envelope=envelope)
    if args.out:
        save(args.out, checkpoint)
    print(json.dumps(checkpoint, indent=2))
    return 0


def cmd_evidence_create(args) -> int:
    refs = [EvidenceReferenceV0_1.from_document(x) for x in load(args.evidence)] if args.evidence else []
    envelope = create_evidence_envelope(
        project_id=args.project, protocol_version="0.1", state_root=args.state_root,
        predecessor_state_root=args.predecessor, transition_id=args.transition,
        evidence=refs, capture_boundary=args.capture_boundary,
    )
    value = envelope.to_document()
    if args.out:
        save(args.out, value)
    print(json.dumps(value, indent=2))
    return 0


def cmd_verify(args) -> int:
    try:
        value = load(args.file)
        if args.portable:
            checkpoints = parse_checkpoints(value)
            if args.graph:
                graph = verify_portable_graph(checkpoints)
                print(json.dumps({"status": "VALID_INTEGRITY", "portable_checkpoints": len(checkpoints), "lineage_graph": graph, "canonical_head": None}, indent=2))
            else:
                verify_portable_chain(checkpoints)
                commitments = [parse_portable(x)[1].commitment() for x in checkpoints]
                print(json.dumps({"status": "VALID_INTEGRITY", "portable_checkpoints": len(checkpoints), "envelope_commitments": commitments, "recovery": "VERIFIABLE"}, indent=2))
        else:
            envs = parse_envelopes(value)
            if args.graph:
                graph = verify_lineage_graph(envs)
                print(json.dumps({"status": "VALID_INTEGRITY", "envelopes": len(envs), "lineage_graph": graph, "canonical_head": None}, indent=2))
            else:
                if not args.chain and len(envs) != 1:
                    raise EvidenceEnvelopeError("verify without --chain requires exactly one envelope")
                verify_chain(envs)
                print(json.dumps({"status": "VALID_INTEGRITY", "envelopes": len(envs), "commitments": [e.commitment() for e in envs]}, indent=2))
        return 0
    except (EvidenceEnvelopeError, EvidenceFormatError, EvidenceVerificationError, OSError, json.JSONDecodeError) as exc:
        print(json.dumps({"status": "INVALID", "reason": str(exc)}, indent=2))
        return 1


def cmd_evidence_verify(args) -> int:
    result = run_sigstore_verification(
        mode=args.mode,
        subject=args.subject,
        bundle=args.bundle,
        offline=args.offline,
        cert_identity=args.cert_identity,
        cert_oidc_issuer=getattr(args, "cert_oidc_issuer", None),
        trigger=getattr(args, "trigger", None),
        sha=getattr(args, "sha", None),
        workflow_name=getattr(args, "workflow_name", None),
        repository=getattr(args, "repository", None),
        ref=getattr(args, "ref", None),
    )
    print(json.dumps(result, indent=2))
    return 0 if result["status"] == "VALID" else 1


def cmd_evidence_inspect(args) -> int:
    result = inspect_evidence_payload(Path(args.file).read_bytes(), args.format)
    print(json.dumps(result, indent=2))
    return 0


def cmd_bundle_create(args) -> int:
    checkpoint = parse_checkpoints(load(args.checkpoint))
    if len(checkpoint) != 1:
        raise EvidenceEnvelopeError("bundle-create requires exactly one checkpoint")
    payloads = {}
    for assignment in args.payload or []:
        if "=" not in assignment:
            raise EvidenceEnvelopeError("payload must use DIGEST=PATH")
        digest, filename = assignment.split("=", 1)
        if digest in payloads:
            raise EvidenceEnvelopeError(f"duplicate payload digest: {digest}")
        payloads[digest] = Path(filename).read_bytes()
    bundle = create_evidence_bundle(checkpoint=checkpoint[0], payloads=payloads)
    if args.out:
        save(args.out, bundle)
    print(json.dumps({
        "status": "BUNDLE_CREATED",
        "bundle_id": bundle["bundle_id"],
        "evidence_objects": len(bundle["objects"]),
        "output": args.out,
    }, indent=2))
    return 0


def cmd_bundle_verify(args) -> int:
    result = verify_evidence_bundle(load(args.file))
    print(json.dumps({"status": "VALID_SELF_CONTAINED_BUNDLE", **result}, indent=2))
    return 0


def cmd_bundle_extract(args) -> int:
    result = extract_evidence_bundle(load(args.file), Path(args.out_dir))
    print(json.dumps(result, indent=2))
    return 0


def cmd_recover(args) -> int:
    try:
        checkpoints = parse_checkpoints(load(args.file))
        verify_portable_chain(checkpoints)
        snapshot, envelope = parse_portable(checkpoints[-1])
        print(json.dumps({
            "status": "RECOVERY_VERIFIED",
            "project_id": envelope.project_id,
            "state_root": snapshot["state_root"],
            "envelope_id": envelope.envelope_id,
            "checkpoint_id": checkpoints[-1]["checkpoint_id"],
            "files": len(snapshot["files"]),
            "lineage_depth": len(checkpoints),
            "semantic_truth": "NOT_ASSERTED",
            "source_payloads": "NOT_INCLUDED",
        }, indent=2))
        return 0
    except (EvidenceEnvelopeError, EvidenceFormatError, EvidenceVerificationError, OSError, json.JSONDecodeError) as exc:
        print(json.dumps({"status": "RECOVERY_FAILED", "reason": str(exc)}, indent=2))
        return 1


def cmd_demo(args) -> int:
    root = Path(args.path).resolve()
    snapshot = repository_snapshot(root)
    envelope = create_evidence_envelope(
        project_id="bod-demo", protocol_version="0.1", state_root=snapshot["state_root"],
        predecessor_state_root=None, transition_id="demo", evidence=(),
        capture_boundary="demo",
    )
    checkpoint = create_portable_checkpoint(snapshot=snapshot, envelope=envelope)
    print(json.dumps({"status": "PASS", "checkpoint_id": checkpoint["checkpoint_id"], "state_root": snapshot["state_root"]}, indent=2))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(prog="bod", description="BOD portable continuity core")
    sub = parser.add_subparsers(dest="command", required=True)

    x = sub.add_parser("snapshot")
    x.add_argument("path", nargs="?", default=".")
    x.add_argument("--out")
    x.set_defaults(func=cmd_snapshot)

    x = sub.add_parser("capture")
    x.add_argument("path", nargs="?", default=".")
    x.add_argument("--project", required=True)
    x.add_argument("--transition")
    x.add_argument("--predecessor")
    x.add_argument("--capture-boundary", default="repository-state")
    x.add_argument("--evidence")
    x.add_argument("--out")
    x.set_defaults(func=cmd_capture)

    x = sub.add_parser("evidence-create")
    x.add_argument("--project", required=True)
    x.add_argument("--state-root", required=True)
    x.add_argument("--transition", required=True)
    x.add_argument("--predecessor")
    x.add_argument("--capture-boundary", default="repository-state")
    x.add_argument("--evidence")
    x.add_argument("--out")
    x.set_defaults(func=cmd_evidence_create)

    x = sub.add_parser("verify")
    x.add_argument("file")
    x.add_argument("--portable", action="store_true")
    x.add_argument("--chain", action="store_true")
    x.add_argument("--graph", action="store_true", help="verify all branches without selecting a canonical head")
    x.set_defaults(func=cmd_verify)

    x = sub.add_parser("evidence-verify", help="verify Sigstore signatures and identity claims using the official sigstore CLI")
    modes = x.add_subparsers(dest="mode", required=True)

    y = modes.add_parser("identity", help="verify a Sigstore bundle against certificate identity and OIDC issuer")
    y.add_argument("subject", help="artifact path or sha256:<digest>")
    y.add_argument("--bundle", required=True)
    y.add_argument("--cert-identity", required=True)
    y.add_argument("--cert-oidc-issuer", required=True)
    y.add_argument("--offline", action="store_true")
    y.set_defaults(func=cmd_evidence_verify)

    y = modes.add_parser("github", help="verify GitHub Actions provenance claims in a Sigstore bundle")
    y.add_argument("subject", help="artifact path or sha256:<digest>")
    y.add_argument("--bundle", required=True)
    y.add_argument("--cert-identity", required=True)
    y.add_argument("--trigger", required=True)
    y.add_argument("--sha", required=True)
    y.add_argument("--workflow-name")
    y.add_argument("--repository", required=True)
    y.add_argument("--ref", required=True)
    y.add_argument("--offline", action="store_true")
    y.set_defaults(func=cmd_evidence_verify)

    x = sub.add_parser("evidence-inspect", help="inspect supported evidence document structure without verifying signatures")
    x.add_argument("file")
    x.add_argument("--format", choices=("auto", "in-toto", "slsa-provenance", "cyclonedx-json", "spdx-json", "dsse"), default="auto")
    x.set_defaults(func=cmd_evidence_inspect)

    x = sub.add_parser("bundle-create", help="package all referenced evidence payloads with one checkpoint")
    x.add_argument("checkpoint")
    x.add_argument("--payload", action="append", metavar="SHA256=PATH", help="repeat once for each evidence digest")
    x.add_argument("--out", required=True)
    x.set_defaults(func=cmd_bundle_create)

    x = sub.add_parser("bundle-verify", help="verify a self-contained evidence bundle")
    x.add_argument("file")
    x.set_defaults(func=cmd_bundle_verify)

    x = sub.add_parser("bundle-extract", help="verify and safely extract evidence payloads from a bundle")
    x.add_argument("file")
    x.add_argument("--out-dir", required=True, help="new directory to create; existing paths are never overwritten")
    x.set_defaults(func=cmd_bundle_extract)

    x = sub.add_parser("recover")
    x.add_argument("file")
    x.set_defaults(func=cmd_recover)

    x = sub.add_parser("demo")
    x.add_argument("path", nargs="?", default=".")
    x.set_defaults(func=cmd_demo)

    args = parser.parse_args()
    try:
        return args.func(args)
    except (EvidenceEnvelopeError, EvidenceFormatError, EvidenceVerificationError, OSError, json.JSONDecodeError) as exc:
        print(json.dumps({"status": "INVALID", "reason": str(exc)}, indent=2))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
