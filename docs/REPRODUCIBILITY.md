# Reproducibility and Dependency Policy

**Status:** partially implemented; package publication and signed Git tag policy remain open.
**Last reviewed:** 2026-11-22.

## Goals

A verifier or reviewer should be able to reproduce the documented checks from a clean checkout and identify the exact toolchain and dependency versions used.

## Current controls

- Python support is declared as 3.11–3.13.
- Ruff is pinned in the optional lint dependency.
- Python CI dependencies are hash-locked in requirements-ci.txt from the reviewed requirements-ci.in input; CI installs with pip hash checking enabled and runs pip-audit.
- EAS SDK and ethers are pinned to exact direct dependency versions.
- package-lock.json is committed and CI uses npm ci.
- npm transitive overrides pin the EAS contracts package and patched Hardhat, Zod and UUID versions; the npm audit gate reports no known production dependency vulnerabilities.
- CI exercises EAS SDK runtime loading and schema encoding, not only JavaScript syntax.
- Solidity compiler version is fixed in Foundry configuration.
- All third-party GitHub Actions used by CI/release workflows are pinned to reviewed full commit SHAs.
- CI runs Python tests across the declared Python versions, Python and npm dependency audits, Foundry tests and EAS SDK runtime/schema-encoding checks.

## Known gaps

- The Python CI lock covers the declared test, lint, audit and build toolchain; it is not a lock of every optional runtime or deployment dependency.
- The npm audit result is time-sensitive and must be rechecked on dependency updates. The EAS SDK currently requires a CommonJS loading path under Node because its published ESM entrypoint imports named exports from CommonJS Lodash; CI now exercises the supported runtime path.
- The EAS SDK dependency tree includes build tooling that is not needed at runtime. Overrides reduce known advisories, but the override set must be reviewed when the SDK or its contracts package changes.
- CI uploads separate CycloneDX SBOM artifacts for the Python CI toolchain and npm dependency tree; these are not a complete inventory of every future runtime deployment.
- CI creates and verifies Sigstore-signed SLSA provenance attestations for the Python and npm SBOM artifacts.
- A separate release workflow is configured for version tags and manual dispatch: it builds the Python wheel and source archive, tests both installations, creates a CycloneDX build-environment SBOM, signs and verifies provenance for all distribution artifacts, and uploads them as a 90-day workflow artifact. The workflow has not yet been run on GitHub; local build/install smoke tests pass. It does not publish to PyPI or create a GitHub Release.
- Cryptographic signing of Git tags and publication to a package registry remain deliberately unconfigured.

## Verifying generated distribution artifacts

The release workflow verifies each artifact before upload. After downloading an artifact, verify it independently with GitHub CLI: gh attestation verify <artifact-path> --repo BogdanXI/Blockchain-BOD. The Python distribution workflow runs only for version tags (v*) or a maintainer-triggered workflow dispatch; it checks that a tag version matches the version in pyproject.toml and does not publish packages.

## Required release controls

Regenerate the Python CI lock after changing the test, lint, audit or build toolchain with: pip-compile --generate-hashes --allow-unsafe --strip-extras --output-file=requirements-ci.txt requirements-ci.in

1. Keep package-lock.json reviewed and use npm ci in CI; rerun npm audit on every dependency update.
2. Keep GitHub Actions pinned to reviewed full commit SHAs and configure Dependabot to propose updates.
3. Keep Foundry pinned to an explicit release for reproducible CI; update it deliberately.
4. Keep requirements-ci.in and its hash-locked requirements-ci.txt synchronized; refresh the lock deliberately with pip-tools, run pip-audit and verify all supported Python versions.
5. Document release ownership, approval gates, incident response and rollback before package publication.
6. Keep SLSA/in-toto provenance generation and verification enabled for every release artifact.
7. Establish a signed Git tag policy and package publication process before publishing externally.
8. Record compiler, toolchain, dependency and build parameters in release evidence.
9. Rebuild from a clean environment and compare outputs where deterministic builds are supported.

## Security boundary

A lockfile improves repeatability but does not prove that dependencies are safe. Pinned actions and packages still require update review, vulnerability monitoring and provenance checks. Reproducibility is an evidence property, not a security certification.
