from pathlib import Path
import yaml


ROOT = Path(__file__).parents[1]
POLICY = ROOT / "protocol" / "genesis" / "BOD_TOKEN_POLICY_v0.1.yml"
READINESS = ROOT / "protocol" / "TESTNET_READINESS_v0.1.yml"


def test_historical_token_policy_remains_an_unapproved_candidate():
    doc = yaml.safe_load(POLICY.read_text(encoding="utf-8"))
    assert doc["status"] == "candidate_not_final"
    assert doc["token"]["max_supply"] == 100_000_000
    assert doc["genesis"]["minted_supply"] == 25_000_000
    assert doc["genesis"]["founder_preallocation"] == 5_000_000
    assert doc["genesis"]["unissued_issuance_capacity"] == 75_000_000


def test_ethereum_is_the_primary_testnet_target_and_not_deployed():
    doc = yaml.safe_load(READINESS.read_text(encoding="utf-8"))
    assert doc["network"]["profile"] == "ethereum-sepolia-checkpoint-registry"
    assert doc["network"]["chain_id"] == 11155111
    assert doc["network"]["production"] is False
    assert doc["network_scope"]["policy"] == "ethereum_l1_only"
    assert doc["network_scope"]["l2_adapters"] == "out_of_scope"
    assert doc["surfaces"]["ethereum_sepolia_deployment"]["status"] == "not_deployed"
    assert doc["surfaces"]["eas_sdk_integration"]["status"] == "source_implemented_ci_syntax_checked_not_live_validated_schema_not_registered"
    assert doc["launch_gate"]["decision"] == "blocked"
    assert "ethereum_mainnet_deployment" in doc["launch_gate"]["prohibited_now"]
    assert doc["native_bod_network"]["status"] == "not_ready"
