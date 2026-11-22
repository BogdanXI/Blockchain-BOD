## 2026-11-22 — Ethereum ecosystem track

- Repositioned the public product around Ethereum-anchored software-state continuity and supply-chain evidence interoperability.
- Added a permissionless append-only Ethereum checkpoint registry with explicit predecessor and sequence validation.
- Added Foundry tests for genesis, parent validation, duplicate rejection, project isolation and observable forks.
- Added Ethereum integration, threat-model, market-hypothesis and roadmap documentation.
- Added Ethereum Mainnet and Sepolia fee-policy descriptors using live base-fee inputs rather than a stale hard-coded floor.
- Retained the Arbitrum implementation as a legacy experimental adapter; no mainnet deployment or security audit is claimed.

## 2026-10-09 — External review readiness

- Clarified that BOD is an experimental continuity prototype and does not claim a production network or solved native consensus.
- Added an evidence-gated public roadmap and a dedicated current-status document.
- Expanded the local quickstart with clean-checkout verification commands and explicit limits on what verification proves.
- Strengthened contribution and security reporting guidance.
- Normalized the installed portable-checkpoint module import path and test configuration after the install-and-test smoke check exposed mismatched exception classes.
- Isolated Python 3.12 verification passed after the fix: package install, public-surface validation, CLI demo, repository snapshot, and full pytest suite.
- GitHub Actions status is not available from the current connector response; do not merge until the PR checks are inspected.

## 2026-10-08 — Red-team hardening of Evidence Fabric

- Replaced ambiguous verifier success semantics with explicit `VALID_INTEGRITY` reporting.
- Added a trust-policy layer for required evidence types, issuers and retrieval metadata.
- Explicitly modelled semantic truth as `NOT_ASSERTED` and evidence availability as `UNKNOWN` until independently checked.
- Added an independent verifier implementation that does not import the BOD reference implementation.
- Added a public threat model covering dishonest producers, compromised CI, history rewriting, anchor compromise, verifier bugs and BOD service loss.
- Added a product-boundary document explaining why BOD composes SLSA/in-toto, Sigstore/Rekor and SBOM standards instead of replacing them.
- Tightened public positioning: continuity and portability are hypotheses to be measured, not unsupported market claims.

## 2026-10-08 — Evidence Fabric public product baseline

- Reframed the public repository around BOD Evidence Fabric: deterministic state -> evidence envelope -> verification -> optional external anchor -> fresh-runtime recovery.
- Published deterministic Evidence Envelope v0.1 and adversarial lineage verification.
- Added an installable `bod` CLI with repository snapshots, envelope creation, verification and local demonstration.
- Added an anchor-provider abstraction with a free local provider for development.
- Added product quickstart, architecture documentation and public product identity assets.
- Hardened the public-surface validator so legitimate identifiers containing blocked substrings are not rejected.
- Verified the public tree locally: public-surface validation passed, product demo returned `VALID`, and **97 tests passed**.

## 2026-10-06 — Network-aware Arbitrum fee preparation

- The public MetaMask bridge now reads the Arbitrum chain-reported minimum gas price before transaction preparation.
- Priority fee remains zero, max-fee headroom remains 20%, and the submitted gas limit uses the exact Arbitrum estimate without a fixed 15% padding.
- Added public ADR-0109 documenting the network fee boundary and its non-final economic status.
