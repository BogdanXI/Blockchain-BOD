// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import {BODEthereumCheckpointRegistry} from "../protocol/ethereum/BODEthereumCheckpointRegistry.sol";

contract BODEthereumCheckpointRegistryTest {
    BODEthereumCheckpointRegistry private registry;

    function setUp() public {
        registry = new BODEthereumCheckpointRegistry();
    }

    function _genesis(bytes32 projectId)
        private pure returns (BODEthereumCheckpointRegistry.CheckpointInput memory)
    {
        return BODEthereumCheckpointRegistry.CheckpointInput({
            projectId: projectId,
            gitCommit: keccak256("git-commit-0"),
            stateRoot: keccak256("state-root-0"),
            manifestHash: keccak256("manifest-0"),
            evidenceRoot: keccak256("evidence-0"),
            previousCheckpointId: bytes32(0),
            sequence: 0
        });
    }

    function testAnchorGenesisCheckpoint() public {
        bytes32 projectId = keccak256("project-A");
        bytes32 checkpointId = registry.anchor(_genesis(projectId));
        require(registry.checkpointExists(checkpointId), "checkpoint missing");
        BODEthereumCheckpointRegistry.Checkpoint memory checkpoint = registry.getCheckpoint(checkpointId);
        require(checkpoint.projectId == projectId, "wrong project");
        require(checkpoint.sequence == 0, "wrong genesis sequence");
        require(checkpoint.publisher == address(this), "wrong publisher");
        require(checkpoint.anchoredAt != 0, "timestamp missing");
    }

    function testRejectDuplicateCheckpoint() public {
        BODEthereumCheckpointRegistry.CheckpointInput memory input = _genesis(keccak256("project-A"));
        registry.anchor(input);
        (bool success,) = address(registry).call(
            abi.encodeCall(BODEthereumCheckpointRegistry.anchor, (input))
        );
        require(!success, "duplicate checkpoint accepted");
    }

    function testRejectUnknownParent() public {
        BODEthereumCheckpointRegistry.CheckpointInput memory input = _genesis(keccak256("project-A"));
        input.previousCheckpointId = keccak256("missing-parent");
        input.sequence = 1;
        (bool success,) = address(registry).call(
            abi.encodeCall(BODEthereumCheckpointRegistry.anchor, (input))
        );
        require(!success, "unknown parent accepted");
    }

    function testRejectParentFromAnotherProject() public {
        bytes32 parentId = registry.anchor(_genesis(keccak256("project-A")));
        BODEthereumCheckpointRegistry.CheckpointInput memory child = _genesis(keccak256("project-B"));
        child.previousCheckpointId = parentId;
        child.sequence = 1;
        (bool success,) = address(registry).call(
            abi.encodeCall(BODEthereumCheckpointRegistry.anchor, (child))
        );
        require(!success, "cross-project parent accepted");
    }

    function testRejectWrongSequence() public {
        bytes32 parentId = registry.anchor(_genesis(keccak256("project-A")));
        BODEthereumCheckpointRegistry.CheckpointInput memory child = _genesis(keccak256("project-A"));
        child.previousCheckpointId = parentId;
        child.sequence = 2;
        (bool success,) = address(registry).call(
            abi.encodeCall(BODEthereumCheckpointRegistry.anchor, (child))
        );
        require(!success, "incorrect sequence accepted");
    }

    function testAllowsForksWithoutChoosingCanonicalHead() public {
        bytes32 projectId = keccak256("project-A");
        bytes32 parentId = registry.anchor(_genesis(projectId));
        BODEthereumCheckpointRegistry.CheckpointInput memory left = _genesis(projectId);
        left.gitCommit = keccak256("left-commit");
        left.stateRoot = keccak256("left-state");
        left.previousCheckpointId = parentId;
        left.sequence = 1;
        BODEthereumCheckpointRegistry.CheckpointInput memory right = left;
        right.gitCommit = keccak256("right-commit");
        right.stateRoot = keccak256("right-state");
        bytes32 leftId = registry.anchor(left);
        bytes32 rightId = registry.anchor(right);
        require(leftId != rightId, "fork identifiers collided");
        require(registry.checkpointExists(leftId), "left branch missing");
        require(registry.checkpointExists(rightId), "right branch missing");
        require(registry.getCheckpoint(leftId).previousCheckpointId == parentId, "left parent mismatch");
        require(registry.getCheckpoint(rightId).previousCheckpointId == parentId, "right parent mismatch");
    }

    function testRejectZeroCommitment() public {
        BODEthereumCheckpointRegistry.CheckpointInput memory input = _genesis(keccak256("project-A"));
        input.evidenceRoot = bytes32(0);
        (bool success,) = address(registry).call(
            abi.encodeCall(BODEthereumCheckpointRegistry.anchor, (input))
        );
        require(!success, "zero evidence root accepted");
    }
}
