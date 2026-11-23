"""Validation for the versioned BOD Ethereum release evidence profile."""

from __future__ import annotations

import re
from datetime import datetime
from typing import Any
from urllib.parse import urlsplit

PROFILE_ID = "bod-ethereum-release-profile-v0.1"
_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_COMMIT = re.compile(r"^(?:[0-9a-f]{40}|[0-9a-f]{64})$")
_TREE = re.compile(r"^(?:sha1:[0-9a-f]{40}|sha256:[0-9a-f]{64})$")
_TX = re.compile(r"^0x[0-9a-fA-F]{64}$")
_ADDRESS = re.compile(r"^0x[0-9a-fA-F]{40}$")


class ReleaseProfileError(ValueError):
    """Raised when an Ethereum release profile is structurally invalid."""


def _object(value: Any, field: str, required: set[str], optional: set[str] = set()) -> dict:
    if not isinstance(value, dict):
        raise ReleaseProfileError(f"{field} must be an object")
    keys = set(value)
    if required - keys:
        raise ReleaseProfileError(f"{field} missing fields: {sorted(required - keys)}")
    if keys - required - optional:
        raise ReleaseProfileError(f"{field} has unknown fields: {sorted(keys - required - optional)}")
    return value


def _string(value: Any, field: str, maximum: int = 4096) -> str:
    if not isinstance(value, str) or not value.strip() or len(value) > maximum:
        raise ReleaseProfileError(f"{field} must be a non-empty string of at most {maximum} characters")
    return value


def _uri(value: Any, field: str, schemes: frozenset[str] = frozenset({"https", "http", "urn"})) -> str:
    text = _string(value, field)
    parsed = urlsplit(text)
    if parsed.scheme not in schemes or (parsed.scheme in {"http", "https"} and not parsed.netloc):
        raise ReleaseProfileError(f"{field} must be an absolute URI using an allowed scheme")
    return text


def _digest(value: Any, field: str) -> str:
    text = _string(value, field)
    if not _SHA256.fullmatch(text):
        raise ReleaseProfileError(f"{field} must be lowercase SHA-256 hex")
    return text


def _compiler(value: Any, field: str) -> list[str]:
    item = _object(
        value, field,
        {"name", "version", "settings_digest", "input_digest", "bytecode_digest", "abi_digest"},
    )
    for key in ("name", "version"):
        _string(item[key], f"{field}.{key}", 256)
    missing = []
    gap_types = {
        "settings_digest": "compiler-settings",
        "input_digest": "compiler-input",
        "bytecode_digest": "compiler-bytecode",
        "abi_digest": "compiler-abi",
    }
    for key, gap_type in gap_types.items():
        if item[key] is None:
            missing.append(gap_type)
        else:
            _digest(item[key], f"{field}.{key}")
    return missing


def validate_release_profile(value: Any) -> dict[str, Any]:
    """Validate profile structure and cross-field release semantics.

    This checks the profile record only. It does not fetch artifacts, verify
    signatures, query Ethereum, validate compiler output or establish truth.
    """
    document = _object(
        value, "profile",
        {"profile", "project", "release", "predecessor", "build", "deployment", "evidence", "gaps", "witnesses"},
    )
    if document["profile"] != PROFILE_ID:
        raise ReleaseProfileError("unsupported Ethereum release profile identifier")

    project = _object(document["project"], "project", {"id", "kind", "repository"})
    _string(project["id"], "project.id", 128)
    if not isinstance(project["kind"], str) or project["kind"] not in {"ethereum-client", "smart-contract", "developer-tool"}:
        raise ReleaseProfileError("project.kind is unsupported")
    _uri(project["repository"], "project.repository", frozenset({"https"}))

    release = _object(
        document["release"], "release",
        {"id", "kind", "sequence", "source_commit", "source_tree"},
    )
    _string(release["id"], "release.id", 128)
    if not isinstance(release["kind"], str) or release["kind"] not in {"software-release", "contract-deployment", "contract-upgrade"}:
        raise ReleaseProfileError("release.kind is unsupported")
    if type(release["sequence"]) is not int or release["sequence"] < 0:
        raise ReleaseProfileError("release.sequence must be a non-negative integer")
    required_gap_types = []
    if release["source_commit"] is None:
        required_gap_types.append("source-commit")
    elif not isinstance(release["source_commit"], str) or not _COMMIT.fullmatch(release["source_commit"]):
        raise ReleaseProfileError("release.source_commit must be null or a full lowercase Git commit ID")
    if release["source_tree"] is None:
        required_gap_types.append("source-tree")
    elif not isinstance(release["source_tree"], str) or not _TREE.fullmatch(release["source_tree"]):
        raise ReleaseProfileError("release.source_tree must be null or use sha1:<hex> or sha256:<hex>")

    predecessor = document["predecessor"]
    if predecessor is not None:
        predecessor = _object(predecessor, "predecessor", {"release_id", "checkpoint_id"})
        _string(predecessor["release_id"], "predecessor.release_id", 128)
        _digest(predecessor["checkpoint_id"], "predecessor.checkpoint_id")
        if predecessor["release_id"] == release["id"]:
            raise ReleaseProfileError("release cannot name itself as predecessor")

    build = document["build"]
    if build is not None:
        build = _object(build, "build", {"builder_id", "provenance_digest", "compiler"})
        if build["builder_id"] is None:
            required_gap_types.append("builder-identity")
        else:
            _uri(build["builder_id"], "build.builder_id")
        if build["provenance_digest"] is None:
            required_gap_types.append("build-provenance")
        else:
            _digest(build["provenance_digest"], "build.provenance_digest")
        if build["compiler"] is not None:
            required_gap_types.extend(_compiler(build["compiler"], "build.compiler"))

    deployment = document["deployment"]
    contract_release = release["kind"] in {"contract-deployment", "contract-upgrade"}
    if contract_release:
        if project["kind"] != "smart-contract":
            raise ReleaseProfileError("contract deployment/upgrade requires project.kind=smart-contract")
        if build is None or build["compiler"] is None:
            raise ReleaseProfileError("contract deployment/upgrade requires compiler build evidence")
        deployment = _object(
            deployment, "deployment",
            {"chain_id", "transaction_hash", "block_hash", "block_number", "contract_address", "runtime_bytecode_digest", "finality"},
            {"source_verification"},
        )
        if type(deployment["chain_id"]) is not int or deployment["chain_id"] < 1:
            raise ReleaseProfileError("deployment.chain_id must be a positive integer")
        if not isinstance(deployment["transaction_hash"], str) or not _TX.fullmatch(deployment["transaction_hash"]):
            raise ReleaseProfileError("deployment.transaction_hash must be a 32-byte 0x hash")
        if not isinstance(deployment["block_hash"], str) or not _TX.fullmatch(deployment["block_hash"]):
            raise ReleaseProfileError("deployment.block_hash must be a 32-byte 0x hash")
        if type(deployment["block_number"]) is not int or deployment["block_number"] < 0:
            raise ReleaseProfileError("deployment.block_number must be a non-negative integer")
        if not isinstance(deployment["contract_address"], str) or not _ADDRESS.fullmatch(deployment["contract_address"]):
            raise ReleaseProfileError("deployment.contract_address must be a 20-byte 0x address")
        if deployment["runtime_bytecode_digest"] is None:
            required_gap_types.append("deployment-runtime-bytecode")
        else:
            _digest(deployment["runtime_bytecode_digest"], "deployment.runtime_bytecode_digest")
        finality = _object(deployment["finality"], "deployment.finality", {"status", "observed_at", "source"})
        finality_statuses = {"NOT_CHECKED", "SAFE", "FINALIZED", "REORGED", "UNKNOWN"}
        if not isinstance(finality["status"], str) or finality["status"] not in finality_statuses:
            raise ReleaseProfileError("deployment.finality.status is unsupported")
        observed_at = finality["observed_at"]
        finality_source = finality["source"]
        if finality["status"] in {"SAFE", "FINALIZED", "REORGED"}:
            _string(observed_at, "deployment.finality.observed_at", 64)
            try:
                parsed_time = datetime.fromisoformat(observed_at.replace("Z", "+00:00"))
            except ValueError as exc:
                raise ReleaseProfileError("deployment.finality.observed_at must be RFC 3339 date-time") from exc
            if parsed_time.tzinfo is None:
                raise ReleaseProfileError("deployment.finality.observed_at must include a timezone")
            _uri(finality_source, "deployment.finality.source")
        elif observed_at is not None or finality_source is not None:
            raise ReleaseProfileError("unchecked or unknown finality must use null observed_at and source")
        source_verification = deployment.get("source_verification")
        if source_verification is None:
            required_gap_types.append("sourcify-match-classification")
        else:
            source_verification = _object(source_verification, "deployment.source_verification", {"provider", "reference", "match_type"})
            _string(source_verification["provider"], "deployment.source_verification.provider", 128)
            _uri(source_verification["reference"], "deployment.source_verification.reference")
            if source_verification["match_type"] is None:
                required_gap_types.append("sourcify-match-classification")
            elif not isinstance(source_verification["match_type"], str) or source_verification["match_type"] not in {"exact_match", "match"}:
                raise ReleaseProfileError("deployment.source_verification.match_type is unsupported")
    elif deployment is not None:
        raise ReleaseProfileError("deployment data is only valid for contract-deployment or contract-upgrade releases")

    evidence = document["evidence"]
    if not isinstance(evidence, list):
        raise ReleaseProfileError("evidence must be an array")
    seen_evidence = set()
    for index, entry in enumerate(evidence):
        field = f"evidence[{index}]"
        entry = _object(entry, field, {"type", "digest", "media_type", "verification_status"}, {"uri", "issuer", "verification_method"})
        evidence_type = _string(entry["type"], f"{field}.type", 128)
        digest = _digest(entry["digest"], f"{field}.digest")
        _string(entry["media_type"], f"{field}.media_type", 256)
        if not isinstance(entry["verification_status"], str) or entry["verification_status"] not in {"NOT_CHECKED", "VALID", "INVALID", "UNAVAILABLE"}:
            raise ReleaseProfileError(f"{field}.verification_status is unsupported")
        if entry["verification_status"] in {"VALID", "INVALID"} and "verification_method" not in entry:
            raise ReleaseProfileError(f"{field}.verification_method is required for a verification result")
        if "verification_method" in entry:
            _string(entry["verification_method"], f"{field}.verification_method", 2048)
        if "uri" in entry:
            _uri(entry["uri"], f"{field}.uri")
        if "issuer" in entry:
            _uri(entry["issuer"], f"{field}.issuer")
        identity = (evidence_type, digest)
        if identity in seen_evidence:
            raise ReleaseProfileError("duplicate evidence type/digest pair")
        seen_evidence.add(identity)

    gaps = document["gaps"]
    if not isinstance(gaps, list):
        raise ReleaseProfileError("gaps must be an array")
    seen_gaps = set()
    for index, gap in enumerate(gaps):
        field = f"gaps[{index}]"
        gap = _object(gap, field, {"type", "status", "reason"})
        gap_type = _string(gap["type"], f"{field}.type", 128)
        if not isinstance(gap["status"], str) or gap["status"] not in {"NOT_PROVIDED", "NOT_CHECKED", "UNAVAILABLE", "INVALID"}:
            raise ReleaseProfileError(f"{field}.status is unsupported")
        _string(gap["reason"], f"{field}.reason", 2048)
        if gap_type in seen_gaps:
            raise ReleaseProfileError("duplicate gap type")
        seen_gaps.add(gap_type)

    undeclared_missing = sorted(set(required_gap_types) - seen_gaps)
    if undeclared_missing:
        raise ReleaseProfileError(
            f"missing explicit gap records for unavailable fields: {undeclared_missing}"
        )

    witnesses = _object(document["witnesses"], "witnesses", {"ethereum_registry_checkpoint", "eas_attestation_uid"})
    registry = witnesses["ethereum_registry_checkpoint"]
    if registry is not None:
        _digest(registry, "witnesses.ethereum_registry_checkpoint")
    eas_uid = witnesses["eas_attestation_uid"]
    if eas_uid is not None and (not isinstance(eas_uid, str) or not _TX.fullmatch(eas_uid)):
        raise ReleaseProfileError("witnesses.eas_attestation_uid must be a 32-byte 0x UID")

    return {
        "status": "VALID_PROFILE_STRUCTURE",
        "profile": PROFILE_ID,
        "project_id": project["id"],
        "release_id": release["id"],
        "release_kind": release["kind"],
        "evidence_items": len(evidence),
        "declared_gaps": len(gaps),
        "deployment_present": deployment is not None,
        "cryptographic_verification": "NOT_PERFORMED",
        "chain_state_verification": "NOT_PERFORMED",
        "semantic_truth": "NOT_ASSERTED",
    }
