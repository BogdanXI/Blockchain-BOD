# Reproducibility and Dependency Policy

**Status:** policy and remediation checklist; not all controls are implemented.  
**Last reviewed:** 2026-11-22.

## Goals

A verifier or reviewer should be able to reproduce the documented checks from a clean checkout and identify the exact toolchain and dependency versions used.

## Current controls

- Python support is declared as 3.11–3.13.
- Ruff is pinned in the optional lint dependency.
- EAS SDK and ethers are pinned to exact direct dependency versions.
- Solidity compiler version is fixed in Foundry configuration.
- Several GitHub Actions are pinned to full commit SHAs.
- CI runs Python tests across the declared Python versions, Foundry tests and EAS JavaScript syntax checks.

## Known gaps

- A committed npm lockfile is not currently present. The current CI installation is therefore not a fully reproducible transitive npm dependency installation.
- Foundry GitHub Action is referenced by a moving major-version tag and should be pinned to a reviewed full commit SHA.
- Foundry itself is installed using the moving stable toolchain version. Pin a reviewed release for release and audit workflows.
- Python dependency constraints for test tools are not all exact lock pins.
- The project has not yet published a complete SBOM and signed provenance for its own releases.

## Required release controls

1. Commit and review package-lock.json; use npm ci in CI.
2. Pin GitHub Actions to reviewed full commit SHAs and configure Dependabot to propose updates.
3. Pin Foundry to an explicit release for reproducible CI; update it deliberately.
4. Produce a Python dependency lock or constraints file for release verification.
5. Generate SPDX or CycloneDX SBOM for release artifacts.
6. Generate and verify SLSA/in-toto build provenance.
7. Sign release artifacts and provenance with a supported Sigstore workflow.
8. Record compiler, toolchain, dependency and build parameters in release evidence.
9. Rebuild from a clean environment and compare outputs where deterministic builds are supported.

## Security boundary

A lockfile improves repeatability but does not prove that dependencies are safe. Pinned actions and packages still require update review, vulnerability monitoring and provenance checks. Reproducibility is an evidence property, not a security certification.
