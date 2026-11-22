# Grant technical brief: BOD release-evidence continuity for Ethereum

**Document type:** pre-application technical brief  
**Prepared:** 22 November 2026  
**Project status:** experimental open-source prototype  
**Requested programme:** Ethereum Foundation Ecosystem Support Program (ESP), subject to a future matching Wishlist item or RFP  
**Funding request:** not yet set; to be costed against an agreed scope and verified contributor capacity  
**License:** MIT

## 1. Executive summary

BOD is an open-source, local-first system for preserving and independently verifying continuity between software project states and the evidence associated with releases. It combines deterministic repository snapshots, predecessor-linked checkpoints, portable evidence bundles, independent verification, and optional Ethereum-native witnesses.

The proposed Ethereum-focused work is narrower than a general blockchain or software-supply-chain platform: develop and validate a portable release-history profile for Ethereum software and smart-contract projects. The profile would connect a source revision to its build configuration, compiler outputs, test and security evidence, deployment or upgrade references, and the preceding release. Evidence payloads remain portable and off-chain; Ethereum L1 and Ethereum Attestation Service (EAS) are optional public witness layers.

The central question is empirical: **does a portable, independently verifiable, predecessor-linked release record materially improve recovery and audit workflows when compared with Git plus established provenance, signing and evidence-management tools?** The project will publish the comparison even if results do not demonstrate an advantage.

BOD does not propose a new token, L2, bridge, rollup, proprietary evidence format mandate, or replacement for SLSA, in-toto, Sigstore, SPDX, CycloneDX, Sourcify or EAS.

## 2. Problem and ecosystem relevance

Ethereum client teams, smart-contract developers and infrastructure maintainers use several systems to produce and retain release evidence. Source history, build provenance, software inventories, signatures, test results, security reviews, deployment transactions and upgrade records can be distributed across Git hosting, CI systems, artifact stores, transparency services, explorers and attestation registries.

These systems solve important individual problems. The proposed research addresses a cross-system continuity and recovery question:

- Can an operator identify exactly which project state and evidence were associated with a release?
- Can the operator trace that release to its predecessor while retaining competing branches rather than silently selecting one?
- Can the evidence bytes be transferred and independently checked after the original CI or artifact service is unavailable?
- Can an Ethereum-native witness bind a compact checkpoint to a public chain history without putting source code or sensitive evidence on-chain?
- Can the result be independently reproduced without a BOD-operated service?

This is a technical problem statement, not a claim that existing tools fail to provide these capabilities. A comparative evaluation is a required deliverable.

## 3. Proposed system and boundaries

### 3.1 Core workflow

1. Capture a defined Git-tracked project boundary into a deterministic snapshot. Snapshot v0.2 commits to path, SHA-256 digest, byte size and Git-compatible file mode.
2. Create a versioned evidence envelope that binds the state root to typed evidence references and a predecessor state root.
3. Verify a linear history or a branch-aware graph. Forks remain visible; BOD does not select a canonical release head.
4. Package the checkpoint with the exact evidence payload bytes selected for portability.
5. Verify and extract the bundle in a fresh process using the reference verifier and a separately implemented verifier.
6. Delegate format-specific cryptographic checks to established tools such as sigstore-python rather than reimplementing their cryptography.
7. Optionally publish a compact commitment to an Ethereum L1 append-only registry and issue linked EAS attestations under a separately reviewed issuer policy.

### 3.2 Ethereum-specific release profile

The proposed profile is specified at design level in [Ethereum software release evidence profile](ETHEREUM_RELEASE_PROFILE.md); it is not yet implemented. It will define stable evidence types and relations for:

- source repository and immutable commit identity;
- compiler name/version, build settings and reproducible build inputs;
- compiled bytecode and ABI digests;
- unit, integration, fuzz and invariant test reports;
- static-analysis and formal-verification reports where available;
- audit reports and remediation references;
- Sourcify verification references or equivalent source/bytecode correspondence evidence;
- deployment transaction, chain ID and contract address;
- upgrade predecessor and successor references, including explicit missing-evidence gaps.

The profile will reference existing evidence formats and external records. It will not claim that a digest proves a report is correct, that source code is safe, or that an on-chain record establishes semantic truth.

### 3.3 Ethereum components

The repository includes a minimal Solidity checkpoint registry and EAS client scripts. They are source-level integrations only. No Sepolia or mainnet deployment, EAS schema registration, live attestation, or independent contract audit is claimed.

The registry is permissionless and append-only. It records compact commitments and predecessor references; it does not authenticate repository ownership or select a canonical branch. Any production authorization policy must be based on independently verified identities and signed evidence.

### 3.4 Explicit non-goals

- BOD token, ERC-20, staking, rewards, treasury or custom gas;
- BOD-operated blockchain, consensus network, L2, rollup or bridge;
- on-chain source code, build artifacts, SBOMs, logs, audit reports or personal data;
- replacement of established provenance, signing, SBOM or contract-verification standards;
- production-security or regulatory-compliance certification.

## 4. Current implementation evidence

The public repository currently contains:

- Python reference implementation and CLI for capture, verification, lineage and bundle operations;
- deterministic snapshots, versioned evidence envelopes and branch-aware graph verification;
- a self-contained evidence bundle format with strict payload digest and completeness checks;
- an independent verifier that does not import the BOD implementation;
- structural inspection for selected in-toto, SLSA, DSSE, CycloneDX and SPDX documents;
- delegated Sigstore verification using upstream tooling;
- a Solidity checkpoint registry with Foundry tests;
- EAS schema and attestation client scripts;
- Python regression tests, CI workflows and documented zero-cost test constraints.

Two public recovery exercises are recorded in [Verification Experiment](VERIFICATION_EXPERIMENT.md): one using GitHub Actions SBOM/Sigstore evidence and one using Reth v2.11.0 release assets. These are bounded demonstrations, not broad interoperability studies or proof of product superiority.

### Evidence and limitations register

| Area | Current evidence | Not established |
|---|---|---|
| Local core | Implemented and regression-tested | Independent production audit |
| Evidence bundle | Real payload recovery demonstrated | Large-scale or streaming performance |
| Sigstore | One offline verification scenario | Broad CI-provider coverage or continuously fresh trust metadata |
| Ethereum registry | Solidity source and tests | Deployed contract, finality operations or audit |
| EAS | SDK scripts and local checks | Registered schema or live attestations |
| Ethereum contract release profile | Proposed scope | Complete profile implementation |
| User value | Technical experiments | Independent users, pilots, demand or product-market fit |
| Comparative advantage | Competitor analysis documented | Reproducible side-by-side benchmark |

## 5. Work plan and milestones

The schedule below is a proposed scope for a future grant discussion, not a commitment that the current prototype already meets these outcomes. A final timeline and budget must be agreed with ESP and grounded in actual contributor capacity.

### Milestone 1 — Protocol correctness and portable evidence (weeks 1–4)

**Work**
- Complete snapshot v0.2 mode semantics and backwards-compatible v0.1 verification.
- Define the Ethereum release evidence profile, canonical field names, versioning and trust boundaries.
- Add adversarial tests for path normalization, symlinks, executable modes, missing evidence, malformed payloads and graph forks.
- Publish independent test vectors and a reproducible clean-environment setup.

**Acceptance**
- All documented snapshot and bundle invariants have positive and negative tests.
- The independent verifier accepts valid fixtures and rejects the same tampering cases as the reference verifier.
- The format specification and implementation agree on every serialized field.
- No wallet, paid RPC or hosted BOD service is required for core verification.

### Milestone 2 — Ethereum release evidence integration (weeks 5–8)

**Work**
- Implement a reference profile for one real, public Ethereum software or smart-contract release.
- Connect source commit, compiler/build inputs, test outputs, SBOM/provenance, security evidence and deployment/upgrade references.
- Define how Sourcify and EAS references are represented without duplicating their authoritative roles.
- Improve the Solidity registry and EAS scripts only where the profile demonstrates a concrete need.

**Acceptance**
- A public-safe fixture can be created and verified from a clean checkout.
- The profile preserves missing or unavailable evidence as explicit gaps rather than silently treating it as verified.
- Ethereum publication is optional; local verification works without an RPC endpoint.
- Any testnet rehearsal uses Sepolia, free public RPC/faucet resources and an explicitly authorized disposable wallet; no mainnet action or paid service.

### Milestone 3 — Comparative evaluation and independent reproduction (weeks 9–12)

**Work**
- Run the same release-recovery scenario against a documented baseline using Git, GitHub artifacts, SLSA/in-toto and Sigstore.
- Evaluate relevant evidence-management tools such as Chainloop, Kosli and Archivista, and metadata aggregation through GUAC where comparable.
- Measure operator steps, recovery time, evidence completeness, verification results, portability, external service dependencies and cost.
- Publish test fixtures, scripts, environment details, raw results and negative findings.

**Acceptance**
- At least two independent maintainers can reproduce the documented evaluation, if external participants are available.
- Comparisons use equivalent inputs and clearly identify features that cannot be compared fairly.
- No superiority claim is made unless supported by measured results.

### Milestone 4 — Security review, documentation and release decision (weeks 13–16)

**Work**
- Commission or obtain an independent review of protocol invariants and the Solidity contract before any deployment proposal.
- Triage findings and add regression tests for resolved issues.
- Publish deployment, key-management, finality, privacy, incident-response and recovery runbooks.
- Decide whether evidence supports a limited Sepolia pilot or whether the Ethereum witness should remain experimental.

**Acceptance**
- Review findings, severity, remediation status and residual risks are public.
- No unresolved critical/high finding is silently waived.
- Deployment is not treated as a milestone requirement if review or zero-cost conditions are not met.
- Final report includes completed work, deviations, costs and remaining limitations.

## 6. Evaluation metrics

The project will report measurements rather than adoption claims:

- checkpoint and evidence-bundle verification success/failure rates;
- percentage of referenced evidence payloads recovered from the portable bundle;
- number and type of missing evidence references;
- time and operator actions required for fresh-environment recovery;
- ability to detect altered bytes, missing predecessors, disconnected branches and forks;
- reproducibility across supported Python versions and independent machines;
- external services and credentials required by each workflow;
- local execution cost and any optional testnet gas usage;
- independent reviewer findings and reproducibility feedback.

The benchmark must include a baseline that uses existing tools without BOD. A result showing no material improvement is a valid outcome and may lead to narrowing or stopping the project.

## 7. Open-source and public-goods commitments

- MIT-licensed source code, specifications, fixtures, tests and reports.
- No proprietary hosted service is required to verify exported artifacts.
- No token or financial incentive is required to use the core.
- No private source or sensitive evidence is placed on-chain.
- Public issue tracking and documented design decisions.
- Reproducible test and benchmark instructions.
- Security limitations and negative results disclosed.

## 8. Risks and mitigations

| Risk | Mitigation |
|---|---|
| Existing tools already solve the use case adequately | Comparative benchmark is a mandatory early gate; stop or narrow if no material gap remains |
| Snapshot or lineage semantics omit important state | Versioned schemas, independent test vectors, adversarial tests and external review |
| Evidence bundle creates false confidence | Explicitly separate integrity, authenticity, semantic truth and availability |
| Permissionless registry is mistaken for authorization | Document publisher identity boundary; require external signed identity policy |
| Reorgs or RPC providers produce misleading observations | Record chain ID, transaction and block identifiers; use independent reads and finality policy |
| Evidence contains secrets or personal data | Off-chain payloads, pre-publication review, privacy guidance and minimal on-chain commitments |
| Contract vulnerability | No deployment before independent security review and remediation |
| Test infrastructure becomes costly | Local-first tests; zero-dollar cap; public free testnet services only; defer rather than pay |
| Demand is not demonstrated | User interviews and independent operator feedback are validation gates, not assumed outcomes |

## 9. Budget and payment approach

No funding amount is asserted in this pre-application brief. A credible request must be calculated from:
- named contributors and their actual responsibilities;
- milestone-level effort and realistic time allocation;
- independent review and testing costs, if any;
- any necessary travel or community participation, if justified;
- explicit zero-cost assumptions for local tests and public testnet work.

The proposal does not include token issuance, token incentives, paid RPC subscriptions or mainnet funds. ESP states that grants are paid on-chain in ETH by default; a recipient must be able to securely receive and manage ETH. Final grant scope and budget are determined with ESP, not assumed here.

## 10. Fit with Ethereum Foundation ESP

ESP describes its scope as open-source, non-commercial work that strengthens Ethereum and supports builders, aligned with CROPS: Censorship Resistance, Open Source, Privacy and Security. Its published selection criteria include technical approach, ecosystem impact, open source, budget, experience and alignment. ESP describes budget review as cost-effectiveness and appropriate allocation, and says it generally expects some flexibility below standard market rates because the support is non-dilutive.

BOD's strongest potential fit is builder tooling and security infrastructure for Ethereum release evidence. The application should not be framed as a generic blockchain, token, or commercial SaaS request.

As of the preparation date, ESP's public pages show no active Wishlist items, RFP items or open grant rounds. Office Hours are described as non-financial guidance, not a grant application or token consultation. This brief is therefore preparation material; it is not a submission to an active funding call and does not imply endorsement or eligibility.

## 11. Decisions required before a formal application

1. Identify a future active Wishlist item or RFP that directly matches the proposed deliverables.
2. Validate the Ethereum smart-contract release profile with independent maintainers.
3. Complete the current technical correctness fixes and obtain fresh CI results for the exact reviewed commit.
4. Produce a reproducible comparative benchmark.
5. Obtain independent protocol and contract review.
6. Define contributor capacity, named responsibilities and a defensible milestone budget.
7. Confirm the applicant's ability to complete ESP onboarding and securely receive ETH if selected.

## 12. Public references

- Ethereum Foundation ESP — Applicants and selection criteria: https://esp.ethereum.foundation/applicants
- ESP Wishlist: https://esp.ethereum.foundation/applicants/wishlist
- ESP RFPs: https://esp.ethereum.foundation/applicants/rfp
- ESP Open Rounds: https://esp.ethereum.foundation/applicants/open-rounds
- ESP Office Hours: https://esp.ethereum.foundation/applicants/office-hours
- ESP Allocation Update Q2 2026: https://blog.ethereum.org/2026/08/18/allocation-q2-26
- Ethereum Attestation Service: https://docs.attest.org/
- Sourcify documentation: https://docs.sourcify.dev/
- SLSA: https://slsa.dev/
- in-toto: https://in-toto.io/
- Sigstore: https://docs.sigstore.dev/
- CycloneDX: https://cyclonedx.org/
- SPDX: https://spdx.dev/
- Chainloop: https://github.com/chainloop-dev/chainloop
- Kosli: https://www.kosli.com/
- Archivista: https://github.com/in-toto/archivista
- GUAC: https://github.com/guacsec/guac
