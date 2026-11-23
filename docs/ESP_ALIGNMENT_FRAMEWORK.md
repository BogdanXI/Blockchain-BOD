# Ethereum Foundation ESP alignment framework

- **Document type:** public pre-application readiness framework
- **Assessment date:** 24 November 2026
- **Programme:** Ethereum Foundation Ecosystem Support Program (ESP)
- **Application status:** not submitted; no matching active opportunity identified
- **Authority:** the official ESP applicant guidance is controlling. This document is a project-side evidence map, not an EF template, endorsement, eligibility decision or prediction of funding.

## 1. How to use this framework

This document separates three things that must not be conflated:

1. **Official ESP guidance** — requirements and process stated by the Ethereum Foundation.
2. **BOD evidence** — what the repository can currently demonstrate, with limitations.
3. **Internal readiness gates** — additional proof we believe is needed to make a credible proposal. These are not represented as official EF criteria.

The ESP applicant page introduces its selection factors with the words “such as”. The six published factors below are therefore the explicit evaluation framework available to applicants, not a promise that EF uses only six factors, assigns equal weights, or applies a fixed scoring rubric. No numerical score is assigned here.

A criterion is not considered demonstrated merely because a document says it is true. Evidence must be inspectable and proportionate to the claim.

## 2. Official programme scope and application route

ESP describes its purpose as supporting eligible work that strengthens Ethereum's foundations and enables future builders. Its scope includes infrastructure, builder tools, research, cryptography, education and community development. Supported work is expected to be open-source, non-commercial in outcome, and aligned with CROPS: Censorship Resistance, Open Source, Privacy and Security.

The applicant guidance adds an important qualification: for-profit companies may apply, but the specific grant-funded work must be open-source and accessible to the community. The proposal must therefore identify the funded public deliverables and explain how they remain freely available; applicant legal form alone should not be treated as an automatic disqualifier.

### Application pathways

| Pathway | Official meaning | BOD status on 22 November 2026 |
|---|---|---|
| Wishlist | A stated ecosystem gap or opportunity; applicants propose an approach | No active Wishlist items |
| RFP | A focused, more prescriptive and time-bound problem with target outcomes | No active RFP items |
| Open Rounds | Time-limited funding round with its own theme, deadline and criteria | No active rounds |
| Office Hours | Non-financial guidance, project feedback and help understanding ecosystem fit | Available as a feedback route; not a grant application or project pitch |

**Consequence:** there is no currently listed Wishlist, RFP or open round to which BOD can honestly claim direct alignment. Do not submit a generic application as though a relevant call were open. Recheck the official pages before any submission.

Office Hours are described as an informal 20-minute call for non-financial support. The ESP explicitly says they are not an application for financial support and not an opportunity to pitch. If used, the request should ask focused questions about project fit, ecosystem context or how to refine the work.

### Payment and applicant-readiness implications

The applicant page states that approved grants are paid on-chain in ETH by default. Recipients must complete onboarding, including identity verification and a formal grant letter. Limited exceptions may be considered where legal or operational constraints prevent ETH receipt.

Before any application, the applicant must personally confirm the ability and willingness to complete onboarding and securely receive/manage ETH, or establish whether a documented exception is relevant. This is an unresolved applicant-side gate, not a technical feature requirement. No wallet action or transaction is authorized by this framework.

## 3. The six published selection factors

The descriptions below track the official ESP applicant page. The BOD assessment is a candid project-side reading, not an EF evaluation.

| Published factor | What the proposal must establish | Current BOD evidence | Current assessment | Evidence still needed |
|---|---|---|---|---|
| **Technical approach** | Soundness, feasibility and clarity of methodology and implementation plan | Working Python prototype; deterministic snapshots; predecessor-linked continuity; portable evidence bundles; independent verifier; Solidity registry source/tests; experimental Ethereum release profile; Reth client fixture; WETH9 mainnet deployment fixture with 12 explicit gaps; CI | **Partially demonstrated.** Deployment facts and Sourcify compiler/source metadata are captured, and two selected evidence payloads were recovered from a temporary BOD bundle; exact source revision, historical runtime bytecode and original build provenance remain unresolved; independent review is incomplete | Resolve source-to-deployment lineage or characterize the mismatch; add a second traceable contract/upgrade fixture; clean-room reproduction; adversarial tests; independent review; comparative benchmark |
| **Ecosystem impact** | Potential benefit to Ethereum and alignment with ecosystem priorities | Proposed use for Ethereum client, infrastructure and smart-contract release evidence | **Not independently demonstrated.** Target users and benefit remain hypotheses | Interviews or structured feedback from Ethereum maintainers/builders; documented workflow pain; measurable impact and adoption/reproduction evidence |
| **Open source** | Outputs open-source or otherwise freely available; grant-funded work accessible to community | Public MIT-licensed repository, specifications, tests and implementation | **Strong structural fit, subject to scope confirmation.** Confirm all funded outputs, dependencies, assets and contributions can be published under compatible terms | Deliverable-level licensing plan; third-party license review; contributor/IP authority; public issue/milestone and release plan |
| **Budget** | Cost-effectiveness and appropriate allocation; ESP notes flexibility below standard market rates for non-dilutive support | Local-first design and zero-cost testing constraints; no paid RPC or hosted BOD service required for core validation | **Not demonstrated.** No costed grant budget or effort estimate exists | Work-package estimates, contributor rates/effort, infrastructure costs, milestone payment schedule and explanation of cost-effectiveness |
| **Experience** | Relevant background, skills and prior work demonstrating capability | Public code, passing CI, test suite and bounded recovery experiments | **Partially evidenced by artifacts; applicant capability is not assessable from repository alone** | Accurate applicant profile, relevant prior work, role allocation, time availability, references or contribution history where available; no invented credentials |
| **Alignment** | Understanding of Ethereum values and ecosystem needs, and contribution to them | Optional Ethereum L1 witness and EAS integration; Ethereum-specific release profile; CROPS commitments | **Partial.** Ethereum integration is optional and much of the core also serves general software supply chains | Specific Ethereum builder workflow, clear reason Ethereum-native components matter, evidence of ecosystem need, and exact match to a future Wishlist/RFP |

## 4. CROPS: project commitments versus evidence

CROPS is part of ESP's stated mission and scope. The following is a self-assessment, not an EF certification.

| Principle | BOD commitment | Evidence currently available | Remaining proof |
|---|---|---|---|
| Censorship Resistance | Core capture and verification do not require a BOD-operated service; Ethereum is optional | Local verification and portable bundles; permissionless registry design | Demonstrate retrieval and verification with original Git host, artifact store, indexer or one RPC provider unavailable |
| Open Source | Protocol, core, verifier, tests and grant-funded outputs remain publicly available | MIT license and public repository | Confirm rights and compatible licensing for every funded contribution and dependency |
| Privacy | Evidence payloads, source, secrets and personal data stay off-chain | Commitment-only registry design and privacy documentation | Test metadata leakage, capture exclusions and operational handling |
| Security | Minimize trusted code; document boundaries; enable independent verification | Threat model, regression tests, independent verifier, CI and Solidity tests | Independent review, findings remediation, fuzz/invariant evidence and incident-response readiness |

A passing test suite is not a security audit. A digest proves byte identity relative to the digest; it does not prove semantic truth, authorization, build safety, source/bytecode correctness or evidence completeness.

## 5. Ethereum-specific value hypothesis

**Current hypothesis:** BOD may help Ethereum software and smart-contract teams preserve and independently recover a predecessor-linked history of release evidence across source revisions, builds, tests, audits, source/bytecode verification, deployments and upgrades.

The hypothesis is narrower than “blockchain-based software supply-chain security”. BOD should compose with established tools and must not claim to replace them.

Potential target users to validate:

- Ethereum execution and consensus client maintainers;
- smart-contract and protocol teams managing deployments and upgrades;
- Ethereum infrastructure and developer-tooling maintainers;
- security reviewers who need to reconstruct evidence for a historical release.

These are target segments, not confirmed users or customers.

The Ethereum-specific case must answer:

1. What workflow fails or becomes materially harder without BOD?
2. Which existing tools already solve parts of that workflow?
3. What continuity or recovery gap remains after combining those tools?
4. Why is an Ethereum-native witness useful, and when is it unnecessary?
5. What measurable operator outcome improves?
6. Can another team reproduce the result without BOD-operated infrastructure?

## 6. Competitive and ecosystem evidence

The comparison must include relevant products and composable baselines, not only conceptual standards:

- Chainloop, Kosli, Archivista and GUAC;
- Git tags/signed commits and ordinary release archives;
- SLSA/in-toto provenance, Sigstore/Rekor and GitHub artifact attestations;
- SPDX/CycloneDX SBOM workflows;
- Sourcify and EAS for Ethereum-specific source verification and attestations.

The current competitive landscape document is a research map, not proof of superiority. The required experiment must run the same release-recovery task with and without BOD, disclose configuration and operator steps, and publish negative results. Useful measures include evidence recovery completeness, time, manual steps, missing context, tamper detection, portability, dependencies, storage and optional gas costs.

ESP's Q2 2026 allocation update includes developer-tooling and infrastructure examples such as Web3j, ETHeorem and mevlog-rs. This confirms that developer tooling appears among supported outputs; it does **not** establish that BOD fits a current priority or predicts a grant decision.

## 7. Internal readiness gates before an application

These gates are project due diligence, not additional official ESP criteria.

| Gate | Pass condition | Current state |
|---|---|---|
| G0 — Opportunity match | A live Wishlist/RFP/open round exists and the proposed scope maps to its stated requirements | **Blocked:** no active item listed on 24 November 2026 |
| G1 — Problem validation | Specific Ethereum users confirm the workflow and its significance; feedback is documented | **Open:** no independently documented user validation |
| G2 — Ethereum case | At least one public contract lifecycle fixture is reproducible end-to-end, with explicit gaps and trust boundaries | **Partially advanced, not passed:** WETH9 deployment, block, compiler metadata and Sourcify metadata are recorded, but the match classification was not retained; two selected payloads passed temporary bundle recovery; exact source commit, historical runtime bytecode and full build/test/audit lineage remain unresolved |
| G3 — Comparative result | Reproducible head-to-head baseline test shows where BOD helps, where it does not, and operational cost | **Partially advanced, not passed:** one WETH9 payload-size/recovery comparison against tar.gz exists; tar.gz was smaller by 44.5% in that sample; no multi-release lineage or competing-platform benchmark |
| G4 — Independent reproduction | An external operator can reproduce the documented procedure without project-maintainer intervention | **Open:** not yet demonstrated |
| G5 — Security confidence | Independent review findings are recorded and critical/high issues resolved before any production/deployment claim | **Open:** no independent audit/review |
| G6 — Execution and budget | Applicant roles, capacity, work packages, milestones, acceptance criteria and budget are realistic and documented | **Open:** not costed; applicant capacity needs confirmation |
| G7 — Applicant/payment readiness | Applicant eligibility, rights, onboarding and ability to receive/manage ETH (or basis for exception) are confirmed | **Open:** applicant-side facts not yet confirmed |

Do not treat all gates as equally blocking at every stage. G0 blocks a direct application while no matching opportunity exists. G1–G6 determine whether BOD has a credible project and proposal when a match appears. G7 must be resolved by the actual applicant before accepting funding.

## 8. Evidence register and repository pointers

| Claim | Public evidence | What it proves — and does not prove |
|---|---|---|
| Core implementation exists | [README](../README.md), [Project status](PROJECT_STATUS.md) | Prototype and documented boundaries; not production readiness |
| Portable recovery was exercised | [Verification experiment](VERIFICATION_EXPERIMENT.md) | Two bounded recovery scenarios; not broad interoperability or market demand |
| Ethereum release profile exists | [Profile specification](ETHEREUM_RELEASE_PROFILE.md), [Reth fixture](../examples/ethereum-release-profile/reth-v2.11.0.json), [WETH9 fixture](../examples/ethereum-release-profile/weth9-mainnet-2017-12-12.json), [contract fixture report](ETHEREUM_CONTRACT_FIXTURE.md) | Experimental client-release and partial contract-deployment records; WETH9 has 12 explicit gaps and is not a complete lifecycle reproduction |
| Competitive analysis exists | [Competitive landscape](COMPETITIVE_LANDSCAPE.md) | Identified products and test design; not superiority |
| User need remains unvalidated | [Market fit](MARKET_FIT.md) | Public problem hypothesis and validation plan; not confirmed demand |
| CROPS commitments exist | [CROPS alignment](CROPS_COMPLIANCE.md) | Project policy and self-assessment; not EF certification |
| Technical proposal exists | [Grant technical brief](GRANT_TECHNICAL_BRIEF.md) | Proposed work packages and evaluation plan; not an approved scope or costed offer |

## 9. Decision rules and integrity constraints

- Do not claim an active EF call, direct Wishlist/RFP alignment, eligibility, endorsement or funding likelihood without current official evidence.
- Do not treat examples in the funded-project database as proof of BOD fit.
- Do not claim user demand, adoption, pilots, partners or endorsements without attributable evidence.
- Do not claim superiority until the comparative experiment is complete and reproducible.
- Do not call a source-code fixture a deployed contract, or local tests an audit.
- Do not describe BOD as CRA compliance, a security certification or a replacement for established standards.
- Keep token, L2, bridge, rollup and proprietary-chain concepts outside the active proposal.
- Keep development and testing at USD 0 where possible; no paid RPC/API, purchased test ETH, wallet signing, schema registration or deployment without separate authorization.
- Do not submit, contact EF, book Office Hours or make external commitments without the applicant's explicit approval.
- Reassess the official ESP pages before relying on this dated snapshot.

## 10. Official sources

All programme status statements above were checked against these official pages on 24 November 2026:

- [ESP applicants: scope, process, selection factors and FAQ](https://esp.ethereum.foundation/applicants)
- [ESP About](https://esp.ethereum.foundation/about)
- [Wishlist applications](https://esp.ethereum.foundation/applicants/wishlist)
- [Request for Proposals](https://esp.ethereum.foundation/applicants/rfp)
- [Open Rounds](https://esp.ethereum.foundation/applicants/open-rounds)
- [Office Hours](https://esp.ethereum.foundation/applicants/office-hours)
- [Funded Projects](https://esp.ethereum.foundation/funded-projects)
- [Allocation Update — Q2 2026](https://blog.ethereum.org/2026/08/18/allocation-q2-26)

## 11. Review history

- 2026-11-22 — Initial framework created from a live review of official ESP applicant, scope, Wishlist, RFP, Open Rounds, Office Hours and funded-project pages.
- 2026-11-24 — Rechecked live Wishlist, RFP, Open Rounds and Office Hours pages; updated G2 after capturing the WETH9 mainnet deployment fixture and its unresolved source/build/runtime evidence gaps.
