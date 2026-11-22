"""Minimal, dependency-free structural inspection for common evidence formats.

This module does not perform cryptographic signature verification or full
standards-schema validation. It only checks the documented structural boundary
needed to classify and safely hand evidence to dedicated verifiers.
"""

from __future__ import annotations

import base64
import binascii
import json
import re
from typing import Any


class EvidenceFormatError(ValueError):
    """Evidence payload is malformed or does not match the requested format."""


INTOTO_STATEMENT_V1 = "https://in-toto.io/Statement/v1"
SLSA_PROVENANCE_V1 = "https://slsa.dev/provenance/v1"
DSSE_IN_TOTO_PAYLOAD = "application/vnd.in-toto+json"
SPDX_DOCUMENT_ID = "SPDXRef-DOCUMENT"


def _require_object(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise EvidenceFormatError(f"{label} must be a JSON object")
    return value


def _require_string(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise EvidenceFormatError(f"{label} must be a non-empty string")
    return value


def _validate_statement(document: Any) -> dict[str, Any]:
    statement = _require_object(document, "in-toto statement")
    if statement.get("_type") != INTOTO_STATEMENT_V1:
        raise EvidenceFormatError("unsupported in-toto statement type")
    subjects = statement.get("subject")
    if not isinstance(subjects, list):
        raise EvidenceFormatError("in-toto subject must be an array")
    for index, subject_value in enumerate(subjects):
        subject = _require_object(subject_value, f"subject[{index}]")
        digest = _require_object(subject.get("digest"), f"subject[{index}].digest")
        if not digest:
            raise EvidenceFormatError(f"subject[{index}].digest must not be empty")
        for algorithm, value in digest.items():
            _require_string(algorithm, f"subject[{index}] digest algorithm")
            _require_string(value, f"subject[{index}] digest value")
        if "name" in subject and subject["name"] is not None:
            _require_string(subject["name"], f"subject[{index}].name")
    _require_string(statement.get("predicateType"), "predicateType")
    if "predicate" in statement and statement["predicate"] is not None:
        _require_object(statement["predicate"], "predicate")
    return statement


def _validate_slsa(statement: dict[str, Any]) -> dict[str, Any]:
    if statement.get("predicateType") != SLSA_PROVENANCE_V1:
        raise EvidenceFormatError("statement is not SLSA provenance v1")
    predicate = _require_object(statement.get("predicate"), "SLSA predicate")
    build_definition = _require_object(
        predicate.get("buildDefinition"), "SLSA buildDefinition"
    )
    _require_string(build_definition.get("buildType"), "SLSA buildType")
    _require_object(
        build_definition.get("externalParameters"), "SLSA externalParameters"
    )
    if "resolvedDependencies" in build_definition and not isinstance(
        build_definition["resolvedDependencies"], list
    ):
        raise EvidenceFormatError("SLSA resolvedDependencies must be an array")

    run_details = _require_object(predicate.get("runDetails"), "SLSA runDetails")
    builder = _require_object(run_details.get("builder"), "SLSA builder")
    builder_id = _require_string(builder.get("id"), "SLSA builder.id")
    if "metadata" in run_details and run_details["metadata"] is not None:
        _require_object(run_details["metadata"], "SLSA metadata")
    return {
        "format": "slsa-provenance-v1",
        "builder_id": builder_id,
        "subject_count": len(statement["subject"]),
        "build_type": build_definition["buildType"],
    }


def _validate_cyclonedx(document: Any) -> dict[str, Any]:
    bom = _require_object(document, "CycloneDX BOM")
    if bom.get("bomFormat") != "CycloneDX":
        raise EvidenceFormatError("CycloneDX bomFormat must equal CycloneDX")
    spec_version = _require_string(bom.get("specVersion"), "CycloneDX specVersion")
    if "version" in bom and (
        type(bom["version"]) is not int or bom["version"] < 1
    ):
        raise EvidenceFormatError("CycloneDX version must be a positive integer")
    components = bom.get("components", [])
    if not isinstance(components, list):
        raise EvidenceFormatError("CycloneDX components must be an array")
    if "metadata" in bom and bom["metadata"] is not None:
        _require_object(bom["metadata"], "CycloneDX metadata")
    return {
        "format": "cyclonedx-json",
        "spec_version": spec_version,
        "bom_version": bom.get("version"),
        "component_count": len(components),
    }


def _validate_spdx(document: Any) -> dict[str, Any]:
    spdx = _require_object(document, "SPDX document")
    version = _require_string(spdx.get("spdxVersion"), "SPDX spdxVersion")
    if not version.startswith("SPDX-2."):
        raise EvidenceFormatError(
            "this inspector currently supports SPDX JSON 2.x only; SPDX 3.x is not implemented"
        )
    if spdx.get("dataLicense") != "CC0-1.0":
        raise EvidenceFormatError("SPDX dataLicense must equal CC0-1.0")
    if spdx.get("SPDXID") != SPDX_DOCUMENT_ID:
        raise EvidenceFormatError("SPDX document SPDXID must equal SPDXRef-DOCUMENT")
    _require_string(spdx.get("name"), "SPDX name")
    namespace = _require_string(spdx.get("documentNamespace"), "SPDX documentNamespace")
    if not namespace.startswith(("https://", "http://")):
        raise EvidenceFormatError("SPDX documentNamespace must be an HTTP(S) URI")
    creation = _require_object(spdx.get("creationInfo"), "SPDX creationInfo")
    created = _require_string(creation.get("created"), "SPDX creationInfo.created")
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", created):
        raise EvidenceFormatError("SPDX creationInfo.created must use UTC RFC3339 seconds")
    creators = creation.get("creators")
    if not isinstance(creators, list) or not creators:
        raise EvidenceFormatError("SPDX creationInfo.creators must be a non-empty array")
    if any(not isinstance(item, str) or not item.strip() for item in creators):
        raise EvidenceFormatError("SPDX creators must be non-empty strings")
    packages = spdx.get("packages", [])
    if not isinstance(packages, list):
        raise EvidenceFormatError("SPDX packages must be an array")
    return {
        "format": "spdx-json-2",
        "spec_version": version,
        "package_count": len(packages),
    }


def _decode_dsse(document: Any) -> tuple[dict[str, Any], int]:
    envelope = _require_object(document, "DSSE envelope")
    if envelope.get("payloadType") != DSSE_IN_TOTO_PAYLOAD:
        raise EvidenceFormatError("unsupported DSSE payloadType")
    encoded_payload = envelope.get("payload")
    if not isinstance(encoded_payload, str):
        raise EvidenceFormatError("DSSE payload must be base64 text")
    try:
        payload = base64.b64decode(encoded_payload, validate=True)
    except (binascii.Error, ValueError) as exc:
        raise EvidenceFormatError("invalid DSSE payload base64") from exc
    signatures = envelope.get("signatures")
    if not isinstance(signatures, list) or not signatures:
        raise EvidenceFormatError("DSSE signatures must be a non-empty array")
    for index, signature_value in enumerate(signatures):
        signature = _require_object(signature_value, f"DSSE signatures[{index}]")
        encoded_signature = signature.get("sig")
        if not isinstance(encoded_signature, str):
            raise EvidenceFormatError(f"DSSE signatures[{index}].sig must be base64 text")
        try:
            decoded_signature = base64.b64decode(encoded_signature, validate=True)
        except (binascii.Error, ValueError) as exc:
            raise EvidenceFormatError("invalid DSSE signature base64") from exc
        if not decoded_signature:
            raise EvidenceFormatError("DSSE signature must not be empty")
        if "keyid" in signature and signature["keyid"] is not None:
            _require_string(signature["keyid"], f"DSSE signatures[{index}].keyid")
    try:
        statement = json.loads(payload.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise EvidenceFormatError("DSSE payload is not UTF-8 JSON") from exc
    return _validate_statement(statement), len(signatures)


def inspect_evidence_payload(
    payload: bytes, format_hint: str = "auto"
) -> dict[str, Any]:
    """Inspect supported evidence structure without asserting authenticity."""
    if not isinstance(payload, bytes):
        raise EvidenceFormatError("evidence payload must be bytes")
    try:
        document = json.loads(payload.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise EvidenceFormatError("evidence payload is not UTF-8 JSON") from exc

    supported = {"auto", "in-toto", "slsa-provenance", "cyclonedx-json", "spdx-json", "dsse"}
    if format_hint not in supported:
        raise EvidenceFormatError(f"unsupported format hint: {format_hint}")

    dsse_signatures = None
    if format_hint == "dsse" or (
        format_hint == "auto" and isinstance(document, dict) and "payloadType" in document
    ):
        statement, dsse_signatures = _decode_dsse(document)
        detected = "in-toto" if statement.get("predicateType") != SLSA_PROVENANCE_V1 else "slsa-provenance"
    else:
        statement = document
        detected = format_hint
        if format_hint == "auto":
            if isinstance(document, dict) and document.get("bomFormat") == "CycloneDX":
                detected = "cyclonedx-json"
            elif isinstance(document, dict) and isinstance(document.get("spdxVersion"), str):
                detected = "spdx-json"
            elif isinstance(document, dict) and document.get("_type") == INTOTO_STATEMENT_V1:
                detected = (
                    "slsa-provenance"
                    if document.get("predicateType") == SLSA_PROVENANCE_V1
                    else "in-toto"
                )
            else:
                raise EvidenceFormatError("unrecognized evidence JSON format")

    if detected == "slsa-provenance":
        result = _validate_slsa(_validate_statement(statement))
    elif detected == "in-toto":
        _validate_statement(statement)
        result = {
            "format": "in-toto-statement-v1",
            "subject_count": len(statement["subject"]),
            "predicate_type": statement["predicateType"],
        }
    elif detected == "cyclonedx-json":
        result = _validate_cyclonedx(statement)
    elif detected == "spdx-json":
        result = _validate_spdx(statement)
    else:
        raise EvidenceFormatError(f"unsupported evidence format: {detected}")

    return {
        **result,
        "structure": "VALID",
        "signature_verification": "NOT_PERFORMED",
        "semantic_truth": "NOT_ASSERTED",
        "dsse_signature_count": dsse_signatures,
    }
