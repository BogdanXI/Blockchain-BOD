## 2026-11-22 — Ethereum release profile v0.1 implementation

- Published a versioned JSON Schema for Ethereum client releases and smart-contract deployment/upgrade records.
- Added a dependency-free structural validator and the `bod profile-validate` CLI command, with explicit non-claims for cryptographic verification, chain-state verification and semantic truth.
- Added a real Reth v2.11.0 release fixture using recorded source and binary identities; missing SLSA provenance and unproven binary-to-source correspondence remain explicit gaps.
- Added regression tests for profile structure, invalid digests, invalid URIs, contract-specific requirements, deployment address width, predecessor consistency and CLI behavior.
- Updated quickstart, project status and grant documents to distinguish implemented profile structure from unimplemented native verification and smart-contract deployment workflows.

## 2026-11-22 — Ethereum grant-readiness and protocol hardening

- Added a grant technical brief scoped to portable release-evidence continuity for Ethereum software and smart-contract upgrades, with measurable milestones, acceptance criteria, evaluation metrics and explicit non-goals.
- Added an ESP readiness assessment that records the current absence of active Wishlist items, RFPs and open rounds, and separates demonstrated engineering evidence from unvalidated demand and future work.
- Versioned repository snapshots to v0.2 and committed Git-compatible file modes (`100644`, `100755`, `120000`) so executable-bit changes alter the state root; retained v0.1 snapshot verification compatibility in both verifiers.
- Added regression coverage for executable-bit changes, symlink mode, invalid modes and legacy snapshot verification.
- Extended the EAS schema to carry both the EAS-context checkpoint identifier and the portable BOD checkpoint identifier. The client now checks that the supplied checkpoint matches the current clean repository snapshot before submitting an attestation.
- Updated public documentation, quickstart commands, grant status, roadmap and zero-cost test status to reflect the current implementation and known limitations.
- Made the historical task/settlement and token-economics boundary explicit in testnet readiness metadata and documentation; added a packaging regression test to ensure legacy economic modules stay outside the installed Python wheel.
- Local validation: Python tests, Ruff, public-surface validation, CLI smoke test, recovery experiment, EAS SDK schema-encoding smoke test and npm production dependency audit passed. Foundry is unavailable in the local workstation environment; GitHub Actions run 45047051723 passed all five jobs on commit ab1ed4b0e93990476b6978cb40b59e8cbe24aa82.
- No EAS schema registration, wallet signing, Sepolia deployment, mainnet transaction or paid test service was used.

## 2026-11-22 — Verified evidence bundle extraction

- Added `bod bundle-extract` to verify a self-contained Evidence Bundle before extracting its evidence payloads.
- Uses digest-derived filenames and a machine-readable extraction manifest; refuses to overwrite an existing destination directory and never uses untrusted evidence metadata as a path.
- Added tests for successful extraction, CLI behavior, tampering rejection, overwrite refusal and path traversal resistance.

## 2026-11-22 — Sigstore verification delegation

- Added evidence-verify CLI modes that delegate GitHub workflow identity/claim verification and generic identity/OIDC issuer verification to the official sigstore-python CLI.
- The wrapper uses argument arrays without a shell, enforces explicit expected identity claims, supports explicit offline mode and reports the verifier exit status.
- Added mocked tests for success, policy requirements, missing verifier and failed verification.
- Verified a real GitHub Actions SBOM attestation bundle offline using sigstore-python 4.5.1; then packaged the SBOM and Sigstore bundle with a BOD checkpoint bound to the exact 108-file GitHub merge-tree snapshot, deleted local original copies, recovered both payloads and re-verified the recovered SBOM. Documented exact run, digests, identities and trust-root freshness caveat.
- BOD delegates cryptography; it does not implement Sigstore signature or transparency verification itself.

## 2026-11-22 — Evidence format interoperability

- Added dependency-free structural inspection for in-toto Statement v1, SLSA provenance v1, DSSE envelope shape, CycloneDX JSON and SPDX JSON 2.x.
- Added the bod evidence-inspect CLI command and regression fixtures for supported structures and malformed documents.
- Extended the synthetic offline recovery experiment to inspect SLSA and CycloneDX fixture structures before packaging.
- Documented that structural inspection is not full schema validation, signature verification, trust-policy evaluation or a claim of semantic truth.
- Added official format specification references and explicit SPDX 3.x non-support.

## 2026-11-22 — Evidence continuity and recovery

- Added experimental Evidence Bundle v0.1 to package every raw evidence payload referenced by one portable checkpoint.
- Added strict bundle commitment, payload digest, size, media-type and completeness verification.
- Added a separate independent bundle verifier and CLI commands to create and verify bundles.
- Documented explicit trust boundaries: payload integrity is checked, semantic truth and format-specific signatures are not asserted, and repository source is not included.
- Added regression coverage for successful bundle round trips, missing payloads, tampering and independent verification.

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
