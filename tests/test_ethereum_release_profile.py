import json
import subprocess
import sys
from pathlib import Path

import pytest

from bod_ethereum_release_profile import ReleaseProfileError, validate_release_profile


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "examples/ethereum-release-profile/reth-v2.11.0.json"
SCHEMA = ROOT / "schemas/bod-ethereum-release-profile-v0.1.schema.json"


def _local_refs(value):
    if isinstance(value, dict):
        if "$ref" in value:
            yield value["$ref"]
        for child in value.values():
            yield from _local_refs(child)
    elif isinstance(value, list):
        for child in value:
            yield from _local_refs(child)


def load_fixture() -> dict:
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def test_reth_public_release_profile_fixture_is_structurally_valid() -> None:
    result = validate_release_profile(load_fixture())
    assert result == {
        "status": "VALID_PROFILE_STRUCTURE",
        "profile": "bod-ethereum-release-profile-v0.1",
        "project_id": "reth",
        "release_id": "v2.11.0",
        "release_kind": "software-release",
        "evidence_items": 1,
        "declared_gaps": 3,
        "deployment_present": False,
        "cryptographic_verification": "NOT_PERFORMED",
        "chain_state_verification": "NOT_PERFORMED",
        "semantic_truth": "NOT_ASSERTED",
    }


def test_profile_json_schema_is_valid_json_and_has_draft_2020_12() -> None:
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    assert schema["$schema"] == "https://json-schema.org/draft/2020-12/schema"
    assert schema["properties"]["release"]["$ref"] == "#/$defs/release"
    assert "contractBuild" in schema["$defs"]
    assert "finality" in schema["$defs"]["deployment"]["required"]
    assert "match_type" in schema["$defs"]["deployment"]["properties"]["source_verification"]["oneOf"][1]["required"]
    for name, definition in schema["$defs"].items():
        for ref in _local_refs(definition):
            assert ref.startswith("#/$defs/") and ref[8:] in schema["$defs"], (name, ref)


@pytest.mark.parametrize(
    ("mutate", "message"),
    [
        (lambda d: d.update(profile="unknown"), "unsupported Ethereum release profile"),
        (lambda d: d["release"].update(source_commit="main"), "full lowercase Git commit ID"),
        (lambda d: d["evidence"][0].update(digest="not-a-digest"), "lowercase SHA-256"),
        (lambda d: d["project"].update(repository="github.com/paradigmxyz/reth"), "absolute URI"),
        (lambda d: d.update(unexpected=True), "unknown fields"),
    ],
)
def test_invalid_profile_fields_are_rejected(mutate, message: str) -> None:
    profile = load_fixture()
    mutate(profile)
    with pytest.raises(ReleaseProfileError, match=message):
        validate_release_profile(profile)


def test_contract_deployment_requires_compiler_and_deployment_evidence() -> None:
    profile = load_fixture()
    profile["project"]["kind"] = "smart-contract"
    profile["release"]["kind"] = "contract-deployment"
    with pytest.raises(ReleaseProfileError, match="requires compiler build evidence"):
        validate_release_profile(profile)


def test_contract_deployment_rejects_wrong_address_width() -> None:
    profile = load_fixture()
    profile["project"]["kind"] = "smart-contract"
    profile["release"]["kind"] = "contract-deployment"
    digest = "a" * 64
    profile["build"] = {
        "builder_id": "https://example.org/build",
        "provenance_digest": digest,
        "compiler": {
            "name": "solc",
            "version": "0.8.30",
            "settings_digest": digest,
            "input_digest": digest,
            "bytecode_digest": digest,
            "abi_digest": digest,
        },
    }
    profile["deployment"] = {
        "chain_id": 1,
        "transaction_hash": "0x" + "b" * 64,
        "block_hash": "0x" + "c" * 64,
        "block_number": 1,
        "contract_address": "0x" + "d" * 39,
        "runtime_bytecode_digest": digest,
        "finality": {"status": "NOT_CHECKED", "observed_at": None, "source": None},
    }
    with pytest.raises(ReleaseProfileError, match="20-byte 0x address"):
        validate_release_profile(profile)


def test_predecessor_cannot_reference_same_release_id() -> None:
    profile = load_fixture()
    profile["predecessor"] = {"release_id": "v2.11.0", "checkpoint_id": "a" * 64}
    with pytest.raises(ReleaseProfileError, match="cannot name itself"):
        validate_release_profile(profile)


def test_profile_validate_cli_reports_structure_without_claiming_crypto_verification() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "bod_cli", "profile-validate", str(FIXTURE)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    output = json.loads(result.stdout)
    assert output["status"] == "VALID_PROFILE_STRUCTURE"
    assert output["cryptographic_verification"] == "NOT_PERFORMED"


def test_valid_evidence_status_requires_a_verification_method() -> None:
    profile = load_fixture()
    profile["evidence"][0].pop("verification_method")
    with pytest.raises(ReleaseProfileError, match="verification_method is required"):
        validate_release_profile(profile)


def test_non_string_enumeration_values_are_rejected_cleanly() -> None:
    profile = load_fixture()
    profile["project"]["kind"] = []
    with pytest.raises(ReleaseProfileError, match="project.kind is unsupported"):
        validate_release_profile(profile)


def test_valid_contract_deployment_profile_is_accepted() -> None:
    profile = load_fixture()
    profile["project"]["id"] = "example-contract"
    profile["project"]["kind"] = "smart-contract"
    profile["project"]["repository"] = "https://github.com/example/contract"
    profile["release"].update(id="v1", kind="contract-deployment")
    digest = "a" * 64
    profile["build"] = {
        "builder_id": "https://github.com/example/contract/.github/workflows/release.yml",
        "provenance_digest": digest,
        "compiler": {
            "name": "solc",
            "version": "0.8.30",
            "settings_digest": digest,
            "input_digest": digest,
            "bytecode_digest": digest,
            "abi_digest": digest,
        },
    }
    profile["deployment"] = {
        "chain_id": 1,
        "transaction_hash": "0x" + "b" * 64,
        "block_hash": "0x" + "c" * 64,
        "block_number": 123,
        "contract_address": "0x" + "d" * 40,
        "runtime_bytecode_digest": digest,
        "finality": {"status": "FINALIZED", "observed_at": "2026-11-22T12:00:00Z", "source": "https://ethereum.org/developers/docs/nodes-and-clients/"},
        "source_verification": {
            "provider": "Sourcify",
            "reference": "https://repo.sourcify.dev/contracts/full_match/1/0x" + "d" * 40 + "/",
            "match_type": "exact_match",
        },
    }
    result = validate_release_profile(profile)
    assert result["status"] == "VALID_PROFILE_STRUCTURE"
    assert result["deployment_present"] is True


def test_contract_profile_rejects_unknown_sourcify_match_classification() -> None:
    profile = load_fixture()
    profile["project"]["kind"] = "smart-contract"
    profile["release"]["kind"] = "contract-deployment"
    digest = "a" * 64
    profile["build"] = {
        "builder_id": "https://example.org/build", "provenance_digest": digest,
        "compiler": {"name": "solc", "version": "0.8.30", "settings_digest": digest, "input_digest": digest, "bytecode_digest": digest, "abi_digest": digest},
    }
    profile["deployment"] = {
        "chain_id": 1, "transaction_hash": "0x" + "b" * 64, "block_hash": "0x" + "c" * 64,
        "block_number": 1, "contract_address": "0x" + "d" * 40, "runtime_bytecode_digest": digest,
        "finality": {"status": "NOT_CHECKED", "observed_at": None, "source": None},
        "source_verification": {"provider": "Sourcify", "reference": "https://repo.sourcify.dev/", "match_type": []},
    }
    with pytest.raises(ReleaseProfileError, match="match_type is unsupported"):
        validate_release_profile(profile)


def test_contract_deployment_requires_explicit_finality_observation() -> None:
    profile = load_fixture()
    profile["project"]["kind"] = "smart-contract"
    profile["release"]["kind"] = "contract-deployment"
    digest = "a" * 64
    profile["build"] = {
        "builder_id": "https://example.org/build", "provenance_digest": digest,
        "compiler": {"name": "solc", "version": "0.8.30", "settings_digest": digest, "input_digest": digest, "bytecode_digest": digest, "abi_digest": digest},
    }
    profile["deployment"] = {
        "chain_id": 1, "transaction_hash": "0x" + "b" * 64, "block_hash": "0x" + "c" * 64,
        "block_number": 1, "contract_address": "0x" + "d" * 40, "runtime_bytecode_digest": digest,
        "finality": {"status": "FINALIZED", "observed_at": "2026-11-22T12:00:00", "source": "https://example.org/rpc"},
    }
    with pytest.raises(ReleaseProfileError, match="must include a timezone"):
        validate_release_profile(profile)


def test_weth9_public_contract_fixture_preserves_unavailable_evidence_as_gaps() -> None:
    path = ROOT / "examples/ethereum-release-profile/weth9-mainnet-2017-12-12.json"
    profile = json.loads(path.read_text(encoding="utf-8"))
    result = validate_release_profile(profile)
    assert result["status"] == "VALID_PROFILE_STRUCTURE"
    assert result["release_kind"] == "contract-deployment"
    assert result["deployment_present"] is True
    assert result["declared_gaps"] == 12
    assert profile["deployment"]["source_verification"]["provider"] == "Sourcify"
    assert profile["deployment"]["source_verification"]["match_type"] is None
    assert any(g["type"] == "sourcify-match-classification" for g in profile["gaps"])
    assert profile["deployment"]["runtime_bytecode_digest"] is None


def test_unknown_profile_fields_require_matching_explicit_gap_records() -> None:
    path = ROOT / "examples/ethereum-release-profile/weth9-mainnet-2017-12-12.json"
    profile = json.loads(path.read_text(encoding="utf-8"))
    profile["gaps"] = [g for g in profile["gaps"] if g["type"] != "compiler-input"]
    with pytest.raises(ReleaseProfileError, match="missing explicit gap records"):
        validate_release_profile(profile)


def test_missing_sourcify_classification_requires_an_explicit_gap() -> None:
    path = ROOT / "examples/ethereum-release-profile/weth9-mainnet-2017-12-12.json"
    profile = json.loads(path.read_text(encoding="utf-8"))
    profile["gaps"] = [g for g in profile["gaps"] if g["type"] != "sourcify-match-classification"]
    with pytest.raises(ReleaseProfileError, match="missing explicit gap records"):
        validate_release_profile(profile)
