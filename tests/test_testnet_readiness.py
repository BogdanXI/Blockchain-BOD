from pathlib import Path
import yaml


ROOT = Path(__file__).parents[1]
POLICY = ROOT / "protocol" / "genesis" / "BOD_TOKEN_POLICY_v0.1.yml"
READINESS = ROOT / "protocol" / "TESTNET_READINESS_v0.1.yml"


def test_candidate_supply_and_founder_boundary_match_policy():
    doc = yaml.safe_load(POLICY.read_text(encoding="utf-8"))
    genesis = doc["genesis"]

    assert doc["token"]["max_supply"] == 100_000_000
    assert genesis["minted_supply"] == 25_000_000
    assert genesis["founder_preallocation"] == 5_000_000
    assert genesis["founder_preallocation_share_bps"] == 500
    assert genesis["initial_circulation_allocation"] == 20_000_000
    assert genesis["founder_preallocation"] + genesis["initial_circulation_allocation"] == genesis["minted_supply"]


def test_unissued_capacity_is_not_an_account_balance():
    doc = yaml.safe_load(POLICY.read_text(encoding="utf-8"))
    genesis = doc["genesis"]

    assert genesis["unissued_issuance_capacity"] == 75_000_000
    assert genesis["minted_supply"] + genesis["unissued_issuance_capacity"] == 100_000_000
    assert genesis["issuance_capacity_is_not_an_account_balance"] is True
    assert genesis["founder_preallocation"] == 5_000_000


def test_testnet_readiness_does_not_claim_native_bod_launch():
    doc = yaml.safe_load(READINESS.read_text(encoding="utf-8"))

    assert doc["network"]["chain_id"] == 421614
    assert doc["network"]["native_bod_network"] is False
    assert doc["network"]["production"] is False
    assert doc["launch_gate"]["decision"] == "blocked"
    assert "mainnet_deployment" in doc["launch_gate"]["prohibited_now"]
    assert doc["native_bod_network"]["status"] == "not_ready"
