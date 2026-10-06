from pathlib import Path
import json
import re


ROOT = Path(__file__).resolve().parents[1]
BRIDGE = ROOT / "tools/metamask/bridge.html"
ARTIFACTS = ROOT / "tools/metamask/artifacts"


def test_metamask_bridge_is_sepolia_only_and_uses_eip1193():
    text = BRIDGE.read_text(encoding="utf-8")
    assert "eth_requestAccounts" in text
    assert "wallet_switchEthereumChain" in text
    assert "421614n" in text
    assert "0x66eee" in text
    assert "sepolia-rollup.arbitrum.io/rpc" in text
    assert "Arbitrum One" not in text
    assert "privateKey" not in text
    assert "PRIVATE_KEY" not in text


def test_metamask_bridge_explicitly_selects_metamask_provider():
    text = BRIDGE.read_text(encoding="utf-8")
    assert "isMetaMask" in text
    assert "eip6963:announceProvider" in text
    assert "eip6963:requestProvider" in text
    assert "io.metamask" in text
    assert "autoconnect" in text


def test_metamask_bridge_contains_complete_transaction_sequence():
    text = BRIDGE.read_text(encoding="utf-8")
    labels = [
        "deploy disposable TestBODToken",
        "deploy BODProtocolAdapterV0_1",
        "approve adapter for 1250 BOD",
        "createTask",
        "submitCandidate",
        "commitVerificationRoot",
        "settle",
    ]
    run_section = text[text.index("async function run"): ]
    positions = [run_section.index(label) for label in labels]
    assert positions == sorted(positions)


def test_browser_artifacts_match_expected_contracts():
    adapter = json.loads((ARTIFACTS / "BODProtocolAdapterV0_1.json").read_text())
    token = json.loads((ARTIFACTS / "TestBODToken.json").read_text())
    assert adapter["contractName"] == "BODProtocolAdapterV0_1"
    assert token["contractName"] == "TestBODToken"
    assert adapter["bytecode"].startswith("0x")
    assert token["bytecode"].startswith("0x")
    assert len(bytes.fromhex(adapter["bytecode"][2:])) == 5061
    assert len(bytes.fromhex(token["bytecode"][2:])) == 1473


def test_browser_bridge_uses_artifacts_and_checks_onchain_conservation():
    text = BRIDGE.read_text(encoding="utf-8")
    assert "BODProtocolAdapterV0_1.json" in text
    assert "TestBODToken.json" in text
    assert "adapterBalance!==0n" in text
    assert "state-root mismatch" in text
    assert "E2E VERIFIED" in text
