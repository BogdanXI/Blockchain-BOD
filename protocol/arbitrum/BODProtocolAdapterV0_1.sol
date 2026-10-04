// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

interface IERC20Like {
    function transfer(address to, uint256 amount) external returns (bool);
    function transferFrom(address from, address to, uint256 amount) external returns (bool);
}

/// @notice Minimal EVM adapter for BOD Protocol v0.1.
/// Project/evidence payloads remain off-chain; only protocol commitments and locked
/// BOD accounting are represented here. Consensus/arbitration is injected through
/// settlementAuthority and is not defined by this adapter.
contract BODProtocolAdapterV0_1 {
    enum TaskStatus { OPEN, SETTLED }
    enum CandidateStatus { SUBMITTED, SELECTED, REJECTED }

    struct Task {
        address requester;
        bytes32 parentStateRoot;
        bytes32 taskSpecHash;
        bytes32 acceptancePolicyHash;
        uint256 rewardAmount;
        uint256 deadline;
        TaskStatus status;
    }

    struct Candidate {
        address executor;
        bytes32 taskId;
        bytes32 parentStateRoot;
        bytes32 candidateStateRoot;
        bytes32 resultArtifactHash;
        bytes32 executionManifestHash;
        bytes32 evidenceRoot;
        uint256 bondAmount;
        CandidateStatus status;
    }

    struct Settlement {
        bytes32 taskId;
        bytes32 selectedCandidateId;
        bytes32 parentStateRoot;
        bytes32 candidateStateRoot;
        bytes32 evidenceRoot;
        bytes32 verificationRoot;
        bytes32 settlementPolicyHash;
        bytes32 economicOutcomeHash;
        bytes32 newStateRoot;
        uint256 settlementEpoch;
    }

    IERC20Like public immutable bodToken;
    address public immutable settlementAuthority;
    bytes32 public currentStateRoot;

    mapping(bytes32 => Task) public tasks;
    mapping(bytes32 => Candidate) public candidates;
    mapping(bytes32 => bytes32) public verificationRoots;
    mapping(bytes32 => Settlement) public settlements;

    error AlreadyExists();
    error UnknownTask();
    error UnknownCandidate();
    error InvalidParent();
    error InvalidAmount();
    error InvalidDeadline();
    error TaskNotOpen();
    error CandidateNotSubmitted();
    error VerificationMissing();
    error UnauthorizedSettlement();
    error InvalidStateRoot();
    error EconomicOutcomeMismatch();
    error TokenTransferFailed();

    event TaskCreated(bytes32 indexed taskId, address indexed requester, bytes32 indexed parentStateRoot,
        uint256 rewardAmount, uint256 deadline, bytes32 taskSpecHash, bytes32 acceptancePolicyHash);
    event CandidateSubmitted(bytes32 indexed candidateId, bytes32 indexed taskId, address indexed executor,
        bytes32 parentStateRoot, bytes32 candidateStateRoot, bytes32 evidenceRoot, uint256 bondAmount);
    event EvidenceRootCommitted(bytes32 indexed candidateId, bytes32 indexed evidenceRoot);
    event VerificationRootCommitted(bytes32 indexed candidateId, bytes32 indexed verificationRoot);
    event SettlementExecuted(bytes32 indexed settlementId, bytes32 indexed taskId, bytes32 indexed selectedCandidateId,
        bytes32 parentStateRoot, bytes32 candidateStateRoot, bytes32 evidenceRoot, bytes32 verificationRoot,
        bytes32 newStateRoot, bytes32 economicOutcomeHash, uint256 rewardPaid, uint256 bondReturned, uint256 bondSlashed);

    constructor(IERC20Like token, address authority, bytes32 initialStateRoot) {
        if (address(token) == address(0) || authority == address(0) || initialStateRoot == bytes32(0)) {
            revert InvalidStateRoot();
        }
        bodToken = token;
        settlementAuthority = authority;
        currentStateRoot = initialStateRoot;
    }

    function createTask(bytes32 taskId, bytes32 parentStateRoot, bytes32 taskSpecHash,
        bytes32 acceptancePolicyHash, uint256 rewardAmount, uint256 deadline) external {
        if (tasks[taskId].requester != address(0)) revert AlreadyExists();
        if (parentStateRoot != currentStateRoot) revert InvalidParent();
        if (rewardAmount == 0) revert InvalidAmount();
        if (deadline <= block.timestamp) revert InvalidDeadline();

        _pull(msg.sender, rewardAmount);
        tasks[taskId] = Task(msg.sender, parentStateRoot, taskSpecHash, acceptancePolicyHash,
            rewardAmount, deadline, TaskStatus.OPEN);
        emit TaskCreated(taskId, msg.sender, parentStateRoot, rewardAmount, deadline, taskSpecHash, acceptancePolicyHash);
    }

    function submitCandidate(bytes32 candidateId, bytes32 taskId, bytes32 parentStateRoot,
        bytes32 candidateStateRoot, bytes32 resultArtifactHash, bytes32 executionManifestHash,
        bytes32 evidenceRoot, uint256 bondAmount) external {
        Task storage task = tasks[taskId];
        if (task.requester == address(0)) revert UnknownTask();
        if (task.status != TaskStatus.OPEN) revert TaskNotOpen();
        if (block.timestamp > task.deadline) revert InvalidDeadline();
        if (parentStateRoot != task.parentStateRoot || parentStateRoot != currentStateRoot) revert InvalidParent();
        if (candidateStateRoot == bytes32(0) || evidenceRoot == bytes32(0)) revert InvalidStateRoot();
        if (bondAmount == 0) revert InvalidAmount();
        if (candidates[candidateId].executor != address(0)) revert AlreadyExists();

        _pull(msg.sender, bondAmount);
        candidates[candidateId] = Candidate(msg.sender, taskId, parentStateRoot, candidateStateRoot,
            resultArtifactHash, executionManifestHash, evidenceRoot, bondAmount, CandidateStatus.SUBMITTED);
        emit CandidateSubmitted(candidateId, taskId, msg.sender, parentStateRoot, candidateStateRoot, evidenceRoot, bondAmount);
        emit EvidenceRootCommitted(candidateId, evidenceRoot);
    }

    /// @notice Records a verification commitment; validity and verifier economics remain off-chain policy.
    function commitVerificationRoot(bytes32 candidateId, bytes32 verificationRoot) external {
        Candidate storage candidate = candidates[candidateId];
        if (candidate.executor == address(0)) revert UnknownCandidate();
        if (candidate.status != CandidateStatus.SUBMITTED) revert CandidateNotSubmitted();
        if (verificationRoot == bytes32(0)) revert InvalidStateRoot();
        verificationRoots[candidateId] = verificationRoot;
        emit VerificationRootCommitted(candidateId, verificationRoot);
    }

    /// @notice Applies an authorized settlement and conserves locked reward/bond balances.
    /// settlementAuthority is the explicit arbitration/consensus adapter boundary.
    function settle(bytes32 settlementId, bytes32 taskId, bytes32 selectedCandidateId,
        bytes32 settlementPolicyHash, bytes32 economicOutcomeHash, bytes32 newStateRoot,
        uint256 settlementEpoch, uint256 rewardPaid, uint256 bondReturned, uint256 bondSlashed,
        address rewardRecipient, address bondReturnRecipient, address bondSlashRecipient) external {
        if (msg.sender != settlementAuthority) revert UnauthorizedSettlement();
        if (settlements[settlementId].taskId != bytes32(0)) revert AlreadyExists();
        if (newStateRoot == bytes32(0)) revert InvalidStateRoot();

        Task storage task = tasks[taskId];
        if (task.requester == address(0)) revert UnknownTask();
        if (task.status != TaskStatus.OPEN) revert TaskNotOpen();
        if (task.parentStateRoot != currentStateRoot) revert InvalidParent();

        bytes32 candidateStateRoot;
        bytes32 evidenceRoot;
        bytes32 verificationRoot;
        uint256 bondAmount;

        if (selectedCandidateId == bytes32(0)) {
            if (rewardPaid != task.rewardAmount || bondReturned != 0 || bondSlashed != 0 ||
                rewardRecipient != task.requester) revert EconomicOutcomeMismatch();
        } else {
            Candidate storage selected = candidates[selectedCandidateId];
            if (selected.executor == address(0) || selected.taskId != taskId) revert UnknownCandidate();
            if (selected.status != CandidateStatus.SUBMITTED) revert CandidateNotSubmitted();
            if (selected.parentStateRoot != currentStateRoot) revert InvalidParent();
            verificationRoot = verificationRoots[selectedCandidateId];
            if (verificationRoot == bytes32(0)) revert VerificationMissing();

            bondAmount = selected.bondAmount;
            if (rewardPaid != task.rewardAmount || bondReturned + bondSlashed != bondAmount) {
                revert EconomicOutcomeMismatch();
            }
            if (rewardPaid != 0 && rewardRecipient == address(0)) revert EconomicOutcomeMismatch();
            if (bondReturned != 0 && bondReturnRecipient == address(0)) revert EconomicOutcomeMismatch();
            if (bondSlashed != 0 && bondSlashRecipient == address(0)) revert EconomicOutcomeMismatch();

            selected.status = CandidateStatus.SELECTED;
            candidateStateRoot = selected.candidateStateRoot;
            evidenceRoot = selected.evidenceRoot;
        }

        task.status = TaskStatus.SETTLED;
        currentStateRoot = newStateRoot;
        settlements[settlementId] = Settlement(taskId, selectedCandidateId, task.parentStateRoot,
            candidateStateRoot, evidenceRoot, verificationRoot, settlementPolicyHash, economicOutcomeHash,
            newStateRoot, settlementEpoch);

        if (rewardPaid != 0) _push(rewardRecipient, rewardPaid);
        if (bondReturned != 0) _push(bondReturnRecipient, bondReturned);
        if (bondSlashed != 0) _push(bondSlashRecipient, bondSlashed);

        emit SettlementExecuted(settlementId, taskId, selectedCandidateId, task.parentStateRoot,
            candidateStateRoot, evidenceRoot, verificationRoot, newStateRoot, economicOutcomeHash,
            rewardPaid, bondReturned, bondSlashed);
    }

    function _pull(address from, uint256 amount) internal {
        if (!bodToken.transferFrom(from, address(this), amount)) revert TokenTransferFailed();
    }

    function _push(address to, uint256 amount) internal {
        if (!bodToken.transfer(to, amount)) revert TokenTransferFailed();
    }
}
