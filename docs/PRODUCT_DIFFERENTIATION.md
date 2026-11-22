# Product differentiation and competitive boundary

**Product:** BOD Evidence Fabric
**Status:** hypothesis under validation; not a claim of unique cryptographic primitives or proven market demand.

## The proposed wedge

BOD is designed to preserve a **portable, predecessor-linked history of release-evidence states** across repositories, CI systems, evidence formats and operators.

A BOD checkpoint commits to a deterministic project snapshot and an evidence set. A later checkpoint can reference its predecessor. The verifier can reconstruct and check the relationship from exported data without requiring a BOD-hosted service. The experimental Evidence Bundle v0.1 can additionally carry the raw bytes of every referenced evidence payload, so those payloads remain inspectable without the original evidence store. The Ethereum registry is an optional external witness for compact commitments; it is not required for local verification and does not decide which fork is canonical.

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

## Direct competitors and substitutes

The closest overlaps are not only standards. Chainloop and Kosli already provide SDLC evidence collection/storage and immutable delivery histories; Archivista stores signed in-toto attestations in a queryable graph and supports export; GUAC ingests SBOM/SLSA/in-toto metadata into a graph. These capabilities materially narrow BOD's novelty claim.

The current BOD hypothesis is therefore limited to deterministic predecessor-linked state snapshots plus self-contained packaging of referenced payloads and independent clean-room verification. Even this is not yet proven unique. See the [competitive landscape and required head-to-head test](COMPETITIVE_LANDSCAPE.md).

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
- self-contained evidence bundles with complete referenced-payload coverage and a separate independent verifier;
- minimal structural inspection of in-toto Statement v1, SLSA provenance v1, DSSE envelope shape, CycloneDX JSON and SPDX JSON 2.x; no cryptographic signature verification is claimed;
- predecessor-linked checkpoint semantics in the Ethereum registry source;
- branch-aware lineage graph verification in the Python library, CLI and independent verifier;
- local Foundry tests, including fuzz tests;
- EAS SDK client scripts and CI syntax/smoke checks;
- CI-generated SBOMs and GitHub artifact attestations for build outputs.

Not yet demonstrated:

- repeatable multi-provider ingestion and policy integration; one real end-to-end test bound a CycloneDX SBOM and Sigstore bundle to the exact 108-file GitHub PR merge tree, removed local original evidence copies, recovered both payloads from a BOD bundle and passed offline Sigstore verification; broad interoperability and automated verification are not yet established;
- a live Sepolia deployment and EAS schema/attestation round trip;
- recovery after removing access to a real external CI/storage provider using independent pilots and third-party evidence;
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


## Evidence of the underlying problem

A USENIX Security 2025 interview study of 18 practitioners across 13 organizations found a gap between signing and verification: all participants reported signing final products, while verification of build signatures before deployment and external dependency signatures was uncommon. The study also identified key-management, compatibility, usability and operationalization barriers. CISA/NSA/ODNI guidance recommends retaining original SBOM files through the software asset lifecycle and while they remain relevant for legal or forensic purposes.

These sources validate the broader evidence-lifecycle and verification problem, not demand for BOD. BOD now has an optional wrapper around the official sigstore-python verifier. One real GitHub Actions SBOM and Sigstore bundle were packaged against the matching merge-tree snapshot, recovered after deletion of local original copies and verified offline. BOD delegates cryptography; broad multi-provider policy verification is still incomplete. A product claim that it solves that gap would be premature.
