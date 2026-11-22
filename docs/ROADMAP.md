# Public Roadmap

The roadmap is evidence-gated. Status labels describe the public repository as it exists today; planned work is not a delivery promise.

## 1. Portable continuity core

**Status: implemented; hardening in progress.**

- Deterministic snapshots of Git-tracked working-tree files.
- Versioned Evidence Envelope v0.1.
- Predecessor-linked state history and lineage checks.
- Portable checkpoint serialization.
- Reference and independent verification paths.
- CLI and regression tests.

**Boundary:** checkpoints currently contain file paths, digests and sizes, not source payloads. Verification is not file restoration.

**Gate:** strict canonical-input validation, reference/independent verifier parity, clean-install tests and green CI for the reviewed commit.

## 2. Reproducible engineering and supply-chain hygiene

**Status: in progress.**

- Test the supported Python versions in CI.
- Pin GitHub Actions to immutable commit SHAs.
- Declare test dependencies in project metadata.
- Check public files for private workspace material and high-confidence credential formats.
- Keep the public documentation aligned with executable behavior.

**Gate:** clean-checkout installation, full test suite, CLI smoke test and dependency consistency checks pass in CI.

## 3. Independent technical review

**Status: not yet completed.**

- Review canonical serialization and commitment boundaries.
- Compare reference and independent verifier behavior on shared positive and negative vectors.
- Review lineage, replay and fork handling.
- Review snapshot path semantics and portability.
- Review the Solidity adapter separately from the Python continuity core.
- Publish findings, severity, affected commit, reproduction steps and remediation status.

**Gate:** an external reviewer can reproduce the findings and verify the fixes against a named commit.

## 4. Product-value experiment

**Status: planned.**

Compare a BOD checkpoint workflow with a baseline using Git and established provenance/signing tools. Measure:

- time to verify the recorded state and lineage;
- ability to identify missing, modified or disconnected evidence;
- effort required to resume work in a clean runtime;
- additional operational complexity and storage cost.

Publish the method, baseline, raw reproducible artifacts and negative results. Do not claim differentiation unless the experiment supports it.

**Gate:** an independent engineering team can reproduce the comparison and confirm a material benefit.

## 5. Payload availability and actual restoration

**Status: not implemented.**

The current repository snapshot records metadata and digests. It does not retain source payloads. A future restoration capability would require an explicit payload-storage or retrieval design, integrity checks, access control, retention policy and tests for missing or unavailable objects.

**Gate:** a documented threat model and reproducible restore test across clean environments. Do not describe the current checkpoint format as a backup.

## 7. Production decision

**Status: not started.**

A production decision requires:

- independently validated user demand;
- a narrow product boundary and measurable value proposition;
- external security review;
- defined transition authority and conflict handling;
- payload availability and recovery expectations;
- operational and key-management procedures;
- measured sustainable costs;
- legal and economic review where applicable.

## Explicit non-goals

- A hash does not prove semantic truth.
- A portable checkpoint is not currently a source-code backup.
- An EVM anchor does not implement BOD consensus.
- A testnet transaction is not production-security evidence.
- Experimental economic parameters are not final monetary policy.
- No production token or native BOD network is claimed.

## Contribute

Reproducible counterexamples, missing invariants, security findings and independent comparisons are welcome. See [Contributing](../CONTRIBUTING.md) and [Security](../SECURITY.md).
