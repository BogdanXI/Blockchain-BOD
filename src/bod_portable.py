from __future__ import annotations

import base64
import binascii
import hashlib
import json
import os
import re
import shutil
import stat
import subprocess
from pathlib import Path, PurePosixPath
from typing import Any

try:
    from bod_evidence_envelope import (
        EvidenceEnvelopeError,
        EvidenceEnvelopeV0_1,
        verify_lineage_graph,
    )
except ImportError:
    from src.bod_evidence_envelope import (
        EvidenceEnvelopeError,
        EvidenceEnvelopeV0_1,
        verify_lineage_graph,
    )

SNAPSHOT_SCHEMA = "bod-repository-snapshot-v0.1"
PORTABLE_SCHEMA = "bod-portable-checkpoint-v0.1"
BUNDLE_SCHEMA = "bod-evidence-bundle-v0.1"
SNAPSHOT_DOMAIN = b"BOD-REPOSITORY-SNAPSHOT-V0.1\0"
PORTABLE_DOMAIN = b"BOD-PORTABLE-CHECKPOINT-V0.1\0"
BUNDLE_DOMAIN = b"BOD-EVIDENCE-BUNDLE-V0.1\0"


def canonical_json(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def repository_snapshot(root: Path) -> dict[str, Any]:
    root = root.resolve()
    raw = subprocess.check_output(["git", "-C", str(root), "ls-files", "-z"])
    files = [Path(p.decode()) for p in raw.split(b"\0") if p]
    entries = []
    for rel in sorted(files, key=lambda p: p.as_posix()):
        path = root / rel
        try:
            metadata = path.lstat()
        except FileNotFoundError as exc:
            raise EvidenceEnvelopeError(f"tracked path is missing from the working tree: {rel.as_posix()}") from exc

        if stat.S_ISLNK(metadata.st_mode):
            payload = os.fsencode(os.readlink(path))
        elif stat.S_ISREG(metadata.st_mode):
            payload = path.read_bytes()
        else:
            raise EvidenceEnvelopeError(f"tracked path is not a regular file or symlink: {rel.as_posix()}")

        entries.append({
            "path": rel.as_posix(),
            "sha256": sha256_bytes(payload),
            "size": len(payload),
        })
    durable = {"schema": SNAPSHOT_SCHEMA, "files": entries}
    return {**durable, "state_root": sha256_bytes(SNAPSHOT_DOMAIN + canonical_json(durable))}


def verify_snapshot(snapshot: dict[str, Any]) -> None:
    if not isinstance(snapshot, dict) or set(snapshot) != {"schema", "files", "state_root"}:
        raise EvidenceEnvelopeError("invalid repository snapshot")
    if snapshot["schema"] != SNAPSHOT_SCHEMA or not isinstance(snapshot["files"], list):
        raise EvidenceEnvelopeError("unsupported repository snapshot schema")
    if not isinstance(snapshot["state_root"], str) or not re.fullmatch(r"[0-9a-f]{64}", snapshot["state_root"]):
        raise EvidenceEnvelopeError("invalid snapshot state_root")

    previous_path: str | None = None
    for item in snapshot["files"]:
        if not isinstance(item, dict) or set(item) != {"path", "sha256", "size"}:
            raise EvidenceEnvelopeError("invalid snapshot file entry")

        relative = item["path"]
        if not isinstance(relative, str) or not relative or chr(92) in relative or chr(0) in relative:
            raise EvidenceEnvelopeError("invalid snapshot path")
        portable_path = PurePosixPath(relative)
        if (
            portable_path.is_absolute()
            or not portable_path.parts
            or portable_path.as_posix() != relative
            or any(part in {".", ".."} for part in portable_path.parts)
            or portable_path.parts[0].endswith(":")
        ):
            raise EvidenceEnvelopeError("snapshot path is not a normalized relative path")
        if previous_path is not None and relative <= previous_path:
            raise EvidenceEnvelopeError("snapshot paths must be unique and sorted")
        previous_path = relative

        digest = item["sha256"]
        if not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest):
            raise EvidenceEnvelopeError("invalid snapshot file digest")
        if type(item["size"]) is not int or item["size"] < 0:
            raise EvidenceEnvelopeError("invalid snapshot file size")

    durable = {"schema": snapshot["schema"], "files": snapshot["files"]}
    expected = sha256_bytes(SNAPSHOT_DOMAIN + canonical_json(durable))
    if expected != snapshot["state_root"]:
        raise EvidenceEnvelopeError("snapshot state_root mismatch")


def create_portable_checkpoint(*, snapshot: dict[str, Any], envelope: EvidenceEnvelopeV0_1) -> dict[str, Any]:
    verify_snapshot(snapshot)
    if envelope.state_root != snapshot["state_root"]:
        raise EvidenceEnvelopeError("envelope state_root does not match snapshot")
    document = {"schema": PORTABLE_SCHEMA, "snapshot": snapshot, "envelope": envelope.to_document()}
    checkpoint_id = sha256_bytes(PORTABLE_DOMAIN + canonical_json(document))
    return {**document, "checkpoint_id": checkpoint_id}


def parse_portable(value: Any) -> tuple[dict[str, Any], EvidenceEnvelopeV0_1]:
    if not isinstance(value, dict) or set(value) != {"schema", "snapshot", "envelope", "checkpoint_id"}:
        raise EvidenceEnvelopeError("invalid portable checkpoint")
    if value["schema"] != PORTABLE_SCHEMA:
        raise EvidenceEnvelopeError("unsupported portable checkpoint schema")
    checkpoint_id = value["checkpoint_id"]
    if not isinstance(checkpoint_id, str) or len(checkpoint_id) != 64:
        raise EvidenceEnvelopeError("invalid checkpoint_id")
    document = {"schema": value["schema"], "snapshot": value["snapshot"], "envelope": value["envelope"]}
    if checkpoint_id != sha256_bytes(PORTABLE_DOMAIN + canonical_json(document)):
        raise EvidenceEnvelopeError("checkpoint_id mismatch")
    verify_snapshot(value["snapshot"])
    envelope = EvidenceEnvelopeV0_1.from_document(value["envelope"])
    if envelope.state_root != value["snapshot"]["state_root"]:
        raise EvidenceEnvelopeError("portable checkpoint state_root mismatch")
    return value["snapshot"], envelope


def verify_portable_graph(values: list[dict[str, Any]]) -> dict[str, Any]:
    """Verify portable checkpoints as a branching graph without choosing a head."""
    if not values:
        raise EvidenceEnvelopeError("portable checkpoint graph is empty")
    parsed = [parse_portable(value) for value in values]
    snapshots = [item[0] for item in parsed]
    envelopes = [item[1] for item in parsed]
    graph = verify_lineage_graph(envelopes)
    roots = [snapshot["state_root"] for snapshot in snapshots]
    if roots != [envelope.state_root for envelope in envelopes] or len(set(roots)) != len(roots):
        raise EvidenceEnvelopeError("portable checkpoint state roots are inconsistent")
    return graph


def verify_portable_chain(values: list[dict[str, Any]]) -> None:
    """Verify a single linear portable checkpoint chain."""
    graph = verify_portable_graph(values)
    if graph["fork_points"]:
        raise EvidenceEnvelopeError("portable checkpoint chain contains a fork; verify it as a graph")


def create_evidence_bundle(
    *, checkpoint: dict[str, Any], payloads: dict[str, bytes]
) -> dict[str, Any]:
    """Create a self-contained bundle for every payload referenced by a checkpoint.

    Keys are lowercase SHA-256 hex digests (without the sha256 prefix).
    Repository source files are deliberately not included by this format.
    """
    _, envelope = parse_portable(checkpoint)
    references = {item.digest: item for item in envelope.evidence}
    if len(references) != len(envelope.evidence):
        raise EvidenceEnvelopeError("one digest cannot have multiple evidence reference descriptors")
    if set(payloads) != set(references):
        missing = sorted(set(references) - set(payloads))
        extra = sorted(set(payloads) - set(references))
        raise EvidenceEnvelopeError(
            f"payload set must exactly match checkpoint evidence (missing={missing}, extra={extra})"
        )

    objects = []
    for digest in sorted(references):
        payload = payloads[digest]
        if not isinstance(payload, bytes):
            raise EvidenceEnvelopeError("evidence payloads must be bytes")
        if sha256_bytes(payload) != digest:
            raise EvidenceEnvelopeError(f"evidence payload digest mismatch: {digest}")
        objects.append({
            "digest": f"sha256:{digest}",
            "media_type": references[digest].media_type,
            "size": len(payload),
            "data_base64": base64.b64encode(payload).decode("ascii"),
        })

    document = {
        "schema": BUNDLE_SCHEMA,
        "checkpoint": checkpoint,
        "objects": objects,
    }
    bundle_id = sha256_bytes(BUNDLE_DOMAIN + canonical_json(document))
    return {**document, "bundle_id": bundle_id}


def extract_evidence_bundle(value: Any, output_dir: Path) -> dict[str, Any]:
    """Verify a self-contained bundle and safely extract payloads by digest.

    The destination must not already exist. Filenames are derived only from
    validated lowercase SHA-256 digests; untrusted evidence metadata is never
    used as a filesystem path.
    """
    summary = verify_evidence_bundle(value)
    target = Path(output_dir)
    if target.exists() or target.is_symlink():
        raise EvidenceEnvelopeError("output directory already exists")

    _, envelope = parse_portable(value["checkpoint"])
    references = {item.digest: item for item in envelope.evidence}
    target.parent.mkdir(parents=True, exist_ok=True)
    target.mkdir(exist_ok=False)
    extracted = []
    try:
        extensions = {
            "application/json": ".json",
            "application/x-ndjson": ".jsonl",
            "application/gzip": ".gz",
            "application/pgp-keys": ".asc",
            "application/pgp-signature": ".asc",
            "application/vnd.cyclonedx+json": ".json",
            "application/vnd.in-toto+json": ".json",
            "application/spdx+json": ".json",
            "text/plain": ".txt",
        }
        for item in value["objects"]:
            digest = item["digest"][7:]
            payload = base64.b64decode(item["data_base64"], validate=True)
            reference = references[digest]
            filename = digest + extensions.get(reference.media_type, ".bin")
            (target / filename).write_bytes(payload)
            entry = {
                "digest": f"sha256:{digest}",
                "file": filename,
                "size": len(payload),
                "media_type": reference.media_type,
                "evidence_type": reference.evidence_type,
            }
            if reference.uri is not None:
                entry["uri"] = reference.uri
            if reference.issuer is not None:
                entry["issuer"] = reference.issuer
            extracted.append(entry)

        manifest = {
            "schema": "bod-evidence-extraction-manifest-v0.1",
            "bundle_id": summary["bundle_id"],
            "checkpoint_id": summary["checkpoint_id"],
            "project_id": summary["project_id"],
            "objects": extracted,
        }
        (target / "manifest.json").write_text(
            json.dumps(manifest, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
            encoding="utf-8",
        )
    except Exception:
        shutil.rmtree(target, ignore_errors=True)
        raise

    return {
        "status": "BUNDLE_EXTRACTED",
        "bundle_id": summary["bundle_id"],
        "output_dir": str(target),
        "evidence_objects": len(extracted),
        "payload_bytes": summary["payload_bytes"],
        "manifest": str(target / "manifest.json"),
    }


def verify_evidence_bundle(value: Any) -> dict[str, Any]:
    """Verify bundle integrity and completeness; does not assert evidence truth."""
    if not isinstance(value, dict) or set(value) != {
        "schema", "checkpoint", "objects", "bundle_id"
    }:
        raise EvidenceEnvelopeError("invalid evidence bundle")
    if value["schema"] != BUNDLE_SCHEMA:
        raise EvidenceEnvelopeError("unsupported evidence bundle schema")
    bundle_id = value["bundle_id"]
    if not isinstance(bundle_id, str) or not re.fullmatch(r"[0-9a-f]{64}", bundle_id):
        raise EvidenceEnvelopeError("invalid bundle_id")
    durable = {
        "schema": value["schema"],
        "checkpoint": value["checkpoint"],
        "objects": value["objects"],
    }
    expected_bundle_id = sha256_bytes(BUNDLE_DOMAIN + canonical_json(durable))
    if bundle_id != expected_bundle_id:
        raise EvidenceEnvelopeError("bundle_id mismatch")

    _, envelope = parse_portable(value["checkpoint"])
    references = {item.digest: item for item in envelope.evidence}
    if len(references) != len(envelope.evidence):
        raise EvidenceEnvelopeError("one digest cannot have multiple evidence reference descriptors")
    objects = value["objects"]
    if not isinstance(objects, list):
        raise EvidenceEnvelopeError("bundle objects must be a list")

    observed: dict[str, bytes] = {}
    previous_digest: str | None = None
    for item in objects:
        if not isinstance(item, dict) or set(item) != {
            "digest", "media_type", "size", "data_base64"
        }:
            raise EvidenceEnvelopeError("invalid evidence object")
        digest_value = item["digest"]
        if not isinstance(digest_value, str) or not digest_value.startswith("sha256:"):
            raise EvidenceEnvelopeError("invalid evidence object digest")
        digest = digest_value[7:]
        if not re.fullmatch(r"[0-9a-f]{64}", digest):
            raise EvidenceEnvelopeError("invalid evidence object digest")
        if previous_digest is not None and digest <= previous_digest:
            raise EvidenceEnvelopeError("evidence objects must be unique and sorted")
        previous_digest = digest
        if digest not in references:
            raise EvidenceEnvelopeError("bundle contains an unreferenced evidence object")
        if item["media_type"] != references[digest].media_type:
            raise EvidenceEnvelopeError("evidence object media_type does not match reference")
        if type(item["size"]) is not int or item["size"] < 0:
            raise EvidenceEnvelopeError("invalid evidence object size")
        encoded = item["data_base64"]
        if not isinstance(encoded, str):
            raise EvidenceEnvelopeError("evidence object data must be base64 text")
        try:
            payload = base64.b64decode(encoded, validate=True)
        except (binascii.Error, ValueError) as exc:
            raise EvidenceEnvelopeError("invalid evidence object base64") from exc
        if len(payload) != item["size"]:
            raise EvidenceEnvelopeError("evidence object size mismatch")
        if sha256_bytes(payload) != digest:
            raise EvidenceEnvelopeError("evidence object digest mismatch")
        observed[digest] = payload

    if set(observed) != set(references):
        missing = sorted(set(references) - set(observed))
        raise EvidenceEnvelopeError(f"bundle is not self-contained; missing evidence payloads: {missing}")

    return {
        "bundle_id": bundle_id,
        "checkpoint_id": value["checkpoint"]["checkpoint_id"],
        "project_id": envelope.project_id,
        "evidence_objects": len(observed),
        "payload_bytes": sum(len(payload) for payload in observed.values()),
        "payloads_complete": True,
        "semantic_truth": "NOT_ASSERTED",
        "bundle_authenticity": "NOT_ASSERTED",
        "repository_source": "NOT_INCLUDED",
    }
