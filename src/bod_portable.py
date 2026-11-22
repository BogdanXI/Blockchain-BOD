from __future__ import annotations

import hashlib
import json
import os
import re
import stat
import subprocess
from pathlib import Path, PurePosixPath
from typing import Any

try:
    from bod_evidence_envelope import EvidenceEnvelopeError, EvidenceEnvelopeV0_1, verify_chain
except ImportError:
    from src.bod_evidence_envelope import EvidenceEnvelopeError, EvidenceEnvelopeV0_1, verify_chain

SNAPSHOT_SCHEMA = "bod-repository-snapshot-v0.1"
PORTABLE_SCHEMA = "bod-portable-checkpoint-v0.1"
SNAPSHOT_DOMAIN = b"BOD-REPOSITORY-SNAPSHOT-V0.1\0"
PORTABLE_DOMAIN = b"BOD-PORTABLE-CHECKPOINT-V0.1\0"


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


def verify_portable_chain(values: list[dict[str, Any]]) -> None:
    if not values:
        raise EvidenceEnvelopeError("portable checkpoint chain is empty")
    parsed = [parse_portable(v) for v in values]
    snapshots = [item[0] for item in parsed]
    envelopes = [item[1] for item in parsed]
    verify_chain(envelopes)
    roots = [snapshot["state_root"] for snapshot in snapshots]
    if roots != [envelope.state_root for envelope in envelopes] or len(set(roots)) != len(roots):
        raise EvidenceEnvelopeError("portable checkpoint state roots are inconsistent")
