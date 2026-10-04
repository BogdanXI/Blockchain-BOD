# ADR-0084 — BOD Protocol v0.1 object lifecycle and chain boundary

Status: accepted baseline

Date: 2026-10-04

## Problem

The existing architecture defined Candidate -> Verification -> Arbitration -> Canonical State, but did not yet specify:

- the Task object that creates an accountable unit of work;
- exactly which envelopes are signed;
- the boundary between off-chain evidence and on-chain commitments;
- where BOD is mandatory;
- how multiple independently valid candidates are represented.

Without these rules, an Arbitrum MVP could accidentally turn the chain into an AI event log or couple the protocol to provisional tokenomics.

## Decision

Adopt the minimal BOD Protocol v0.1 lifecycle:

    Task -> Candidate -> Evidence -> Verification -> Settlement

Use the following authority separation:

- Task authorizes work and escrows the reward.
- Candidate proposes a result but has no canonical authority.
- Evidence proves what was executed/observed through content commitments.
- Verification attests to validity under a named policy.
- Arbitration/consensus selects canonicality.
- Settlement applies the canonical result and the economic outcome atomically.

Use domain-separated signatures over complete canonical envelopes for Task, Candidate and Verification.

Keep prompts, source trees, tool calls, logs, reports and large artifacts off-chain. Commit them by content hash/Merkle root.

Record on-chain only protocol-significant commitments and economic state:

- Task escrow;
- Candidate bond;
- evidence commitment;
- verification commitment/aggregate;
- settlement;
- state-root transition;
- BOD accounting outcome.

Require BOD for reward escrow, candidate bonds and settlement-defined economic outcomes. Reserve verifier staking economics for EC-0001 calibration rather than silently introducing a new monetary rule.

## Alternatives rejected

### 1. Store the complete AI activity stream on-chain

Rejected because it scales with tool calls, file edits, prompts, logs and model events rather than economically significant state transitions.

### 2. Store only a final code hash

Rejected because a hash alone does not provide task identity, evidence provenance, verification policy, accountability or settlement semantics.

### 3. Make verifier signatures determine canonicality

Rejected because verification answers validity, while canonicality requires an arbitration/consensus rule. Conflating them would invalidate the existing architecture boundary.

### 4. Make BOD the gas token

Rejected for v0.1. The token's required role is economic accountability and settlement. Gas denomination is an execution-layer decision and is unnecessary for proving BOD utility.

### 5. Finalize verifier staking parameters now

Rejected because the repository explicitly requires adversarial economic calibration before provisional economic parameters become final protocol decisions.

## Consequences

Positive:

- Codex, Cursor and other agents can become execution clients without becoming protocol authorities.
- The same protocol objects can be implemented first on an existing EVM chain and later on a native BOD chain.
- On-chain growth is tied to canonical protocol transitions rather than raw AI activity.
- The protocol has a concrete testable boundary for signatures, evidence and settlement.

Remaining work:

- define canonical serialization and signature implementation;
- implement the deterministic object/state machine;
- build an Arbitrum adapter prototype;
- test concurrent candidates, forged evidence, replay, stale state and economic griefing;
- continue EC-0001 parameter calibration before final token economics.

This ADR does not resolve RC-0019 or claim a novel consensus mechanism.
