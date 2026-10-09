# Public Roadmap

The project advances by evidence, not dates. This roadmap describes plans, not guarantees.

## 1. Portable continuity core

**Status: implemented; regression-gated.**

- Deterministic repository snapshots.
- Versioned evidence envelopes and predecessor links.
- Independent verification and portable checkpoints.
- Fresh-process recovery and tamper-rejection tests.

Gate: implementation, tests, independent verifier, and passing CI for the reviewed commit.

## 2. Independent review

**Status: in progress.**

- Document trust assumptions and known limits.
- Reproduce verification from a clean checkout.
- Invite external technical review and track findings.

Gate: current CI green and review findings triaged.

## 3. Product-value experiment

**Status: planned.**

Compare recovery from BOD checkpoints with a baseline using Git and existing provenance tools. Measure recovery correctness, missing context, time to resume, and verification failures. Publish reproducible methods and privacy-safe results, including negative results.

Gate: an independent reviewer can reproduce the experiment.

## 4. Arbitrum testnet integration

**Status: experimental.**

- Treat EVM anchoring as optional infrastructure, not BOD consensus.
- Complete the test-only custom gas-token creation path before L3 genesis.
- Measure execution and parent-chain data-posting costs separately.
- Test bridge and fee-pricer configuration.
- Keep production token decisions behind separate review gates.

Gate: deterministic integration tests, testnet evidence, and a documented cost model. Testnet success is not production readiness.

## 5. Canonicality review

**Status: blocking for production claims.**

Specify transition authority and conflict handling; distinguish validity, acceptance, and canonicality; obtain independent review; resolve critical findings with evidence.

## 6. Production decision

**Status: not started.**

Requires a clear user value proposition, security and operational review, recovery and availability expectations, measured sustainable costs, key-management procedures, and relevant legal review.

## Explicit non-goals

- Hashes do not prove semantic truth.
- A testnet adapter does not implement native BOD consensus.
- Experimental economic values are not final monetary policy.
- No production token or network is claimed.

## Contribute

Submit reproducible counterexamples, missing invariants, security concerns, or comparisons with existing tools. See [Contributing](../CONTRIBUTING.md) and [Security](../SECURITY.md).
