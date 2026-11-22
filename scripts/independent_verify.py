#!/usr/bin/env python3
"""Independent verifier for BOD portable checkpoints.

This verifier intentionally has no import dependency on the BOD implementation.
"""

from __future__ import annotations

import base64
import binascii
import hashlib
import json
import re
import sys
from pathlib import Path, PurePosixPath

ENVELOPE_SCHEMA = "bod-evidence-envelope-v0.1"
LEGACY_SNAPSHOT_SCHEMA = "bod-repository-snapshot-v0.1"
SNAPSHOT_SCHEMA = "bod-repository-snapshot-v0.2"
PORTABLE_SCHEMA = "bod-portable-checkpoint-v0.1"
BUNDLE_SCHEMA = "bod-evidence-bundle-v0.1"
ENVELOPE_DOMAIN = b"BOD-EVIDENCE-ENVELOPE-V0.1\0"
LEGACY_SNAPSHOT_DOMAIN = b"BOD-REPOSITORY-SNAPSHOT-V0.1\0"
SNAPSHOT_DOMAIN = b"BOD-REPOSITORY-SNAPSHOT-V0.2\0"
SNAPSHOT_DOMAINS = {LEGACY_SNAPSHOT_SCHEMA: LEGACY_SNAPSHOT_DOMAIN, SNAPSHOT_SCHEMA: SNAPSHOT_DOMAIN}
PORTABLE_DOMAIN = b"BOD-PORTABLE-CHECKPOINT-V0.1\0"
BUNDLE_DOMAIN = b"BOD-EVIDENCE-BUNDLE-V0.1\0"
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
    schema = snapshot["schema"]
    if schema not in SNAPSHOT_DOMAINS or not isinstance(snapshot["files"], list):
        raise ValueError("unsupported repository snapshot")
    expected_entry_fields = {"path", "sha256", "size"}
    if schema == SNAPSHOT_SCHEMA:
        expected_entry_fields.add("mode")
    if not isinstance(snapshot["state_root"], str) or not HEX.fullmatch(snapshot["state_root"]):
        raise ValueError("invalid snapshot state_root")

    previous_path = None
    for item in snapshot["files"]:
        if not isinstance(item, dict) or set(item) != expected_entry_fields:
            raise ValueError("invalid snapshot file entry")
        relative = item["path"]
        if not isinstance(relative, str) or not relative or chr(92) in relative or chr(0) in relative:
            raise ValueError("invalid snapshot path")
        portable_path = PurePosixPath(relative)
        if (
            portable_path.is_absolute()
            or not portable_path.parts
            or portable_path.as_posix() != relative
            or any(part in {".", ".."} for part in portable_path.parts)
            or portable_path.parts[0].endswith(":")
        ):
            raise ValueError("snapshot path is not a normalized relative path")
        if previous_path is not None and relative <= previous_path:
            raise ValueError("snapshot paths must be unique and sorted")
        previous_path = relative
        if not isinstance(item["sha256"], str) or not HEX.fullmatch(item["sha256"]):
            raise ValueError("invalid snapshot file digest")
        if type(item["size"]) is not int or item["size"] < 0:
            raise ValueError("invalid snapshot file size")
        if schema == SNAPSHOT_SCHEMA and (
            type(item["mode"]) is not int or item["mode"] not in {0o100644, 0o100755, 0o120000}
        ):
            raise ValueError("invalid snapshot Git-compatible file mode")

    durable = {"schema": snapshot["schema"], "files": snapshot["files"]}
    if sha(SNAPSHOT_DOMAINS[schema] + canonical(durable)) != snapshot["state_root"]:
        raise ValueError("snapshot state_root mismatch")


def verify_envelope(document):
    required = {"schema", "project_id", "protocol_version", "state_root", "predecessor_state_root", "transition_id", "evidence", "capture_boundary", "envelope_id"}
    if not isinstance(document, dict) or set(document) != required or document["schema"] != ENVELOPE_SCHEMA:
        raise ValueError("unsupported envelope schema or fields")

    for field in ("project_id", "protocol_version", "transition_id", "capture_boundary"):
        if not isinstance(document[field], str) or not document[field]:
            raise ValueError(f"invalid {field}")
    for field in ("state_root", "envelope_id"):
        if not isinstance(document[field], str) or not HEX.fullmatch(document[field]):
            raise ValueError(f"invalid {field}")

    predecessor = document["predecessor_state_root"]
    if predecessor is not None and (not isinstance(predecessor, str) or not HEX.fullmatch(predecessor)):
        raise ValueError("invalid predecessor_state_root")
    if not isinstance(document["evidence"], list):
        raise TypeError("invalid evidence")

    allowed = {"evidence_type", "digest", "media_type", "uri", "issuer"}
    required_evidence = {"evidence_type", "digest", "media_type"}
    seen_evidence = set()
    for item in document["evidence"]:
        if not isinstance(item, dict) or set(item) - allowed or not required_evidence <= set(item):
            raise ValueError("invalid evidence reference")
        for field in ("evidence_type", "media_type", "digest"):
            if not isinstance(item[field], str) or not item[field]:
                raise ValueError(f"invalid evidence {field}")
        if not item["digest"].startswith("sha256:") or not HEX.fullmatch(item["digest"][7:]):
            raise ValueError("invalid evidence digest")
        for field in ("uri", "issuer"):
            if field in item and item[field] is not None and (
                not isinstance(item[field], str) or not item[field]
            ):
                raise ValueError(f"invalid evidence {field}")
        key = canonical(item)
        if key in seen_evidence:
            raise ValueError("duplicate evidence reference")
        seen_evidence.add(key)

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


def verify_chain(documents, allow_forks=False):
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
    if any(count > 1 for count in successor_count.values()) and not allow_forks:
        raise ValueError("fork; use --graph to verify all branches")
    children_by_root = {root: [] for root in by_root}
    for envelope in envelopes:
        parent = envelope["predecessor_state_root"]
        if parent is not None:
            children_by_root[parent].append(envelope)
    visited = set()
    pending = [genesis[0]]
    while pending:
        current = pending.pop()
        root = current["state_root"]
        if root in visited:
            continue
        visited.add(root)
        pending.extend(children_by_root[root])
    if visited != set(by_root):
        raise ValueError("disconnected component or cycle")



def verify_bundle(document):
    required = {"schema", "checkpoint", "objects", "bundle_id"}
    if not isinstance(document, dict) or set(document) != required:
        raise ValueError("invalid evidence bundle")
    if document["schema"] != BUNDLE_SCHEMA:
        raise ValueError("unsupported evidence bundle")
    bundle_id = document["bundle_id"]
    if not isinstance(bundle_id, str) or not HEX.fullmatch(bundle_id):
        raise ValueError("invalid bundle_id")
    durable = {
        "schema": document["schema"],
        "checkpoint": document["checkpoint"],
        "objects": document["objects"],
    }
    if sha(BUNDLE_DOMAIN + canonical(durable)) != bundle_id:
        raise ValueError("bundle_id mismatch")

    verify_portable(document["checkpoint"])
    evidence = document["checkpoint"]["envelope"]["evidence"]
    references = {}
    for item in evidence:
        digest = item["digest"][7:]
        if digest in references:
            raise ValueError("one digest has multiple evidence reference descriptors")
        references[digest] = item
    if not isinstance(document["objects"], list):
        raise TypeError("bundle objects must be a list")

    observed = set()
    previous_digest = None
    for item in document["objects"]:
        if not isinstance(item, dict) or set(item) != {"digest", "media_type", "size", "data_base64"}:
            raise ValueError("invalid evidence object")
        digest_value = item["digest"]
        if not isinstance(digest_value, str) or not digest_value.startswith("sha256:"):
            raise ValueError("invalid evidence object digest")
        digest = digest_value[7:]
        if not HEX.fullmatch(digest):
            raise ValueError("invalid evidence object digest")
        if previous_digest is not None and digest <= previous_digest:
            raise ValueError("evidence objects must be unique and sorted")
        previous_digest = digest
        if digest not in references:
            raise ValueError("unreferenced evidence object")
        if item["media_type"] != references[digest]["media_type"]:
            raise ValueError("evidence media type mismatch")
        if type(item["size"]) is not int or item["size"] < 0:
            raise ValueError("invalid evidence object size")
        try:
            payload = base64.b64decode(item["data_base64"], validate=True)
        except (binascii.Error, ValueError, TypeError) as exc:
            raise ValueError("invalid evidence object base64") from exc
        if len(payload) != item["size"]:
            raise ValueError("evidence object size mismatch")
        if sha(payload) != digest:
            raise ValueError("evidence object digest mismatch")
        observed.add(digest)
    if observed != set(references):
        raise ValueError("bundle is not self-contained; missing evidence payloads")


def main():
    if len(sys.argv) not in (2, 3):
        print("usage: independent_verify.py FILE [--chain|--graph]", file=sys.stderr)
        return 2
    try:
        value = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
        if isinstance(value, dict) and value.get("schema") == BUNDLE_SCHEMA:
            if len(sys.argv) != 2:
                raise ValueError("bundle verification does not accept chain flags")
            verify_bundle(value)
            print(json.dumps({"status": "VALID_SELF_CONTAINED_BUNDLE"}, indent=2))
            return 0
        if isinstance(value, dict) and "checkpoints" in value:
            value = value["checkpoints"]
        if sys.argv[-1] == "--chain":
            verify_chain(value if isinstance(value, list) else [value])
        elif sys.argv[-1] == "--graph":
            verify_chain(value if isinstance(value, list) else [value], allow_forks=True)
        elif isinstance(value, list):
            raise ValueError("list requires --chain")
        elif "schema" in value and value["schema"] == PORTABLE_SCHEMA:
            verify_portable(value)
        else:
            verify_envelope(value)
        print(json.dumps({"status": "VALID_INTEGRITY"}, indent=2))
        return 0
    except (OSError, json.JSONDecodeError, TypeError, ValueError) as exc:
        print(json.dumps({"status": "INVALID", "reason": str(exc)}, indent=2))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
