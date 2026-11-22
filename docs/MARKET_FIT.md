# Market hypothesis and validation plan

## Target problem

Software teams increasingly produce signed build provenance, SBOMs, vulnerability reports and release attestations. The unresolved workflow hypothesis is that these records are fragmented across systems and do not, by themselves, provide a portable, deterministic continuity chain that a new operator can reconstruct after the original CI runner or runtime is gone.

BOD targets the continuity/recovery gap between existing evidence systems. It is not a replacement for them.

## Initial users to validate

1. Maintainers of open-source infrastructure and Ethereum clients.
2. Protocol and smart-contract teams with release and audit obligations.
3. Security engineering and software-supply-chain teams.
4. CI/platform engineering teams operating reproducible build and release pipelines.
5. Auditors who need to reconstruct which evidence supported a historical release.

These are hypotheses, not confirmed customers.

## Why Ethereum is relevant

Ethereum can provide a public, independently queryable timestamped commitment for a release checkpoint. The chain should be used only when an external witness is worth the gas cost. Local verification must remain useful without it.

BOD should integrate with established provenance and attestation systems, including SLSA/in-toto, Sigstore/Rekor, SPDX/CycloneDX and EAS. A proprietary registry alone is not a defensible market advantage.

## Direct competitor review

The direct product set includes Chainloop, Kosli, Archivista and GUAC—not only standards such as SLSA and Sigstore. These projects already cover substantial parts of evidence collection, immutable event recording, attestation storage, graph queries, policy enforcement and export. BOD must not position those capabilities as missing from the market.

The current product hypothesis is narrower: a deterministic predecessor-linked record of successive evidence states, with a self-contained package of referenced payloads and an independent clean-room verifier. This remains unvalidated. The required head-to-head test and documented competitor boundaries are in [Competitive landscape](COMPETITIVE_LANDSCAPE.md).

## Competitive baseline

The comparison must include Git tags and signed commits, SLSA/in-toto provenance, Sigstore and Rekor transparency, GitHub artifact attestations, SPDX/CycloneDX SBOM workflows, and EAS for Ethereum ecosystem attestations.

The project must demonstrate a material reduction in recovery time, audit effort, missing context or verification ambiguity. If it cannot, the product hypothesis should be narrowed or rejected.

## Pilot experiment

For a real open-source repository:

1. Produce a release using the repository's existing CI pipeline.
2. Capture source commit, build provenance, SBOM, test report and release artifacts by digest.
3. Create a BOD checkpoint linked to its predecessor.
4. Remove access to the original runner/workspace and recover in a clean environment.
5. Independently verify the checkpoint and all available referenced evidence.
6. Repeat using the baseline toolchain without BOD.
7. Measure operator time, steps, missing evidence, failure detection, gas and storage costs.

Publish scripts, test fixtures, raw non-sensitive measurements and negative results.

## Success criteria

- At least two independent teams reproduce the procedure.
- At least one team identifies a recurring workflow where BOD materially reduces effort or risk.
- The same result can be independently verified without a BOD-operated service.
- The cost of optional Ethereum anchoring is measured and acceptable to the pilot user.
- Security and privacy boundaries are documented.

## Claims policy

Do not claim market demand, production readiness, security certification, Ethereum endorsement or customer adoption until there is direct evidence.
