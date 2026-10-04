# Blockchain-BOD Protocol Architecture v0.1

Status: proposed architecture baseline

## 1. Objective

Build a public blockchain whose canonical state changes through a verifiable state-transition pipeline:

    Candidate -> Verification -> Arbitration -> Canonical State

The architecture is derived from the Canonical Architecture adaptation in docs/CANONICAL_ARCHITECTURE_ADAPTED_v0.1.md.

## 2. Layers

### 2.1 Candidate layer

A proposer submits a candidate transition against a parent state root.

Required commitments:

- parent state root;
- candidate state root;
- transition payload hash;
- execution identity;
- policy version;
- authorized verification-suite hash;
- evidence package hash;
- nonce / replay identifier;
- economic bond.

A candidate has no authority to modify canonical state.

### 2.2 Verification layer

Independent verifiers reproduce the transition and check:

- parent state matches the advertised parent;
- execution is deterministic;
- candidate artifact matches the tested artifact;
- authorized tests/checks pass;
- evidence is fresh and correctly committed;
- authorization and policy are valid;
- token accounting balances;
- no replay condition is violated.

A verifier returns a signed verification result. Verification does not by itself make the candidate canonical.

### 2.3 Arbitration layer

If more than one candidate is valid for the same parent state, consensus/arbitration selects exactly one canonical transition according to a protocol rule.

The v0.1 architecture intentionally does not claim a new consensus mechanism. The first implementation may use an established consensus adapter while the research program continues to test the novel authority frontier.

### 2.4 Canonical state layer

The state machine applies only the selected transition:

    S(n+1) = Apply(S(n), T_canonical)

All nodes must obtain the same resulting state root from the same parent and canonical transition.

### 2.5 Economic layer

The economic state is updated atomically with the canonical state.

Economic events include:

- transaction fees;
- candidate bonds;
- verifier rewards;
- arbitration rewards;
- penalties/slashing;
- scheduled token emission;
- treasury inflows/outflows;
- fee burns.

## 3. Transition validity

Conceptually:

    VALID(T) =
      parent == current_state
      AND candidate_commitment_valid
      AND authorization_valid
      AND policy_valid
      AND execution_reproducible
      AND evidence_valid
      AND verification_threshold_met
      AND economic_accounting_balances
      AND replay_protected

The exact verifier threshold and consensus mechanism are implementation parameters, not yet a novel-primitive claim.

## 4. Concurrency

For a parent state S(n), the network may observe:

    S(n) -> C1
    S(n) -> C2
    S(n) -> C3

where all candidates may individually satisfy VALID(T).

Therefore:

1. verification determines admissibility;
2. arbitration determines canonicality;
3. state execution applies only the canonical candidate;
4. rejected-but-valid candidates receive the protocol-defined economic outcome.

The economic policy must not make a rejected valid candidate indistinguishable from an invalid candidate.

## 5. Economic invariants

For every accepted transition:

- total supply never exceeds the hard cap;
- no unauthorized mint exists;
- no balance becomes negative;
- every burn has a recorded source;
- every reward has a deterministic recipient rule;
- every slash has a defined fault predicate;
- every bond has a deterministic release/penalty rule;
- treasury spending cannot exceed available treasury balance;
- emission cannot exceed the remaining unissued reserve.

## 6. Failure behavior

Invalid candidate -> reject and apply bond policy.

Valid but non-canonical candidate -> reject from canonical state; apply non-canonical candidate policy.

Verifier disagreement -> invoke the consensus/verifier dispute rule; do not silently accept.

Stale candidate -> reject.

Replay -> reject.

State-root mismatch -> reject.

Economic accounting mismatch -> reject the transition.

## 7. Technology boundary

The architecture is technology-neutral regarding:

- cryptographic primitives;
- networking;
- storage;
- VM/execution environment;
- consensus implementation.

Those choices must be specified only after their role in the transition pipeline is clear.

## 8. Development sequence

1. deterministic state model;
2. token accounting;
3. candidate format;
4. verification interface;
5. consensus adapter;
6. adversarial tests;
7. simulation;
8. network implementation;
9. benchmark and security review.


## 9. BOD Protocol v0.1 interface

The application-independent lifecycle is refined to:

    Task -> Candidate -> Evidence -> Verification -> Settlement

Task creates the accountable unit of work and escrows its reward. Candidate proposes a result. Evidence remains content-addressed off-chain. Verification attests to validity under a named policy. Arbitration/consensus determines canonicality. Settlement applies the selected result and the economic outcome atomically.

The exact signed envelopes, on-chain commitments, off-chain boundary and BOD utility requirements are specified in protocol/BOD_PROTOCOL_v0.1.md.

This refinement does not change the existing rule that verification and canonicality are distinct.

## 10. Chain/storage boundary

The protocol does not store prompts, model context, raw source trees, tool calls, logs or full evidence bundles on-chain. On-chain state stores only protocol-significant commitments and economic transitions.

An initial EVM/Arbitrum adapter is permitted without making Arbitrum part of the protocol core. A future native BOD chain may implement the same object lifecycle.

## 11. Protocol status

The Task-to-Settlement object model is a v0.1 specification baseline. Canonical serialization, executable state transitions, signature implementation and adapter contracts remain implementation work.


## 11. Arbitrum adapter v0.1

The first chain-facing adapter is implemented at protocol/arbitrum/BODProtocolAdapterV0_1.sol.

It stores only protocol-significant state:

- Task metadata and BOD reward escrow;
- Candidate metadata and BOD bond;
- EvidenceRoot commitment;
- VerificationRoot commitment;
- Settlement and canonical state-root transition.

The adapter injects the existing arbitration/consensus boundary through settlementAuthority. It does not define a new consensus mechanism or finalize verifier economics. Arbitrum Sepolia is the first deployment target; the protocol core remains chain-independent.
