## 2026-11-22 — Public engineering hardening

- Reworked the public README and product documentation to align claims with executable behavior and clearly distinguish checkpoint verification from source-payload restoration.
- Added a dated maintainer update and an evidence-gated roadmap focused on independent review, reproducibility and measurable product value.
- Replaced the public-surface term blacklist with checks for private workspace paths and high-confidence credential formats.
- Tightened portable snapshot validation for normalized relative paths, sorted entries, digest formats and integer file sizes.
- Aligned the independent verifier with the reference verifier's envelope and snapshot validation rules.
- Changed the portable CLI status to `CHECKPOINT_VERIFIED` and made the demo verify the checkpoint it creates.
- Declared test dependencies in project metadata, modernized SPDX license metadata and expanded CI to Python 3.11–3.13.
- Pinned GitHub Actions references to immutable release commits.
- Added a pinned Ruff toolchain and made static analysis a required CI step.
- Added locked Node tooling for Arbitrum workflows and a CI compile gate for all public Solidity contracts.
- Added explicit Arbitrum Sepolia chain-ID checks before deployment or anchoring.
- Local validation on Python 3.14.4: public-surface validation passed, **109 tests passed**, Ruff static analysis passed, the Solidity 0.8.24 compile check passed, the CLI demo passed and `pip check` reported no broken requirements. The distributable wheel built successfully; snapshot tests cover symlink handling without reading target contents. A distributable wheel also built successfully and contained the CLI and core verification modules.
- GitHub Actions CI run [#123](https://github.com/BogdanXI/Blockchain-BOD/actions/runs/45007814377) passed Python 3.11, 3.12 and 3.13 plus the Solidity 0.8.24 compile job for branch-head commit `f59105375ff73444d6e443f98de4bee4599ba7f9`.

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
