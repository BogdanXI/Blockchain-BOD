# Project Status

**Release status:** experimental public engineering prototype  
**Protocol version:** v0.1  
**License:** MIT

## What can be evaluated

The public repository contains a local continuity workflow:

1. Capture a deterministic repository snapshot.
2. Bind its state root to a versioned evidence envelope.
3. Verify the envelope and predecessor-linked history.
4. Export a portable checkpoint.
5. Verify and recover the checkpoint in a fresh process.

Start with [Getting Started](GETTING_STARTED.md). The reference implementation, CLI, independent verifier, tests, and CI workflow are part of this repository.

## Verification record

A prior public CI run passed for commit [316f261](https://github.com/BogdanXI/Blockchain-BOD/commit/316f26115c9d8578276f1553f3dce876c8b5ed34). Check the live [CI workflow](https://github.com/BogdanXI/Blockchain-BOD/actions/workflows/ci.yml) before relying on that result; a historical pass does not establish the current branch status.

Tests are evidence for the behaviors they exercise. They are not an external security audit or proof of production readiness.

## What is not claimed

- No production-ready BOD blockchain or native consensus mechanism is claimed.
- No production token launch is claimed.
- Cryptographic integrity does not prove semantic truth.
- The repository does not guarantee availability of referenced evidence.
- EVM or Arbitrum inclusion does not by itself make a BOD transition valid or canonical.
- Economic assumptions and fee targets remain experimental until measured and independently reviewed.

## Current open question

Does portable, independently verifiable continuity materially improve a real engineering workflow compared with Git and established provenance/signing tools? This requires independent users and reproducible comparisons, not marketing claims.

Technical limitations are documented in the [Threat Model](THREAT_MODEL_v0.1.md). Planned validation gates are in the [Roadmap](ROADMAP.md).

## How to review

1. Follow [Getting Started](GETTING_STARTED.md).
2. Run `python -m pytest -q`.
3. Inspect the latest public CI result.
4. Review [Why BOD Exists](WHY_BOD_v0.1.md) and the [Threat Model](THREAT_MODEL_v0.1.md).
5. Report a reproducible counterexample, missing invariant, or comparison through the [issue tracker](https://github.com/BogdanXI/Blockchain-BOD/issues).

Feedback that disproves the product hypothesis or exposes a verification boundary is useful.
