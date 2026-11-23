# Grant readiness assessment

**Assessment date:** 24 November 2026

**Target programme:** Ethereum Foundation Ecosystem Support Program (ESP)  
**Status:** pre-application preparation; not submitted

## Executive assessment

BOD has a credible experimental engineering base and a plausible builder-tooling/security-infrastructure angle for Ethereum. It is not yet grant-ready as a funding application. The largest gaps are a precise match to an active ESP Wishlist/RFP, independent user validation, a reproducible comparative benchmark, current-head remote CI evidence, and independent review of the Ethereum contract.

**Important programme status:** ESP's public Applicants pages currently show no active Wishlist items, no active RFP items and no active open rounds. Office Hours remain a non-financial feedback channel. This repository can be prepared for a future matching opportunity, but there is no current open call to which this project can honestly claim alignment.

## 1. Current ESP fit

ESP describes support for work that strengthens Ethereum and enables builders, with open-source outputs aligned with CROPS: Censorship Resistance, Open Source, Privacy and Security. Its applicant guidance says for-profit companies may apply, but the specific grant-funded work must be open-source and accessible to the community. The published selection factors are technical approach, ecosystem impact, open source, budget, experience and alignment; the page introduces them as factors “such as”, so they should not be treated as an exhaustive or weighted scoring rubric. See the [ESP alignment framework](ESP_ALIGNMENT_FRAMEWORK.md) for the criterion-by-criterion evidence map.

| ESP criterion | BOD evidence | Assessment |
|---|---|---|
| Technical approach | Working Python prototype, portable bundles, independent verifier, Solidity registry source and tests | Promising, but protocol and contract review remain incomplete |
| Ecosystem impact | Potential release-evidence continuity for Ethereum software and smart-contract teams | Plausible; user value has not been independently demonstrated |
| Open source | MIT-licensed public repository, public specifications and tests | Strong structural fit |
| Budget | Local-first test plan; no paid RPC, token or hosted service requirement | Cost-conscious; grant budget not yet costed. ESP says it generally expects flexibility below standard market rates for non-dilutive support |
| Experience | Public code, test suite and bounded recovery experiments | Evidence of implementation; contributor capacity and relevant track record need to be presented accurately |
| Alignment | Optional Ethereum L1 registry and EAS integration | Moderate; generic supply-chain tooling alone is not sufficient evidence of Ethereum-specific impact |

## 2. Readiness by workstream

| Workstream | Current state | Gap before a strong application |
|---|---|---|
| Core continuity | Implemented prototype; snapshot v0.2 and legacy v0.1 verification pass | Repeat across independent projects and baseline toolchains |
| Evidence portability | One GitHub/Sigstore scenario and one Reth release recovery scenario documented | Repeat across independent projects and baseline toolchains |
| Ethereum contract | Solidity source/tests; WETH9 mainnet deployment record, compiler metadata and Sourcify compiler/source metadata captured in a public fixture; match classification not retained | Exact source commit, historical runtime code, original build provenance and full lifecycle still unresolved; independent review not done |
| EAS | SDK scripts and local smoke checks | Schema not registered; no live attestation; issuer policy needs independent review |
| Ethereum release profile | Experimental JSON Schema, structural validator, CLI, Reth client fixture and partial WETH9 mainnet deployment fixture | Resolve exact source lineage; add complete build/test/audit/bytecode/upgrade evidence and native verification |
| Interoperability | Structural inspection and delegated Sigstore verification | Broader real fixtures and format-specific verifiers |
| Competitive differentiation | Competitor landscape documented | Reproducible side-by-side benchmark against Git + SLSA/in-toto + Sigstore and relevant evidence tools |
| User demand | No independently documented users, pilots or expressed team interest | Interviews, design-partner feedback or reproducible operator evaluations |
| Security | Threat model and automated tests | Independent protocol and Solidity review; resolve critical/high findings |
| Grant proposal | Technical brief prepared | Match an active Wishlist/RFP, cost milestones, establish contributor roles and confirm applicant details |

## 3. Current technical evidence

The repository contains real, bounded experiments:
- GitHub Actions-generated CycloneDX SBOM and Sigstore bundle were packaged, recovered and checked offline under the documented trust-root conditions.
- A Reth v2.11.0 release archive and associated release evidence were recovered from a BOD bundle and independently checked with GPG.
- A WETH9 mainnet deployment fixture captures transaction/block facts, compiler metadata and Sourcify compiler/source metadata (match classification not retained); a temporary BOD bundle containing two selected evidence payloads passed both BOD and separate independent verification after original payload deletion and extraction.
- Python regression tests, Ruff, public-surface validation, CLI smoke checks, JSON Schema validation and npm production dependency audit have passed locally in the current working environment.

These results do not constitute:
- a production security audit;
- proof that BOD is superior to Chainloop, Kosli, Archivista or existing Git/SLSA/Sigstore workflows;
- a deployed Ethereum contract or registered EAS schema;
- independent user adoption or product-market fit;
- an independently reproduced multi-project benchmark.

GitHub Actions run [45050151175](https://github.com/BogdanXI/Blockchain-BOD/actions/runs/45050151175) passed on the exact reviewed code commit bcfdc7f25a619f96bffe9709f506fb0f531e28cd across Python 3.11, 3.12, 3.13, Foundry Solidity tests and EAS tooling. Foundry is not installed locally, but the remote Solidity job passed. Any subsequent source or workflow changes require another run.

## 4. Recommended grant framing

Use the title:

**Portable, Independently Verifiable Release Continuity for Ethereum Software**

Focus on a specific, measurable builder need: preserving and independently recovering the evidence chain across Ethereum software releases and smart-contract upgrades. Keep the generic portable core as the reusable foundation, but make the funded deliverable explicitly useful to Ethereum builders.

Do not frame the request as:
- building a new blockchain;
- launching a BOD token;
- creating an L2 or bridge;
- replacing EAS, Sourcify, Sigstore or SLSA;
- providing regulatory compliance certification;
- a production-ready security product.

The accompanying [Grant Technical Brief](GRANT_TECHNICAL_BRIEF.md) contains the proposed architecture, milestones, acceptance criteria, evaluation metrics, risks and budget assumptions. The supporting [Ethereum Release Profile](ETHEREUM_RELEASE_PROFILE.md) and [WETH9 contract fixture report](ETHEREUM_CONTRACT_FIXTURE.md) make the current data model, captured deployment facts and unresolved trust boundaries explicit.

## 5. Critical gaps, ordered by importance

1. **Active programme fit:** wait for a relevant ESP Wishlist item or RFP; use Office Hours only for non-financial project feedback.
2. **Ethereum-specific validation:** resolve the WETH9 source-revision mismatch or explicitly bound the use case; add a second contract fixture with traceable source/build history and an upgrade path.
3. **Comparative evidence:** benchmark the same workflow against a baseline without BOD and publish all methods and results.
4. **Technical correctness:** review the snapshot v0.2 file-mode correction, independent verifier compatibility and adversarial regression tests on the exact current commit.
5. **Security review:** obtain independent review of the registry, EAS trust model and off-chain evidence semantics before any deployment.
6. **Execution credibility:** establish actual contributor capacity, responsibilities, milestone timing and a costed budget.
7. **Independent demand:** seek feedback from Ethereum maintainers and smart-contract teams; do not claim demand until documented.

## 6. Non-negotiable integrity rules

- No invented users, partners, pilot results, endorsements or demand.
- No claim of a grant award, active application round or guaranteed eligibility.
- No claim that a local test is a deployed-chain test or security audit.
- No tokenomics in the active proposal; legacy token/economics files are historical research only.
- Keep all core testing and development at USD 0 where possible. Do not purchase test ETH or use paid RPC/API services.
- Do not register an EAS schema, deploy a contract, sign a transaction or use a wallet without separate explicit authorization.
- Keep public claims synchronized with the exact code and test results on the reviewed commit.

## 7. Official ESP sources checked on 24 November 2026

- Applicants, scope, selection criteria and process: https://esp.ethereum.foundation/applicants
- Wishlist: https://esp.ethereum.foundation/applicants/wishlist
- RFPs: https://esp.ethereum.foundation/applicants/rfp
- Open rounds: https://esp.ethereum.foundation/applicants/open-rounds
- Office Hours: https://esp.ethereum.foundation/applicants/office-hours
- ESP Q2 2026 allocation update: https://blog.ethereum.org/2026/08/18/allocation-q2-26

ESP states that approved grants are paid on-chain in ETH by default; recipients complete onboarding, including identity verification and a formal grant letter. Limited exceptions may be considered for legal or operational constraints. The applicant must confirm their ability to securely receive and manage ETH before accepting a grant. Office Hours are non-financial guidance, not a grant application or pitch opportunity, and do not provide advice on creating, structuring or launching a token.
