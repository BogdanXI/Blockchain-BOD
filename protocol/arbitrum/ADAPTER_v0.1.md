# Arbitrum adapter v0.1

Status: implementation baseline.

## Purpose

This contract is the first chain-facing implementation of the application-independent lifecycle:

Task -> Candidate -> EvidenceRoot -> VerificationRoot -> Settlement.

Arbitrum is an adapter target, not part of the protocol core. A future native BOD chain can implement the same lifecycle.

## On-chain

- Task metadata and reward escrow.
- Candidate metadata and BOD bond.
- Evidence root commitment.
- Verification root commitment.
- Settlement record and new canonical state root.

## Off-chain

The adapter does not store prompts, model context, source trees, raw Git history, individual edits, tool calls, compiler/test logs, full evidence bundles, or verifier reports. Those artifacts are authenticated by commitments.

## Settlement boundary

The settlementAuthority address is the explicit arbitration/consensus boundary. It is not a claim that BOD has solved a new consensus mechanism.

This adapter intentionally does not finalize:
- verifier quorum;
- verifier staking;
- final verifier rewards;
- validator admission;
- final token emission.

Settlement receives an already-computed economic outcome and enforces conservation of the locked task reward and selected candidate bond.

## Core invariants

1. A task escrows its reward only once.
2. Task creation requires the current state root.
3. Candidate parent must match both task parent and current state.
4. Candidate bond is transferred before candidate state exists.
5. Evidence root is immutable after candidate submission.
6. Only settlementAuthority can perform settlement.
7. A selected candidate requires a non-zero verification root.
8. A task can settle only once.
9. Settlement advances currentStateRoot exactly once.
10. Reward and bond outflows cannot exceed locked amounts.
11. No-candidate settlement refunds the full task reward to the requester.
12. Rejected-but-valid candidates remain an arbitration policy concern; the adapter does not equate rejection with invalidity.

## Limitation

Candidate IDs are supplied by the off-chain protocol and candidate sets are discoverable from CandidateSubmitted logs. This v0.1 adapter does not attempt to enumerate or mass-slash every losing candidate on-chain.

## Network target

The first deployment target is Arbitrum Sepolia (chain ID 421614), followed by Arbitrum One only after testnet evidence is sufficient. Current Arbitrum documentation lists Sepolia as chain ID 421614 and recommends testnet-first deployment for Arbitrum chains.
