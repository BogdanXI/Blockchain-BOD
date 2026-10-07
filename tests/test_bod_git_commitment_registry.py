from pathlib import Path

CONTRACT = Path("protocol/arbitrum/BODGitCommitmentRegistryV0_1.sol")


def test_registry_is_commitment_only():
    source = CONTRACT.read_text(encoding="utf-8")
    assert "mapping(bytes32 => Anchor) public anchors" in source
    assert "event RepositoryAnchored" in source
    for field in ("bytes32 repositoryId", "bytes32 gitCommit", "bytes32 stateRoot", "bytes32 manifestHash"):
        assert field in source


def test_registry_rejects_duplicate_and_zero_anchors():
    source = CONTRACT.read_text(encoding="utf-8")
    assert "error AlreadyAnchored();" in source
    assert "error ZeroCommitment();" in source
    assert "if (anchors[anchorId].timestamp != 0) revert AlreadyAnchored();" in source
    assert "repositoryId == bytes32(0)" in source