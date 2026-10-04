from pathlib import Path
import yaml


ROOT = Path(__file__).parents[1]
POLICY = ROOT / "protocol" / "genesis" / "BOD_TOKEN_POLICY_v0.1.yml"
READINESS = ROOT / "protocol" / "TESTNET_READINESS_v0.1.yml"


def test_stage1_allocation_targets_match_candidate_configuration():
    doc = yaml.safe_load(POLICY.read_text(encoding="utf-8"))
    targets = doc["genesis"]["allocation_targets"]

    assert targets["developer_founder"] == {
        "total_amount": 100_000_000,
        "share_bps": 1_000,
    }
    assert targets["community"]["total_amount"] == 200_000_000
    assert targets["community"]["share_bps"] == 2_000
    assert targets["community"]["genesis_amount"] == 150_000_000
    assert targets["community"]["reserve_amount"] == 50_000_000
    assert (
        targets["community"]["genesis_amount"]
        + targets["community"]["reserve_amount"]
        == targets["community"]["total_amount"]
    )


def test_stage1_targets_are_distinct_from_genesis_mint():
    doc = yaml.safe_load(POLICY.read_text(encoding="utf-8"))
    genesis = doc["genesis"]
    targets = genesis["allocation_targets"]

    assert sum(v["amount"] for v in genesis["allocations"].values()) == genesis["minted_supply"]
    assert targets["community"]["total_amount"] > genesis["allocations"]["community"]["amount"]
    assert targets["community"]["reserve_amount"] == 50_000_000


def test_testnet_readiness_does_not_claim_native_bod_launch():
    doc = yaml.safe_load(READINESS.read_text(encoding="utf-8"))

    assert doc["network"]["chain_id"] == 421614
    assert doc["network"]["native_bod_network"] is False
    assert doc["network"]["production"] is False
    assert doc["launch_gate"]["decision"] == "blocked"
    assert "mainnet_deployment" in doc["launch_gate"]["prohibited_now"]
    assert doc["native_bod_network"]["status"] == "not_ready"
