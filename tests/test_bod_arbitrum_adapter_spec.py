from pathlib import Path

CONTRACT = Path("protocol/arbitrum/BODProtocolAdapterV0_1.sol")
SPEC = Path("protocol/arbitrum/ADAPTER_v0.1.md")
TEST_TOKEN = Path("protocol/arbitrum/TestBODToken.sol")
LIVE_RUNNER = Path("scripts/run_arbitrum_sepolia_integration.py")


def test_adapter_has_required_chain_objects():
    text = CONTRACT.read_text(encoding="utf-8")
    for name in ("Task", "Candidate", "Settlement", "currentStateRoot", "verificationRoots",
                 "bodToken", "settlementAuthority"):
        assert name in text


def test_adapter_has_required_events():
    text = CONTRACT.read_text(encoding="utf-8")
    for event in ("TaskCreated", "CandidateSubmitted", "EvidenceRootCommitted",
                  "VerificationRootCommitted", "SettlementExecuted"):
        assert "event " + event in text


def test_adapter_enforces_core_guards():
    text = CONTRACT.read_text(encoding="utf-8")
    for fragment in (
        "if (parentStateRoot != currentStateRoot) revert InvalidParent();",
        "if (parentStateRoot != task.parentStateRoot || parentStateRoot != currentStateRoot) revert InvalidParent();",
        "if (task.parentStateRoot != currentStateRoot) revert InvalidParent();",
        "if (verificationRoot == bytes32(0)) revert VerificationMissing();",
        "if (task.status != TaskStatus.OPEN) revert TaskNotOpen();",
        "currentStateRoot = newStateRoot;",
        "if (rewardPaid != task.rewardAmount || bondReturned + bondSlashed != bondAmount)",
    ):
        assert fragment in text


def test_adapter_keeps_large_protocol_data_off_chain():
    text = SPEC.read_text(encoding="utf-8")
    for phrase in ("prompts", "source trees", "raw Git history", "tool calls", "full evidence bundles"):
        assert phrase in text


def test_adapter_does_not_finalize_verifier_economics():
    text = SPEC.read_text(encoding="utf-8")
    for phrase in ("verifier quorum", "verifier staking", "final verifier rewards"):
        assert phrase in text


def test_sepolia_test_token_is_explicitly_non_production():
    text = TEST_TOKEN.read_text(encoding="utf-8")
    assert "Test-only ERC-20" in text
    assert "must not be used on mainnet" in text
    for fragment in ("balanceOf", "allowance", "approve", "transferFrom", "totalSupply"):
        assert fragment in text


def test_live_operator_credentials_are_not_part_of_the_public_contract_source():
    text = CONTRACT.read_text(encoding="utf-8")
    assert "private key" not in text.lower()
    assert "BOD_ARBITRUM_SEPOLIA_PRIVATE_KEY" not in text
