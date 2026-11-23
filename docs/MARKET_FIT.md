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

## Empirical evidence: the need is real, but BOD demand is not established

Two primary sources support the underlying evidence-lifecycle problem:

- A 2025 USENIX Security interview study spoke with 18 experienced practitioners across 13 organizations. All 18 reported signing final software products, but verification was much less common: only two subjects from one organization described verifying build signatures before deployment, and only three subjects reported verifying signatures from external dependencies. Six subjects across five organizations identified lack of signature verification as a challenge. The study also records key-management, compatibility, usability and operationalization barriers. This is qualitative evidence, not a market-wide prevalence estimate. [Study and paper](https://www.usenix.org/system/files/usenixsecurity25-kalu.pdf).
- CISA/NSA/ODNI's SBOM Consumption guidance recommends preserving original SBOM files and tracking receipt time, location, content, retention and lifecycle. It says retention should continue until the represented software asset is decommissioned and the information is no longer relevant for legal or forensic purposes. This directly supports the importance of durable, retrievable release evidence, but it concerns SBOM lifecycle management rather than demand for BOD. [Guidance PDF](https://www.cisa.gov/sites/default/files/2024-08/SECURING_THE_SOFTWARE_SUPPLY_CHAIN_RECOMMENDED_PRACTICES_FOR_SOFTWARE_BILL_OF_MATERIALS_CONSUMPTION-508.pdf).

The USENIX study also provides negative evidence: one participant reported lack of customer demand for signing, and practitioners described usability, staffing and policy costs. BOD must therefore reduce operator effort and integrate existing cryptographic verifiers; another metadata format or hash ledger will not solve the observed verification gap.

The EU Cyber Resilience Act's reporting obligations for actively exploited vulnerabilities and severe incidents became applicable on 11 September 2026, with staged reporting timelines. This increases the operational importance of reliable records, but it does not prescribe BOD, blockchain or a particular evidence-retention product. [European Commission CRA reporting guidance](https://digital-strategy.ec.europa.eu/en/policies/cra-reporting).

**Interpretation:** these sources support a broad need for reliable evidence management and verification. They do not prove that teams need a separate continuity product, that BOD is differentiated, or that customers will pay for it. The next step is direct interviews and a comparative recovery experiment.

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
