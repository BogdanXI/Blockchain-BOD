# Project status

**Release classification:** experimental public engineering prototype (alpha)
**Evidence envelope / portable checkpoint:** v0.1
**Repository snapshot:** v0.2 (v0.1 read compatibility)
**Evidence Bundle:** v0.1 experimental format
**License:** MIT
**Ethereum deployment:** none
**Independent security audit:** none

## Implemented and reviewable

- Deterministic Git-tracked repository snapshots with SHA-256 content digests, byte sizes and Git-compatible modes (100644, 100755, 120000).
- Backwards-compatible verification of legacy snapshot v0.1 documents.
- Versioned evidence envelopes and predecessor-linked project history.
- Branch-aware lineage graph verification that reports forks and heads without selecting a canonical head.
- Self-contained Evidence Bundle v0.1 packaging every referenced evidence payload included in a checkpoint, with strict completeness, size, media-type and digest checks.
- Safe bundle extraction to digest-derived filenames with a manifest; destination overwrite is refused.
- Independent verifier that does not import the BOD implementation, with tests for current and legacy snapshot formats.
- Structural inspection for in-toto Statement v1, SLSA provenance v1, DSSE envelope shape, CycloneDX JSON and SPDX JSON 2.x.
- Delegation to official sigstore-python for selected identity and GitHub artifact-attestation verification.
- One documented GitHub Actions/SBOM/Sigstore recovery experiment and one documented Reth v2.11.0 release-evidence recovery experiment.
- Solidity checkpoint registry source with Foundry unit/fuzz tests and a CI test job configured.
- EAS schema-registration and linked-attestation scripts, including clean-checkout and current-snapshot checks, a fixed Sepolia chain guard, parent-attestation checks, and both EAS and portable checkpoint identifiers.
- CI workflows for Python, Solidity and EAS SDK checks; Python/npm dependency SBOM generation and GitHub artifact-attestation verification.
- Public threat, privacy, CROPS, reproducibility, zero-cost testing, competitive landscape and grant-readiness documentation.

## Current local validation

The following checks passed locally on the current working branch:

- Python regression suite;
- Ruff checks (E4,E7,E9,F);
- public-surface validation;
- installed bod demo smoke test;
- synthetic fresh-process recovery experiment;
- EAS SDK runtime import and schema-encoding smoke test;
- npm production dependency audit (zero reported vulnerabilities).

The workstation's active Python interpreter is 3.14.4; the declared CI support matrix remains Python 3.11, 3.12 and 3.13. GitHub Actions run [45046678505](https://github.com/BogdanXI/Blockchain-BOD/actions/runs/45046678505) passed on commit cac8ce81546e895d76fcba743525f773735132d4: Python 3.11, 3.12, 3.13, Ethereum Solidity tests and EAS tooling all succeeded. Foundry is not installed in the workstation environment, so Solidity tests were validated remotely. Any later code or workflow changes require a fresh CI run.

## Ethereum integration boundary

The Solidity registry is permissionless and append-only. It checks parent existence, project identity and sequence, permits forks, and records the publisher. It does not authenticate repository ownership, select a canonical head, store evidence bytes or establish semantic truth.

No Sepolia or mainnet deployment is claimed. No EAS schema has been registered and no live attestation has been submitted. The contract has not received an independent security audit. No wallet signing or blockchain transaction was performed as part of this work.

Ethereum is an optional external witness. Local capture, portable bundle verification and independent recovery do not require a wallet, ETH, RPC endpoint or BOD-operated service.

## Legacy research boundary

Historical task/settlement, token and economic experiments remain in the source tree for traceability. They are not active product requirements, grant deliverables, deployment policy or approved monetary policy, and are excluded from the installed Python wheel. See [Legacy Components](LEGACY_COMPONENTS.md) and [Economics archive](../economics/README.md).

## Explicit non-claims

- No production-ready BOD blockchain or native consensus network.
- No production token, token launch or final tokenomics.
- No audited or production-secure smart contract.
- No guarantee that evidence is truthful, complete or available beyond payload bytes included in a verified bundle.
- No claim that an Ethereum transaction makes a release safe, valid or canonical.
- No independently demonstrated advantage over Chainloop, Kosli, Archivista, GUAC or existing Git/SLSA/Sigstore workflows.
- No independent users, pilots, expressed team interest, paying customers or product-market fit.
- No Ethereum Foundation endorsement, grant award or active application.

## Remaining validation gates

1. Obtain fresh remote CI results for the exact reviewed branch commit, including Python matrix, Foundry and EAS SDK jobs.
2. Implement and reproduce the proposed [Ethereum release evidence profile](ETHEREUM_RELEASE_PROFILE.md) using public fixtures.
3. Run a controlled comparison against Git + SLSA/in-toto + Sigstore and relevant evidence-management tools.
4. Obtain independent protocol and Solidity contract review; resolve critical/high findings.
5. Only after review and explicit authorization, rehearse deployment and EAS registration/attestation on Sepolia using free services and test ETH.
6. Obtain independent maintainer feedback and document positive and negative results.
7. Define actual contributor capacity and a costed milestone budget before any grant submission.

See [Architecture](ARCHITECTURE_OVERVIEW.md), [Grant Readiness](GRANT_READINESS.md), [Grant Technical Brief](GRANT_TECHNICAL_BRIEF.md), [Roadmap](ROADMAP.md), [Threat Model](THREAT_MODEL_v0.1.md), [Privacy Model](PRIVACY_MODEL.md), and [Verification Experiment](VERIFICATION_EXPERIMENT.md).
