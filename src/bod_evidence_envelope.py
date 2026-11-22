"""Versioned, deterministic evidence envelopes for BOD continuity.

The envelope is the durable bridge between a BOD state transition and external
provenance/attestation systems. External evidence is referenced by digest;
payload semantics remain owned by the originating standard.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import re
from typing import Any, Iterable, Mapping, Sequence

_SCHEMA = "bod-evidence-envelope-v0.1"
_DOMAIN = b"BOD-EVIDENCE-ENVELOPE-V0.1\0"
_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


class EvidenceEnvelopeError(ValueError):
    """Invalid or unverifiable evidence envelope."""


def _canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _commit(document: Mapping[str, Any]) -> str:
    return hashlib.sha256(_DOMAIN + _canonical_bytes(document)).hexdigest()


def _require_sha256(value: str, field: str) -> str:
    if not isinstance(value, str) or not _SHA256_RE.fullmatch(value):
        raise EvidenceEnvelopeError(f"{field} must be a lowercase SHA-256 hex digest")
    return value


@dataclass(frozen=True)
class EvidenceReferenceV0_1:
    evidence_type: str
    digest: str
    media_type: str
    uri: str | None = None
    issuer: str | None = None

    def durable_document(self) -> dict[str, Any]:
        document: dict[str, Any] = {
            "evidence_type": self.evidence_type,
            "digest": f"sha256:{self.digest}",
            "media_type": self.media_type,
        }
        if self.uri is not None:
            document["uri"] = self.uri
        if self.issuer is not None:
            document["issuer"] = self.issuer
        return document

    @classmethod
    def from_document(cls, document: Mapping[str, Any]) -> "EvidenceReferenceV0_1":
        if not isinstance(document, Mapping):
            raise EvidenceEnvelopeError("evidence reference must be an object")
        allowed = {"evidence_type", "digest", "media_type", "uri", "issuer"}
        required = {"evidence_type", "digest", "media_type"}
        if set(document) - allowed or not required <= set(document):
            raise EvidenceEnvelopeError("invalid evidence reference fields")
        evidence_type = document["evidence_type"]
        media_type = document["media_type"]
        digest = document["digest"]
        if not all(isinstance(v, str) and v for v in (evidence_type, media_type, digest)):
            raise EvidenceEnvelopeError("evidence reference strings are invalid")
        if not digest.startswith("sha256:"):
            raise EvidenceEnvelopeError("evidence digest must use sha256:<digest>")
        digest_value = _require_sha256(digest[7:], "evidence digest")
        for field in ("uri", "issuer"):
            if field in document and document[field] is not None and (
                not isinstance(document[field], str) or not document[field]
            ):
                raise EvidenceEnvelopeError(f"{field} must be a non-empty string")
        return cls(
            evidence_type=evidence_type,
            digest=digest_value,
            media_type=media_type,
            uri=document.get("uri"),
            issuer=document.get("issuer"),
        )


@dataclass(frozen=True)
class EvidenceEnvelopeV0_1:
    project_id: str
    protocol_version: str
    state_root: str
    predecessor_state_root: str | None
    transition_id: str
    evidence: tuple[EvidenceReferenceV0_1, ...]
    capture_boundary: str
    envelope_id: str | None = None

    def durable_document(self) -> dict[str, Any]:
        evidence = sorted(
            (item.durable_document() for item in self.evidence),
            key=lambda item: _canonical_bytes(item),
        )
        return {
            "schema": _SCHEMA,
            "project_id": self.project_id,
            "protocol_version": self.protocol_version,
            "state_root": self.state_root,
            "predecessor_state_root": self.predecessor_state_root,
            "transition_id": self.transition_id,
            "evidence": evidence,
            "capture_boundary": self.capture_boundary,
        }

    def canonical_bytes(self) -> bytes:
        return _canonical_bytes(self.durable_document())

    def commitment(self) -> str:
        return _commit(self.durable_document())

    def to_document(self) -> dict[str, Any]:
        document = self.durable_document()
        document["envelope_id"] = self.envelope_id or self.commitment()
        return document

    @classmethod
    def from_document(cls, document: Mapping[str, Any]) -> "EvidenceEnvelopeV0_1":
        if not isinstance(document, Mapping):
            raise EvidenceEnvelopeError("envelope must be an object")
        required = {
            "schema", "project_id", "protocol_version", "state_root",
            "predecessor_state_root", "transition_id", "evidence",
            "capture_boundary", "envelope_id",
        }
        if set(document) != required or document["schema"] != _SCHEMA:
            raise EvidenceEnvelopeError("unsupported envelope schema")
        strings = ("project_id", "protocol_version", "transition_id", "capture_boundary")
        if any(not isinstance(document[field], str) or not document[field] for field in strings):
            raise EvidenceEnvelopeError("required envelope field is invalid")
        _require_sha256(document["state_root"], "state_root")
        predecessor = document["predecessor_state_root"]
        if predecessor is not None:
            _require_sha256(predecessor, "predecessor_state_root")
        evidence = document["evidence"]
        if not isinstance(evidence, list):
            raise EvidenceEnvelopeError("evidence must be a list")
        refs = tuple(EvidenceReferenceV0_1.from_document(item) for item in evidence)
        keys = {
            (r.evidence_type, r.digest, r.media_type, r.uri, r.issuer)
            for r in refs
        }
        if len(keys) != len(refs):
            raise EvidenceEnvelopeError("duplicate evidence references")
        envelope_id = _require_sha256(document["envelope_id"], "envelope_id")
        candidate = cls(
            project_id=document["project_id"],
            protocol_version=document["protocol_version"],
            state_root=document["state_root"],
            predecessor_state_root=predecessor,
            transition_id=document["transition_id"],
            evidence=refs,
            capture_boundary=document["capture_boundary"],
            envelope_id=envelope_id,
        )
        if candidate.commitment() != envelope_id:
            raise EvidenceEnvelopeError("envelope_id does not match canonical commitment")
        return candidate


def create_evidence_envelope(
    *,
    project_id: str,
    protocol_version: str,
    state_root: str,
    predecessor_state_root: str | None,
    transition_id: str,
    evidence: Sequence[EvidenceReferenceV0_1],
    capture_boundary: str,
) -> EvidenceEnvelopeV0_1:
    _require_sha256(state_root, "state_root")
    if predecessor_state_root is not None:
        _require_sha256(predecessor_state_root, "predecessor_state_root")
    if not project_id or not protocol_version or not transition_id or not capture_boundary:
        raise EvidenceEnvelopeError("required envelope field is empty")
    if not all(isinstance(item, EvidenceReferenceV0_1) for item in evidence):
        raise EvidenceEnvelopeError("evidence contains an unsupported reference")
    envelope = EvidenceEnvelopeV0_1(
        project_id=project_id,
        protocol_version=protocol_version,
        state_root=state_root,
        predecessor_state_root=predecessor_state_root,
        transition_id=transition_id,
        evidence=tuple(evidence),
        capture_boundary=capture_boundary,
    )
    return EvidenceEnvelopeV0_1.from_document(envelope.to_document())


def verify_lineage(previous: EvidenceEnvelopeV0_1, current: EvidenceEnvelopeV0_1) -> None:
    if previous.project_id != current.project_id:
        raise EvidenceEnvelopeError("lineage crosses project boundaries")
    if current.predecessor_state_root != previous.state_root:
        raise EvidenceEnvelopeError("predecessor linkage mismatch")
    if current.state_root == previous.state_root:
        raise EvidenceEnvelopeError("state root was replayed")


def verify_lineage_graph(envelopes: Iterable[EvidenceEnvelopeV0_1]) -> dict[str, Any]:
    """Verify a complete project lineage graph without choosing a canonical head.

    Multiple children of one predecessor are valid branches. The returned
    metadata identifies fork points and branch heads but does not rank them.
    """
    items = tuple(envelopes)
    if not items:
        raise EvidenceEnvelopeError("evidence graph is empty")
    if any(item.envelope_id != item.commitment() for item in items):
        raise EvidenceEnvelopeError("graph contains an invalid envelope commitment")
    projects = {item.project_id for item in items}
    if len(projects) != 1:
        raise EvidenceEnvelopeError("graph contains multiple projects")
    if len({item.state_root for item in items}) != len(items):
        raise EvidenceEnvelopeError("graph contains duplicate state roots")

    genesis = [item for item in items if item.predecessor_state_root is None]
    if len(genesis) != 1:
        raise EvidenceEnvelopeError("graph must contain exactly one genesis envelope")

    by_state = {item.state_root: item for item in items}
    children: dict[str, list[str]] = {root: [] for root in by_state}
    for item in items:
        parent_root = item.predecessor_state_root
        if parent_root is None:
            continue
        parent = by_state.get(parent_root)
        if parent is None:
            raise EvidenceEnvelopeError("graph contains a missing predecessor")
        verify_lineage(parent, item)
        children[parent_root].append(item.state_root)

    visited: set[str] = set()
    pending = [genesis[0].state_root]
    while pending:
        state_root = pending.pop()
        if state_root in visited:
            continue
        visited.add(state_root)
        pending.extend(children[state_root])
    if visited != set(by_state):
        raise EvidenceEnvelopeError("graph contains a disconnected component or cycle")

    fork_points = tuple(sorted(root for root, descendants in children.items() if len(descendants) > 1))
    heads = tuple(sorted(root for root, descendants in children.items() if not descendants))
    edges = tuple(sorted((parent, child) for parent, descendants in children.items() for child in descendants))
    return {
        "project_id": next(iter(projects)),
        "genesis_state_root": genesis[0].state_root,
        "state_roots": tuple(sorted(by_state)),
        "edges": edges,
        "fork_points": fork_points,
        "heads": heads,
    }


def verify_chain(envelopes: Iterable[EvidenceEnvelopeV0_1]) -> None:
    """Verify a single linear lineage; use verify_lineage_graph for branches."""
    graph = verify_lineage_graph(envelopes)
    if graph["fork_points"]:
        raise EvidenceEnvelopeError("chain contains a fork; verify it as a lineage graph")
