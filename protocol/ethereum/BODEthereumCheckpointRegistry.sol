// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

/// @title BOD Ethereum Checkpoint Registry
/// @notice Permissionless, append-only publication of compact project-state commitments.
/// @dev External witness only; not a consensus engine or repository authorization system.
contract BODEthereumCheckpointRegistry {
    bytes32 public constant CHECKPOINT_DOMAIN = keccak256("BOD_ETHEREUM_CHECKPOINT_V1");

    struct CheckpointInput {
        bytes32 projectId;
        bytes32 gitCommit;
        bytes32 stateRoot;
        bytes32 manifestHash;
        bytes32 evidenceRoot;
        bytes32 previousCheckpointId;
        uint64 sequence;
    }

    struct Checkpoint {
        bytes32 projectId;
        bytes32 gitCommit;
        bytes32 stateRoot;
        bytes32 manifestHash;
        bytes32 evidenceRoot;
        bytes32 previousCheckpointId;
        uint64 sequence;
        uint64 anchoredAt;
        address publisher;
    }

    mapping(bytes32 checkpointId => Checkpoint checkpoint) private _checkpoints;
    mapping(bytes32 checkpointId => bool exists) public checkpointExists;

    error ZeroCommitment();
    error InvalidGenesis();
    error UnknownParent();
    error ParentProjectMismatch();
    error InvalidSequence();
    error DuplicateCheckpoint();
    error TimestampOverflow();

    event CheckpointAnchored(
        bytes32 indexed checkpointId,
        bytes32 indexed projectId,
        bytes32 indexed stateRoot,
        bytes32 gitCommit,
        bytes32 manifestHash,
        bytes32 evidenceRoot,
        bytes32 previousCheckpointId,
        uint64 sequence,
        uint64 anchoredAt,
        address publisher
    );

    /// @notice Publish a checkpoint. Any account may submit; publisher is recorded.
    /// @dev Forks are intentionally allowed and remain independently visible.
    function anchor(CheckpointInput calldata input) external returns (bytes32 checkpointId) {
        if (
            input.projectId == bytes32(0) ||
            input.gitCommit == bytes32(0) ||
            input.stateRoot == bytes32(0) ||
            input.manifestHash == bytes32(0) ||
            input.evidenceRoot == bytes32(0)
        ) revert ZeroCommitment();

        if (input.previousCheckpointId == bytes32(0)) {
            if (input.sequence != 0) revert InvalidGenesis();
        } else {
            if (!checkpointExists[input.previousCheckpointId]) revert UnknownParent();
            Checkpoint storage parent = _checkpoints[input.previousCheckpointId];
            if (parent.projectId != input.projectId) revert ParentProjectMismatch();
            if (
                parent.sequence == type(uint64).max ||
                input.sequence != parent.sequence + 1
            ) revert InvalidSequence();
        }

        checkpointId = keccak256(
            abi.encode(
                CHECKPOINT_DOMAIN,
                block.chainid,
                address(this),
                input.projectId,
                input.gitCommit,
                input.stateRoot,
                input.manifestHash,
                input.evidenceRoot,
                input.previousCheckpointId,
                input.sequence,
                msg.sender
            )
        );

        if (checkpointExists[checkpointId]) revert DuplicateCheckpoint();
        if (block.timestamp > type(uint64).max) revert TimestampOverflow();

        _checkpoints[checkpointId] = Checkpoint({
            projectId: input.projectId,
            gitCommit: input.gitCommit,
            stateRoot: input.stateRoot,
            manifestHash: input.manifestHash,
            evidenceRoot: input.evidenceRoot,
            previousCheckpointId: input.previousCheckpointId,
            sequence: input.sequence,
            anchoredAt: uint64(block.timestamp),
            publisher: msg.sender
        });
        checkpointExists[checkpointId] = true;

        emit CheckpointAnchored(
            checkpointId,
            input.projectId,
            input.stateRoot,
            input.gitCommit,
            input.manifestHash,
            input.evidenceRoot,
            input.previousCheckpointId,
            input.sequence,
            uint64(block.timestamp),
            msg.sender
        );
    }

    /// @notice Read a checkpoint by its content-derived identifier.
    function getCheckpoint(bytes32 checkpointId) external view returns (Checkpoint memory) {
        if (!checkpointExists[checkpointId]) revert UnknownParent();
        return _checkpoints[checkpointId];
    }
}
