// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

/// @notice Minimal public anchor for BOD repository state checkpoints.
/// @dev Stores commitments only; GitHub content and internal project state remain off-chain.
contract BODGitCommitmentRegistryV0_1 {
    struct Anchor {
        bytes32 repositoryId;
        bytes32 gitCommit;
        bytes32 stateRoot;
        bytes32 manifestHash;
        uint64 timestamp;
        address submitter;
    }

    mapping(bytes32 => Anchor) public anchors;

    error AlreadyAnchored();
    error ZeroCommitment();

    event RepositoryAnchored(bytes32 indexed anchorId, bytes32 indexed repositoryId, bytes32 indexed gitCommit, bytes32 stateRoot, bytes32 manifestHash, uint64 timestamp, address submitter);

    function anchor(bytes32 anchorId, bytes32 repositoryId, bytes32 gitCommit, bytes32 stateRoot, bytes32 manifestHash) external {
        if (anchors[anchorId].timestamp != 0) revert AlreadyAnchored();
        if (repositoryId == bytes32(0) || gitCommit == bytes32(0) || stateRoot == bytes32(0) || manifestHash == bytes32(0)) revert ZeroCommitment();
        uint64 timestamp = uint64(block.timestamp);
        anchors[anchorId] = Anchor(repositoryId, gitCommit, stateRoot, manifestHash, timestamp, msg.sender);
        emit RepositoryAnchored(anchorId, repositoryId, gitCommit, stateRoot, manifestHash, timestamp, msg.sender);
    }
}