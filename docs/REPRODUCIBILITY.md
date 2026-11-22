# Reproducibility and Dependency Policy

**Status:** partially implemented; release-grade provenance and Python locking remain open.
**Last reviewed:** 2026-11-22.

## Goals

A verifier or reviewer should be able to reproduce the documented checks from a clean checkout and identify the exact toolchain and dependency versions used.

## Current controls

- Python support is declared as 3.11–3.13.
- Ruff is pinned in the optional lint dependency.
- EAS SDK and ethers are pinned to exact direct dependency versions.
- package-lock.json is committed and CI uses npm ci.
- npm transitive overrides pin the EAS contracts package and patched Hardhat, Zod and UUID versions; npm audit --omit=dev reports zero known vulnerabilities at the last local check.
- CI exercises EAS SDK runtime loading and schema encoding, not only JavaScript syntax.
- Solidity compiler version is fixed in Foundry configuration.
- Several GitHub Actions are pinned to full commit SHAs.
- CI runs Python tests across the declared Python versions, Foundry tests, npm vulnerability audit and EAS SDK runtime/schema-encoding checks.

## Known gaps

- Python test/lint dependencies are bounded but not captured in a complete cross-platform lockfile.
- The npm audit result is time-sensitive and must be rechecked on dependency updates. The EAS SDK currently requires a CommonJS loading path under Node because its published ESM entrypoint imports named exports from CommonJS Lodash; CI now exercises the supported runtime path.
- The EAS SDK dependency tree includes build tooling that is not needed at runtime. Overrides reduce known advisories, but the override set must be reviewed when the SDK or its contracts package changes.
- The project has not yet published a complete SBOM and signed provenance for its own releases.

## Required release controls

1. Keep package-lock.json reviewed and use npm ci in CI; rerun npm audit on every dependency update.
2. Keep GitHub Actions pinned to reviewed full commit SHAs and configure Dependabot to propose updates.
3. Keep Foundry pinned to an explicit release for reproducible CI; update it deliberately.
4. Produce a Python dependency lock or constraints file for release verification.
5. Generate SPDX or CycloneDX SBOM for release artifacts.
6. Generate and verify SLSA/in-toto build provenance.
7. Sign release artifacts and provenance with a supported Sigstore workflow.
8. Record compiler, toolchain, dependency and build parameters in release evidence.
9. Rebuild from a clean environment and compare outputs where deterministic builds are supported.

## Security boundary

A lockfile improves repeatability but does not prove that dependencies are safe. Pinned actions and packages still require update review, vulnerability monitoring and provenance checks. Reproducibility is an evidence property, not a security certification.
