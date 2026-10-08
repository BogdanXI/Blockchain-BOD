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


def verify_chain(envelopes: Iterable[EvidenceEnvelopeV0_1]) -> None:
    items = tuple(envelopes)
    if not items:
        raise EvidenceEnvelopeError("evidence chain is empty")
    if any(item.envelope_id != item.commitment() for item in items):
        raise EvidenceEnvelopeError("chain contains an invalid envelope commitment")
    projects = {item.project_id for item in items}
    if len(projects) != 1:
        raise EvidenceEnvelopeError("chain contains multiple projects")
    if len({item.state_root for item in items}) != len(items):
        raise EvidenceEnvelopeError("chain contains duplicate state roots")
    genesis = [item for item in items if item.predecessor_state_root is None]
    if len(genesis) != 1:
        raise EvidenceEnvelopeError("chain must contain exactly one genesis envelope")

    by_state = {item.state_root: item for item in items}
    successors: dict[str, int] = {}
    for item in items:
        if item.predecessor_state_root is None:
            continue
        predecessor = by_state.get(item.predecessor_state_root)
        if predecessor is None:
            raise EvidenceEnvelopeError("chain contains a missing predecessor")
        verify_lineage(predecessor, item)
        successors[item.predecessor_state_root] = successors.get(item.predecessor_state_root, 0) + 1
    if any(count > 1 for count in successors.values()):
        raise EvidenceEnvelopeError("chain contains a fork")

    visited: set[str] = set()
    current = genesis[0]
    while True:
        visited.add(current.state_root)
        next_items = [item for item in items if item.predecessor_state_root == current.state_root]
        if not next_items:
            break
        current = next_items[0]
    if visited != set(by_state):
        raise EvidenceEnvelopeError("chain contains a disconnected component")
