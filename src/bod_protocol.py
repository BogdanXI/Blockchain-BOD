"""Deterministic BOD Protocol v0.1 object and lifecycle state machine.

The module intentionally separates protocol commitments from a production
signature primitive. Signatures are injected through a verifier callback;
tests use HMAC only as a deterministic fixture.
"""
from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
import hmac
import json
from typing import Callable, Dict, Mapping, Optional


class ProtocolError(ValueError):
    pass


DOMAIN = {
    "task": "BOD/TASK/v0.1",
    "candidate": "BOD/CANDIDATE/v0.1",
    "verification": "BOD/VERIFICATION/v0.1",
    "settlement": "BOD/SETTLEMENT/v0.1",
}

VERIFY_RESULTS = {"VALID", "INVALID", "INCONCLUSIVE"}
TASK_STATUSES = {"OPEN", "SETTLED", "EXPIRED"}
CANDIDATE_STATUSES = {"SUBMITTED", "SELECTED", "REJECTED"}


def canonical_bytes(value: Mapping[str, object]) -> bytes:
    """Return one deterministic JSON representation for protocol envelopes."""
    try:
        encoded = json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        ).encode("utf-8")
    except (TypeError, ValueError) as exc:
        raise ProtocolError("value is not canonically encodable") from exc
    return encoded


def commitment(object_type: str, payload: Mapping[str, object]) -> str:
    if object_type not in DOMAIN:
        raise ProtocolError("unknown object type")
    material = DOMAIN[object_type].encode("utf-8") + b"\0" + canonical_bytes(payload)
    return hashlib.sha256(material).hexdigest()


def sign_fixture(key: bytes, object_type: str, payload: Mapping[str, object]) -> str:
    """Test-only deterministic signer; not a production asymmetric signature."""
    if not isinstance(key, bytes):
        raise ProtocolError("fixture key must be bytes")
    material = DOMAIN[object_type].encode("utf-8") + b"\0" + canonical_bytes(payload)
    return hmac.new(key, material, hashlib.sha256).hexdigest()


SignatureVerifier = Callable[[str, Mapping[str, object], str], bool]


def fixture_verifier(keys: Mapping[str, bytes]) -> SignatureVerifier:
    def verify(object_type: str, payload: Mapping[str, object], signature: str) -> bool:
        signer = payload.get(_signer_field(object_type))
        key = keys.get(str(signer))
        return key is not None and hmac.compare_digest(
            sign_fixture(key, object_type, payload), signature
        )
    return verify


def _signer_field(object_type: str) -> str:
    return {
        "task": "requester",
        "candidate": "executor",
        "verification": "verifier",
        "settlement": "settler",
    }[object_type]


def _required(object_type: str) -> tuple[str, ...]:
    return {
        "task": (
            "task_id", "project_id", "parent_state_root", "task_spec_hash",
            "acceptance_policy_hash", "reward_amount_bod", "deadline",
            "requester", "request_nonce",
        ),
        "candidate": (
            "candidate_id", "task_id", "parent_state_root",
            "candidate_state_root", "result_artifact_hash",
            "execution_manifest_hash", "evidence_root", "executor",
            "candidate_nonce", "bond_amount_bod",
        ),
        "verification": (
            "verification_id", "candidate_id", "candidate_hash",
            "evidence_root", "acceptance_policy_hash", "verification_result",
            "verifier", "verification_epoch", "verifier_nonce", "report_hash",
        ),
    }[object_type]


def _validate_envelope(
    object_type: str,
    payload: Mapping[str, object],
    signature: str,
    verifier: SignatureVerifier,
) -> None:
    if object_type not in DOMAIN:
        raise ProtocolError("unknown object type")
    if not isinstance(payload, Mapping):
        raise ProtocolError("payload must be a mapping")
    if set(payload) != set(_required(object_type)):
        raise ProtocolError("envelope fields are not exactly the v0.1 schema")
    if any(not isinstance(k, str) for k in payload):
        raise ProtocolError("field names must be strings")
    if not isinstance(signature, str) or not signature:
        raise ProtocolError("signature is required")
    if not verifier(object_type, payload, signature):
        raise ProtocolError("invalid signature")

    object_id_field = {
        "task": "task_id",
        "candidate": "candidate_id",
        "verification": "verification_id",
    }[object_type]
    supplied_id = payload[object_id_field]
    unsigned_payload = dict(payload)
    unsigned_payload.pop(object_id_field)
    expected = commitment(object_type, unsigned_payload)
    if not isinstance(supplied_id, str) or supplied_id != expected:
        raise ProtocolError("object id does not match canonical commitment")

    for field_name in ("reward_amount_bod", "bond_amount_bod"):
        if field_name in payload and (
            not isinstance(payload[field_name], int) or payload[field_name] <= 0
        ):
            raise ProtocolError("BOD amount must be a positive integer")
    for field_name in ("request_nonce", "candidate_nonce", "verifier_nonce", "deadline", "verification_epoch"):
        if field_name in payload and (
            not isinstance(payload[field_name], int) or payload[field_name] < 0
        ):
            raise ProtocolError("numeric protocol field is invalid")


@dataclass
class ProtocolState:
    current_state_root: str
    tasks: Dict[str, dict] = field(default_factory=dict)
    candidates: Dict[str, dict] = field(default_factory=dict)
    verifications: Dict[str, dict] = field(default_factory=dict)
    settlements: Dict[str, dict] = field(default_factory=dict)
    used_nonces: set[tuple[str, str, int]] = field(default_factory=set)


class BODProtocol:
    def __init__(self, initial_state_root: str, verifier: SignatureVerifier):
        if not isinstance(initial_state_root, str) or not initial_state_root:
            raise ProtocolError("initial state root is required")
        self.state = ProtocolState(initial_state_root)
        self._verifier = verifier

    @staticmethod
    def make_id(object_type: str, payload_without_id: Mapping[str, object], id_field: str) -> str:
        if id_field in payload_without_id:
            raise ProtocolError("payload_without_id already contains object id")
        return commitment(object_type, payload_without_id)

    def create_task(self, payload: Mapping[str, object], signature: str) -> str:
        _validate_envelope("task", payload, signature, self._verifier)
        task_id = str(payload["task_id"])
        nonce_key = ("requester", str(payload["requester"]), int(payload["request_nonce"]))
        if nonce_key in self.state.used_nonces:
            raise ProtocolError("replayed task nonce")
        if payload["parent_state_root"] != self.state.current_state_root:
            raise ProtocolError("task parent state is stale")
        if task_id in self.state.tasks:
            raise ProtocolError("duplicate task")
        self.state.used_nonces.add(nonce_key)
        self.state.tasks[task_id] = {**dict(payload), "signature": signature, "status": "OPEN"}
        return task_id

    def submit_candidate(self, payload: Mapping[str, object], signature: str) -> str:
        _validate_envelope("candidate", payload, signature, self._verifier)
        candidate_id = str(payload["candidate_id"])
        task_id = str(payload["task_id"])
        task = self.state.tasks.get(task_id)
        if task is None:
            raise ProtocolError("unknown task")
        if task["status"] != "OPEN":
            raise ProtocolError("task is not open")
        if payload["parent_state_root"] != task["parent_state_root"]:
            raise ProtocolError("candidate parent does not match task")
        nonce_key = ("candidate", str(payload["executor"]), int(payload["candidate_nonce"]))
        if nonce_key in self.state.used_nonces:
            raise ProtocolError("replayed candidate nonce")
        if candidate_id in self.state.candidates:
            raise ProtocolError("duplicate candidate")
        self.state.used_nonces.add(nonce_key)
        self.state.candidates[candidate_id] = {
            **dict(payload), "signature": signature, "status": "SUBMITTED"
        }
        return candidate_id

    def verify_candidate(self, payload: Mapping[str, object], signature: str) -> str:
        _validate_envelope("verification", payload, signature, self._verifier)
        verification_id = str(payload["verification_id"])
        candidate_id = str(payload["candidate_id"])
        candidate = self.state.candidates.get(candidate_id)
        if candidate is None:
            raise ProtocolError("unknown candidate")
        if candidate["status"] not in {"SUBMITTED", "SELECTED"}:
            raise ProtocolError("candidate is not verifiable")
        if payload["candidate_hash"] != candidate["candidate_id"]:
            raise ProtocolError("candidate commitment mismatch")
        if payload["evidence_root"] != candidate["evidence_root"]:
            raise ProtocolError("evidence root mismatch")
        task = self.state.tasks[str(candidate["task_id"])]
        if payload["acceptance_policy_hash"] != task["acceptance_policy_hash"]:
            raise ProtocolError("verification policy mismatch")
        if payload["verification_result"] not in VERIFY_RESULTS:
            raise ProtocolError("unknown verification result")
        nonce_key = ("verification", str(payload["verifier"]), int(payload["verifier_nonce"]))
        if nonce_key in self.state.used_nonces:
            raise ProtocolError("replayed verifier nonce")
        if verification_id in self.state.verifications:
            raise ProtocolError("duplicate verification")
        self.state.used_nonces.add(nonce_key)
        self.state.verifications[verification_id] = {
            **dict(payload), "signature": signature
        }
        return verification_id

    def settle(self, task_id: str, selected_candidate_id: Optional[str], verification_root: str,
               new_state_root: str, economic_outcome_hash: str, settlement_epoch: int) -> str:
        task = self.state.tasks.get(task_id)
        if task is None:
            raise ProtocolError("unknown task")
        if task["status"] != "OPEN":
            raise ProtocolError("task already settled")
        if task["parent_state_root"] != self.state.current_state_root:
            raise ProtocolError("settlement parent is stale")
        if selected_candidate_id is None:
            valid_candidates = []
        else:
            candidate = self.state.candidates.get(selected_candidate_id)
            if candidate is None or candidate["task_id"] != task_id:
                raise ProtocolError("selected candidate is unknown")
            valid_candidates = [
                v for v in self.state.verifications.values()
                if v["candidate_id"] == selected_candidate_id and v["verification_result"] == "VALID"
            ]
            if not valid_candidates:
                raise ProtocolError("selected candidate lacks valid verification")
            if candidate["parent_state_root"] != self.state.current_state_root:
                raise ProtocolError("selected candidate is stale")
            candidate["status"] = "SELECTED"
            for candidate_id, other in self.state.candidates.items():
                if candidate_id != selected_candidate_id and other["task_id"] == task_id:
                    other["status"] = "REJECTED"

        settlement_payload = {
            "task_id": task_id,
            "selected_candidate_id": selected_candidate_id,
            "verification_root": verification_root,
            "new_state_root": new_state_root,
            "economic_outcome_hash": economic_outcome_hash,
            "settlement_epoch": settlement_epoch,
        }
        settlement_id = commitment("settlement", settlement_payload)
        self.state.settlements[settlement_id] = settlement_payload
        task["status"] = "SETTLED"
        self.state.current_state_root = new_state_root
        return settlement_id


