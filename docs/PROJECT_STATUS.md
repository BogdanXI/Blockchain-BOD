# Project Status

**Status:** experimental public engineering prototype  
**Protocol:** v0.1  
**License:** MIT  
**Status date:** 22 November 2026

## Maintainer update

I am keeping the public scope focused on one engineering hypothesis: a portable record should make successive digital project states and their associated evidence independently verifiable, even when the original execution environment is gone.

My current engineering priorities are:

1. Keep the public claims, protocol specification, CLI behavior and tests in exact agreement.
2. Strengthen canonical input validation and independent-verifier parity.
3. Make installation and CI reproducible across supported Python versions.
4. Build a controlled comparison against Git and established provenance tools.
5. Prepare the implementation for external technical review before making production claims.

I am treating measured results and reproducible counterexamples as more important than adding features or expanding the protocol surface.

## What can be evaluated today

The public repository contains:

- deterministic snapshots of Git-tracked working-tree files;
- Evidence Envelope v0.1 with canonical serialization and self-verifying commitments;
- predecessor-linked state history;
- checks for missing predecessors, duplicate roots, forks and disconnected components;
- a portable checkpoint format binding a snapshot to an evidence envelope;
- a Python CLI for snapshot capture, checkpoint creation and verification;
- a separate verifier that does not import the reference implementation;
- regression and adversarial tests;
- an experimental Arbitrum Sepolia anchoring path.

Start with [Getting Started](GETTING_STARTED.md). The protocol and implementation are versioned independently from any future production network or economic design.

## Important implementation boundary

A BOD portable checkpoint is currently a **verification record, not a backup archive**.

A repository snapshot contains the ordered paths, SHA-256 digests and byte sizes of Git-tracked working-tree files. It does not embed those files. The `bod recover` command validates the portable checkpoint and reports its captured metadata; it does not restore the original source files.

Likewise, `VALID_INTEGRITY` means only that the verifier accepted the declared commitments and lineage rules. It does not establish semantic truth, producer honesty, evidence availability, build correctness or external-chain canonicality.

## Verification and security status

The public-readiness branch passed GitHub Actions CI run [#123](https://github.com/BogdanXI/Blockchain-BOD/actions/runs/45007814377) on Python 3.11, 3.12 and 3.13 and the Solidity 0.8.24 compile job for branch-head commit `f59105375ff73444d6e443f98de4bee4599ba7f9`. The run covered public-surface validation, Ruff static analysis, the Python test suite, the installed CLI smoke test, dependency consistency and compilation of all public Solidity sources.

- The reference verifier and independent verifier are both included in the public tree.
- The test suite covers Python protocol behavior and selected adversarial cases.
- CI compiles all public Solidity sources with pinned compiler tooling; this is a compile check only, not a Solidity behavioral test suite.
- CI results are commit-specific. A historical green run does not prove that a later commit passes.
- No independent third-party security audit is published.
- The Arbitrum integration and Solidity contracts are experimental and must not be used to secure production value.
- The economic model and any token parameters are research artifacts, not finalized monetary policy.

The [Threat Model](THREAT_MODEL_v0.1.md) documents the trust boundaries. The [Security Policy](../SECURITY.md) explains how to report issues.

## Open engineering questions

1. Does portable continuity provide measurable value beyond a well-configured Git and provenance workflow?
2. Can independent implementations agree on the same canonical test vectors and reject the same malformed inputs?
3. What payload-retention or retrieval mechanism, if any, is required for actual project restoration?
4. What transition authority and conflict-resolution model would be required before any production network claim?
5. Can external users reproduce the intended workflow and demonstrate a material reduction in recovery or verification effort?

These questions are gates, not claims of completed capability.

## External validation

No independent review report or externally validated pilot results are published in this repository at this time. The next evidence gates are:

- clean-checkout reproduction by an independent reviewer;
- a published comparison with existing tools;
- feedback from independent engineering users;
- triage and resolution of critical protocol and implementation findings.

## How to review

1. Follow [Getting Started](GETTING_STARTED.md).
2. Install the project with `python -m pip install --editable ".[test,lint]"`.
3. Run `python scripts/validate_public_surface.py`.
4. Run `ruff check --select E4,E7,E9,F src scripts tests`.
5. Run `python -m pytest -q`.
6. Run the independent verifier against a portable checkpoint or chain.
7. Inspect the latest [CI runs](https://github.com/BogdanXI/Blockchain-BOD/actions).

Please report reproducible counterexamples, missing invariants and incorrect assumptions through the [issue tracker](https://github.com/BogdanXI/Blockchain-BOD/issues). Negative results are useful when they are reproducible.
