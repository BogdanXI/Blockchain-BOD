# Product differentiation and competitive boundary

**Product:** BOD Evidence Fabric
**Status:** hypothesis under validation; not a claim of unique cryptographic primitives or proven market demand.

## The proposed wedge

BOD is designed to preserve a **portable, predecessor-linked history of release-evidence states** across repositories, CI systems, evidence formats and operators.

A BOD checkpoint commits to a deterministic project snapshot and an evidence set. A later checkpoint can reference its predecessor. The verifier can reconstruct and check the relationship from exported data without requiring a BOD-hosted service. The Ethereum registry is an optional external witness for compact commitments; it is not required for local verification and does not decide which fork is canonical.

The intended benefit is not another signature, SBOM, provenance statement or transparency log. It is a continuity and recovery layer that lets an independent party ask:

- Which exact project/evidence state is this release connected to?
- What changed between successive checkpoints?
- Can a verifier detect a broken, missing, duplicated or forked lineage?
- Can the evidence history be reconstructed after losing access to the original CI runner, workstation or vendor service?

## Comparison with established tools

| System | Primary capability | BOD's intended relationship | What BOD must still prove |
|---|---|---|---|
| Git and signed tags | Source history, content identity and signed release references | Capture a portable snapshot and bind release evidence beyond source commits | A recovery or audit benefit beyond a clean Git mirror and signed tags |
| SLSA provenance / in-toto | Verifiable statements about how artifacts and supply-chain steps were produced | Reference provenance by digest and preserve it in a sequence of project checkpoints | Correct parsing, policy validation and end-to-end interoperability |
| Sigstore / Rekor | Artifact signing, identity binding and public transparency-log records | Reference signed artifacts/attestations without replacing signing or transparency | Independent verification of referenced bundles and continuity after source services change |
| GitHub artifact attestations | Signed provenance and optional SBOM association for GitHub-built artifacts | Consume and bind GitHub attestations as one evidence source | Portability across non-GitHub builders and a measurable benefit over GitHub's native verification |
| SPDX / CycloneDX | Standardized software inventory and component metadata | Commit to SBOM digests and preserve which inventory belonged to each checkpoint | Format-aware validation and evidence retrieval, not just digest storage |
| Ethereum Attestation Service | General-purpose on-chain/off-chain attestations | Use EAS as an optional attestation transport for checkpoint claims | Live testnet interoperability, schema lifecycle and independent verification |

These systems solve important problems already. BOD should integrate with them rather than imply that they lack provenance, signatures, timestamps or append-only records.

## What is potentially distinctive

The proposed combination has four properties:

1. **Longitudinal evidence continuity:** checkpoints link successive project/evidence states, rather than treating each release record as an isolated object.
2. **Portable verification:** exported checkpoint material is intended to be independently checked without a BOD-operated backend, account or wallet.
3. **Explicit branch/fork visibility:** the registry permits multiple descendants and does not silently select a canonical project head.
4. **Chain-optional architecture:** local verification remains useful without Ethereum; an Ethereum transaction adds an external public witness rather than becoming a service dependency.

The distinction is the composition and workflow, not a claim that hashing, Merkle structures, attestations, append-only logs or provenance are new inventions.

## Current evidence versus unfinished work

Implemented in the current public branch:

- deterministic portable checkpoint and snapshot verification;
- predecessor-linked checkpoint semantics in the Ethereum registry source;
- local Foundry tests, including fuzz tests;
- EAS SDK client scripts and CI syntax/smoke checks;
- CI-generated SBOMs and GitHub artifact attestations for build outputs.

Not yet demonstrated:

- end-to-end ingestion and policy verification of SLSA/in-toto, SPDX/CycloneDX and Sigstore evidence from independent systems;
- a live Sepolia deployment and EAS schema/attestation round trip;
- recovery after removing access to the original repository/CI/storage provider;
- comparative results against Git + SLSA/in-toto + Sigstore/GitHub attestations without BOD;
- adoption or validation by independent Ethereum maintainers;
- an independent security review.

## Required falsifiable experiment

Run the same release-recovery task with and without BOD using at least two independent repositories and maintainers.

Record, for each approach:

- time and operator steps to reconstruct the release evidence;
- evidence references found, missing, invalid or no longer retrievable;
- whether source, artifact, provenance and SBOM digests match;
- whether a changed or forked checkpoint is detected;
- recovery success from a fresh machine with original CI/workspace access removed;
- Ethereum gas and any other infrastructure cost, where anchoring is used.

Publish the scripts, fixtures, environment, raw non-sensitive measurements and negative results. If BOD does not materially improve recovery, continuity or audit effort, narrow or reject the product claim.

## Grant-facing positioning

The strongest defensible proposal is a small, open-source Ethereum ecosystem infrastructure project: build and validate a reusable release-evidence continuity and recovery workflow for Ethereum client/tooling maintainers. Funding should be requested for measurable integrations, independent security review and pilots—not for creating another blockchain, token or generic hash registry.
