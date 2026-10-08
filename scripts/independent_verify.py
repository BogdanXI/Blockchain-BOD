#!/usr/bin/env python3
"""Independent verifier for BOD portable checkpoints.

This verifier intentionally has no import dependency on the BOD implementation.
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

ENVELOPE_SCHEMA = "bod-evidence-envelope-v0.1"
SNAPSHOT_SCHEMA = "bod-repository-snapshot-v0.1"
PORTABLE_SCHEMA = "bod-portable-checkpoint-v0.1"
ENVELOPE_DOMAIN = b"BOD-EVIDENCE-ENVELOPE-V0.1\0"
SNAPSHOT_DOMAIN = b"BOD-REPOSITORY-SNAPSHOT-V0.1\0"
PORTABLE_DOMAIN = b"BOD-PORTABLE-CHECKPOINT-V0.1\0"
HEX = re.compile(r"^[0-9a-f]{64}$")


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def sha(value):
    return hashlib.sha256(value).hexdigest()


def envelope_commitment(document):
    durable = {k: document[k] for k in (
        "schema", "project_id", "protocol_version", "state_root",
        "predecessor_state_root", "transition_id", "evidence", "capture_boundary"
    )}
    durable["evidence"] = sorted(durable["evidence"], key=canonical)
    return sha(ENVELOPE_DOMAIN + canonical(durable))


def verify_snapshot(snapshot):
    if not isinstance(snapshot, dict) or set(snapshot) != {"schema", "files", "state_root"}:
        raise ValueError("invalid repository snapshot")
    if snapshot["schema"] != SNAPSHOT_SCHEMA or not isinstance(snapshot["files"], list):
        raise ValueError("unsupported repository snapshot")
    seen = set()
    for item in snapshot["files"]:
        if not isinstance(item, dict) or set(item) != {"path", "sha256", "size"}:
            raise ValueError("invalid snapshot file entry")
        if item["path"] in seen:
            raise ValueError("duplicate snapshot path")
        seen.add(item["path"])
        if not HEX.fullmatch(item["sha256"]) or not isinstance(item["size"], int) or item["size"] < 0:
            raise ValueError("invalid snapshot file digest or size")
    durable = {"schema": snapshot["schema"], "files": snapshot["files"]}
    if sha(SNAPSHOT_DOMAIN + canonical(durable)) != snapshot["state_root"]:
        raise ValueError("snapshot state_root mismatch")


def verify_envelope(document):
    required = {"schema", "project_id", "protocol_version", "state_root", "predecessor_state_root", "transition_id", "evidence", "capture_boundary", "envelope_id"}
    if not isinstance(document, dict) or set(document) != required or document["schema"] != ENVELOPE_SCHEMA:
        raise ValueError("unsupported envelope schema or fields")
    for field in ("state_root", "envelope_id"):
        if not isinstance(document[field], str) or not HEX.fullmatch(document[field]):
            raise ValueError(f"invalid {field}")
    predecessor = document["predecessor_state_root"]
    if predecessor is not None and (not isinstance(predecessor, str) or not HEX.fullmatch(predecessor)):
        raise ValueError("invalid predecessor_state_root")
    if not isinstance(document["evidence"], list):
        raise ValueError("invalid evidence")
    for item in document["evidence"]:
        if not isinstance(item, dict) or not {"evidence_type", "digest", "media_type"} <= set(item):
            raise ValueError("invalid evidence reference")
        if not isinstance(item["digest"], str) or not item["digest"].startswith("sha256:") or not HEX.fullmatch(item["digest"][7:]):
            raise ValueError("invalid evidence digest")
    if envelope_commitment(document) != document["envelope_id"]:
        raise ValueError("envelope_id mismatch")


def portable_commitment(document):
    durable = {"schema": document["schema"], "snapshot": document["snapshot"], "envelope": document["envelope"]}
    return sha(PORTABLE_DOMAIN + canonical(durable))


def verify_portable(document):
    required = {"schema", "snapshot", "envelope", "checkpoint_id"}
    if not isinstance(document, dict) or set(document) != required or document["schema"] != PORTABLE_SCHEMA:
        raise ValueError("unsupported portable checkpoint")
    if not isinstance(document["checkpoint_id"], str) or not HEX.fullmatch(document["checkpoint_id"]):
        raise ValueError("invalid checkpoint_id")
    if portable_commitment(document) != document["checkpoint_id"]:
        raise ValueError("checkpoint_id mismatch")
    verify_snapshot(document["snapshot"])
    verify_envelope(document["envelope"])
    if document["snapshot"]["state_root"] != document["envelope"]["state_root"]:
        raise ValueError("snapshot/envelope state root mismatch")


def verify_chain(documents):
    if not documents:
        raise ValueError("empty checkpoint chain")
    for document in documents:
        verify_portable(document)
    envelopes = [d["envelope"] for d in documents]
    projects = {e["project_id"] for e in envelopes}
    if len(projects) != 1:
        raise ValueError("multiple projects")
    roots = [e["state_root"] for e in envelopes]
    if len(set(roots)) != len(roots):
        raise ValueError("duplicate state roots")
    by_root = {e["state_root"]: e for e in envelopes}
    genesis = [e for e in envelopes if e["predecessor_state_root"] is None]
    if len(genesis) != 1:
        raise ValueError("chain must contain exactly one genesis")
    successor_count = {}
    for e in envelopes:
        parent = e["predecessor_state_root"]
        if parent is None:
            continue
        if parent not in by_root:
            raise ValueError("missing predecessor")
        successor_count[parent] = successor_count.get(parent, 0) + 1
    if any(count > 1 for count in successor_count.values()):
        raise ValueError("fork")
    visited = set()
    current = genesis[0]
    while True:
        if current["state_root"] in visited:
            raise ValueError("cycle")
        visited.add(current["state_root"])
        children = [e for e in envelopes if e["predecessor_state_root"] == current["state_root"]]
        if not children:
            break
        current = children[0]
    if visited != set(by_root):
        raise ValueError("disconnected component")


def main():
    if len(sys.argv) not in (2, 3):
        print("usage: independent_verify.py FILE [--chain]", file=sys.stderr)
        return 2
    try:
        value = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
        if isinstance(value, dict) and "checkpoints" in value:
            value = value["checkpoints"]
        if sys.argv[-1] == "--chain":
            verify_chain(value if isinstance(value, list) else [value])
        elif isinstance(value, list):
            raise ValueError("list requires --chain")
        elif "schema" in value and value["schema"] == PORTABLE_SCHEMA:
            verify_portable(value)
        else:
            verify_envelope(value)
        print(json.dumps({"status": "VALID_INTEGRITY"}, indent=2))
        return 0
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(json.dumps({"status": "INVALID", "reason": str(exc)}, indent=2))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
