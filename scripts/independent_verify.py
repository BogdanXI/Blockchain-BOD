#!/usr/bin/env python3
"""Independent BOD Evidence Envelope verifier.

This file intentionally does not import the BOD implementation. It is a small
reference implementation for cross-checking canonical serialization,
commitments, and predecessor lineage from exported JSON documents.
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

SCHEMA = "bod-evidence-envelope-v0.1"
DOMAIN = b"BOD-EVIDENCE-ENVELOPE-V0.1\0"
HEX = re.compile(r"^[0-9a-f]{64}$")


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def sha(value):
    return hashlib.sha256(value).hexdigest()


def commitment(document):
    durable = {k: document[k] for k in (
        "schema", "project_id", "protocol_version", "state_root",
        "predecessor_state_root", "transition_id", "evidence", "capture_boundary"
    )}
    evidence = sorted(durable["evidence"], key=canonical)
    durable = dict(durable)
    durable["evidence"] = evidence
    return sha(DOMAIN + canonical(durable))


def verify_one(document):
    required = {
        "schema", "project_id", "protocol_version", "state_root",
        "predecessor_state_root", "transition_id", "evidence",
        "capture_boundary", "envelope_id"
    }
    if set(document) != required or document["schema"] != SCHEMA:
        raise ValueError("unsupported envelope schema or fields")
    for field in ("state_root", "envelope_id"):
        if not isinstance(document[field], str) or not HEX.fullmatch(document[field]):
            raise ValueError(f"invalid {field}")
    predecessor = document["predecessor_state_root"]
    if predecessor is not None and (not isinstance(predecessor, str) or not HEX.fullmatch(predecessor)):
        raise ValueError("invalid predecessor_state_root")
    if not isinstance(document["evidence"], list):
        raise ValueError("evidence must be a list")
    for item in document["evidence"]:
        if not isinstance(item, dict) or not {"evidence_type", "digest", "media_type"} <= set(item):
            raise ValueError("invalid evidence reference")
        if not item["digest"].startswith("sha256:") or not HEX.fullmatch(item["digest"][7:]):
            raise ValueError("invalid evidence digest")
    if commitment(document) != document["envelope_id"]:
        raise ValueError("envelope_id does not match canonical commitment")


def verify_chain(documents):
    if not documents:
        raise ValueError("empty chain")
    for item in documents:
        verify_one(item)
    projects = {item["project_id"] for item in documents}
    if len(projects) != 1:
        raise ValueError("multiple projects")
    roots = [item["state_root"] for item in documents]
    if len(set(roots)) != len(roots):
        raise ValueError("duplicate state roots")
    by_root = {item["state_root"]: item for item in documents}
    genesis = [item for item in documents if item["predecessor_state_root"] is None]
    if len(genesis) != 1:
        raise ValueError("chain must contain exactly one genesis")
    successor_count = {}
    for item in documents:
        parent = item["predecessor_state_root"]
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
        root = current["state_root"]
        if root in visited:
            raise ValueError("cycle")
        visited.add(root)
        children = [item for item in documents if item["predecessor_state_root"] == root]
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
        if isinstance(value, dict) and "envelopes" in value:
            value = value["envelopes"]
        if sys.argv[-1] == "--chain":
            verify_chain(value if isinstance(value, list) else [value])
        else:
            verify_one(value)
        print(json.dumps({"status": "VALID_INTEGRITY"}, indent=2))
        return 0
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(json.dumps({"status": "INVALID", "reason": str(exc)}, indent=2))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
