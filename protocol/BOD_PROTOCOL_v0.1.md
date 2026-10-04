# BOD Protocol v0.1 — Task-to-Settlement Specification

Status: proposed protocol interface baseline

## 1. Purpose

BOD Protocol v0.1 defines the minimum verifiable work lifecycle:

    Task -> Candidate -> Evidence -> Verification -> Settlement

The protocol separates:

- work execution from canonical state selection;
- evidence storage from on-chain commitments;
- signatures from consensus;
- BOD economic accountability from execution identity.

This specification is an application protocol. It does not claim a new consensus mechanism.

## 2. Core objects

All protocol objects have:

- `protocol_version`;
- `object_type`;
- `object_id`;
- `created_at` / protocol epoch where applicable;
- domain-separated canonical encoding;
- a cryptographic digest;
- an author/executor identity where applicable.

Object IDs are hashes of the canonical signed envelope. Mutable metadata is forbidden after an object is committed.

### 2.1 Task

A Task is a request to produce a state transition or other protocol-defined software result.

Required signed fields:

- `task_id`;
- `project_id`;
- `parent_state_root`;
- `task_spec_hash` — hash of the complete task specification stored off-chain;
- `acceptance_policy_hash` — hash of the exact verification policy;
- `reward_amount_bod`;
- `deadline`;
- `requester`;
- `request_nonce`.

The requester signs:

    Sign("BOD/TASK/v0.1", canonical(TaskEnvelope))

The task reward is escrowed in BOD before the task can enter the executable state.

The task specification itself is not stored on-chain.

### 2.2 Candidate

A Candidate is one proposed result for exactly one Task.

Required signed fields:

- `candidate_id`;
- `task_id`;
- `parent_state_root`;
- `candidate_state_root`;
- `result_artifact_hash`;
- `execution_manifest_hash`;
- `evidence_root`;
- `executor`;
- `candidate_nonce`;
- `bond_amount_bod`.

The executor signs:

    Sign("BOD/CANDIDATE/v0.1", canonical(CandidateEnvelope))

A Candidate cannot modify canonical state.

The candidate bond is locked in BOD when the candidate is submitted. Bond semantics are inherited from the economic state machine and remain subject to calibration.

### 2.3 Evidence

Evidence is an off-chain, content-addressed bundle proving how a Candidate was produced and verified.

The bundle may contain:

- source/artifact references;
- Git commit or content-address identifiers;
- build/execution manifest;
- test results;
- logs;
- environment description;
- tool/agent version;
- reproducibility inputs;
- verifier-produced reports;
- optional dispute material.

The chain stores only:

- `evidence_root`;
- evidence bundle content identifier;
- policy hash;
- candidate hash;
- optional aggregate/Merkle commitments.

Individual evidence items are hashed and arranged under the `evidence_root`. Large files and logs remain off-chain.

Evidence does not become authoritative merely because it exists.

### 2.4 Verification

A Verification is a signed statement that a specific Candidate was evaluated under a specific policy.

Required signed fields:

- `verification_id`;
- `candidate_id`;
- `candidate_hash`;
- `evidence_root`;
- `acceptance_policy_hash`;
- `verification_result`;
- `verifier`;
- `verification_epoch`;
- `verifier_nonce`;
- `report_hash`.

The verifier signs:

    Sign("BOD/VERIFICATION/v0.1", canonical(VerificationEnvelope))

Allowed result values in v0.1:

- `VALID`;
- `INVALID`;
- `INCONCLUSIVE`.

A Verification is not a vote for canonicality. It is evidence about validity.

A verifier does not need to publish the full report on-chain; the report is referenced by `report_hash`.

The economic requirement for verifier bonds/rewards is intentionally not finalized by this protocol document. It is a parameter of the economic calibration work.

### 2.5 Settlement

Settlement is the canonical outcome for a Task after verification and arbitration.

Required fields:

- `settlement_id`;
- `task_id`;
- `parent_state_root`;
- `selected_candidate_id` or explicit `NO_ACCEPTED_CANDIDATE`;
- `candidate_state_root` when a candidate is selected;
- `evidence_root`;
- `verification_root`;
- `settlement_policy_hash`;
- `economic_outcome_hash`;
- `new_state_root`;
- `settlement_epoch`.

Settlement is authoritative only when included in the canonical chain state by the active consensus/arbitration mechanism.

No application agent signature alone can create canonical Settlement.

## 3. What is signed

The signed object is always the complete canonical envelope, not a human-readable summary.

Domain separation is mandatory:

- `BOD/TASK/v0.1`
- `BOD/CANDIDATE/v0.1`
- `BOD/VERIFICATION/v0.1`
- `BOD/SETTLEMENT/v0.1` where an external settlement signature is used by an adapter.

The canonical encoding must:

- define field order;
- define integer representation;
- define byte/string encoding;
- reject duplicate fields;
- reject unknown fields unless the protocol version explicitly permits them;
- hash referenced content rather than embedding unbounded content;
- include protocol version and object type in the domain separator.

A signature authenticates a commitment. It does not authenticate the referenced off-chain bytes unless their content hash is included in the signed envelope.

## 4. Off-chain / on-chain boundary

### Off-chain

Keep off-chain:

- prompts and model context;
- raw source files;
- full Git history;
- individual file edits;
- tool calls;
- agent reasoning;
- compiler/test logs;
- large artifacts;
- complete evidence bundles;
- verifier reports;
- intermediate candidates that never enter protocol state.

These objects are content-addressed and committed by hashes/Merkle roots.

### On-chain

Record only protocol-significant commitments and economic state:

- Task creation and reward escrow;
- Candidate commitment and BOD bond;
- Evidence root;
- Verification commitments or an aggregate verification root;
- disputes/arbitration outcomes when enabled;
- Settlement;
- selected candidate;
- state-root transition;
- BOD accounting changes.

The chain must never require storing the complete software project to validate the protocol state transition.

## 5. Minimal on-chain state

A v0.1 implementation can represent a task lifecycle with:

    TaskRecord {
        task_id
        project_id
        parent_state_root
        task_spec_hash
        acceptance_policy_hash
        reward_escrow_bod
        deadline
        status
    }

    CandidateRecord {
        candidate_id
        task_id
        candidate_state_root
        result_artifact_hash
        execution_manifest_hash
        evidence_root
        executor
        bond_bod
        status
    }

    VerificationCommitment {
        candidate_id
        verification_hash
        verifier
        result
        evidence_root
    }

    SettlementRecord {
        task_id
        selected_candidate_id
        verification_root
        new_state_root
        economic_outcome_hash
        status
    }

Large collections of Verification objects can be committed as a Merkle root rather than stored individually, provided the protocol can prove inclusion when needed.

## 6. BOD utility boundary

BOD is required for economic actions that create protocol accountability:

1. Task reward escrow.
2. Candidate bond.
3. Settlement-defined rewards, refunds and penalties.
4. Dispute stake if a dispute mechanism is activated.

BOD is not required merely to:

- read a task;
- execute code;
- create off-chain evidence;
- produce a cryptographic signature;
- download a project;
- run tests locally.

Verifier staking/reward mechanics remain a calibration question and must not be invented here as a final economic rule.

Gas for an initial Arbitrum deployment is a separate execution-layer concern. BOD utility does not imply that BOD is the gas token.

## 7. State machine

The minimal lifecycle is:

    OPEN
      |
      +--> CANDIDATE_SUBMITTED
      |       |
      |       +--> VERIFIED_VALID ----+
      |       |                        |
      |       +--> VERIFIED_INVALID   |
      |                                v
      +--------------------------> SETTLED
      |
      +--> EXPIRED

For multiple valid candidates:

    Task(parent=S)
       |
       +--> C1(valid)
       +--> C2(valid)
       +--> C3(invalid)
              |
              v
        Arbitration/consensus
              |
              v
        selected C1 or C2
              |
              v
          Settlement

Validity never implies canonicality.

## 8. Deterministic validity predicate

For Candidate C:

    VALID(C, S) =
        task_exists
        AND C.task_id == task.id
        AND C.parent_state_root == S
        AND task_policy_is_valid
        AND candidate_commitment_is_valid
        AND evidence_commitment_is_valid
        AND required_verification_rule_is_satisfied
        AND bond_accounting_is_valid
        AND replay_protection_is_satisfied

Settlement additionally requires:

    selected_candidate_is_valid
    AND selected_candidate.parent_state_root == current_state_root
    AND settlement_policy_is_valid
    AND economic_transition_is_conservative

The exact verification threshold and arbitration rule are intentionally adapter-defined in v0.1.

## 9. Failure and adversarial rules

A conforming implementation must reject:

- wrong parent state root;
- candidate for an unknown Task;
- candidate submitted after deadline;
- duplicate nonce/object identity;
- signature over a non-canonical envelope;
- evidence-root mismatch;
- verification for a different candidate/policy;
- settlement selecting an invalid candidate;
- settlement against a stale parent;
- economic transition that violates accounting invariants;
- replayed settlement;
- malformed or ambiguous canonical encoding.

The protocol must tolerate multiple independently valid Candidates. Their existence is not itself a protocol fault.

## 10. Arbitrum adapter boundary

The protocol core remains chain-neutral.

An initial Arbitrum adapter may implement the on-chain commitments as smart-contract state:

    Task -> Candidate -> EvidenceRoot -> VerificationRoot -> Settlement

The adapter must not move raw project data or full evidence bundles onto the chain.

The adapter must expose deterministic events or queryable state sufficient to reconstruct:

- Task identity;
- Candidate identity;
- evidence commitment;
- verification commitment;
- settlement;
- BOD accounting outcome.

A future native BOD chain can reuse the same protocol objects without changing the object-level lifecycle.

## 11. MVP acceptance criteria

The first implementation is sufficient when it can:

1. create a Task with BOD escrow;
2. submit two independent Candidates against the same parent;
3. attach off-chain evidence to both;
4. submit signed Verification objects;
5. select one valid Candidate through an established arbitration adapter;
6. settle BOD reward/bond outcomes atomically;
7. reconstruct the canonical Task lifecycle from on-chain commitments plus off-chain content-addressed evidence;
8. prove that changing any signed field changes the object commitment;
9. reject stale, replayed, malformed and mismatched objects.

## 12. Explicit non-goals

v0.1 does not specify:

- a new consensus mechanism;
- validator admission;
- final verifier quorum size;
- final token emission parameters;
- final verifier staking economics;
- decentralized storage provider selection;
- a specific AI model or coding IDE;
- raw prompt/model-context persistence on-chain.

These are separate engineering decisions.

## 13. Design consequence

The protocol's scarce on-chain resource is not AI activity. It is canonical state transition and economic settlement.

Therefore the scaling target is:

    O(protocol-significant state transitions)

rather than:

    O(agent tool calls + file edits + logs + tokens + model events)

This keeps the protocol compatible with long-running AI development workloads without making the blockchain a database of every agent action.
