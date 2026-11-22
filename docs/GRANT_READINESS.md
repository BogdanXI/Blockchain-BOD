# Ethereum Ecosystem Support Program — Grant Readiness

**Status:** preparation document; not a submitted application.  
**Project:** BOD Evidence Fabric.  
**Repository:** https://github.com/BogdanXI/Blockchain-BOD  
**Reviewed:** 2026-11-22.

## 1. Purpose

This document prepares a truthful project-feedback request and a potential ESP application. It is not an assertion of eligibility, endorsement, funding, market demand or completed technical work.

Official starting points:
- [ESP applicants](https://esp.ethereum.foundation/applicants)
- [ESP wishlist](https://esp.ethereum.foundation/applicants/wishlist)
- [ESP RFPs](https://esp.ethereum.foundation/applicants/rfp)
- [ESP Office Hours / Project Feedback](https://esp.ethereum.foundation/applicants/office-hours/apply)
- [Ethereum Foundation Mandate](https://ethereum.foundation/ef-mandate.pdf)

Availability of funding rounds and wishlist topics changes. Re-check official pages immediately before applying.

## 2. Proposed project statement

BOD is an open-source, independently verifiable continuity layer for software release evidence. It binds successive software states to portable checkpoints and can use Ethereum and EAS as optional public witnesses. It is designed to complement, not replace, Git, SLSA, in-toto, Sigstore, SPDX, CycloneDX or EAS.

The proposed Ethereum ecosystem contribution is a reusable way for protocol and infrastructure teams to preserve and independently verify the continuity of release evidence across CI systems, repositories and storage providers.

This ecosystem benefit remains a hypothesis until independent Ethereum teams validate it.

## 3. Why Ethereum ecosystem support may be relevant

Potential beneficiaries include maintainers of Ethereum execution and consensus clients, smart-contract frameworks, wallet infrastructure, security tooling and critical developer libraries.

The project must demonstrate a concrete use case with at least one real Ethereum software release workflow. Generic claims that Ethereum is decentralized or that BOD uses EAS are insufficient.

## 4. Current implementation — verified scope

- Portable BOD checkpoint and local independent verification: implemented in the public branch.
- Ethereum checkpoint registry source and Foundry unit tests: implemented; no deployment claimed.
- EAS SDK schema-registration and attestation clients: implemented; no schema registration or live attestation claimed.
- Python CI matrix, static analysis and public-surface validation: present.
- SLSA/in-toto ingestion, SPDX/CycloneDX ingestion and Sigstore/Rekor verification: not implemented as end-to-end product integrations.
- Independent smart-contract audit, formal verification and external product pilots: not completed.

See [Project Status](PROJECT_STATUS.md), [Ethereum Integration](ETHEREUM_INTEGRATION.md), [EAS Integration](EAS_INTEGRATION.md) and [Threat Model](THREAT_MODEL_v0.1.md).

## 5. Proposed work packages

The following are candidate milestones. Dates and costs must be estimated from actual scope and applicant availability before submission.

| Work package | Deliverables | Acceptance evidence |
|---|---|---|
| WP1 — Specification and privacy | Versioned data model, CROPS mapping, privacy review, threat-model update | Public specifications, reviewed data-flow diagrams, automated privacy tests |
| WP2 — Ethereum/EAS testnet | Sepolia registry deployment, schema registration, genesis and child attestations, independent reader | Transaction IDs, contract verification, schema UID, reproducible test instructions |
| WP3 — Supply-chain interoperability | SLSA/in-toto provenance, SPDX/CycloneDX SBOM and Sigstore verification adapters | Reproducible CI example and independent verification results |
| WP4 — Security engineering | Fuzz and invariant tests, dependency pinning, independent contract review, remediation | Public test corpus, review report and resolved findings |
| WP5 — Ecosystem pilot | Pilot with independent Ethereum software maintainers | Published methodology, anonymized or approved results, limitations and user feedback |
| WP6 — Documentation and handover | Operator guide, verifier guide, release, maintenance and exit plan | Public release, docs, reproducible build and handover checklist |

A mainnet deployment is not assumed or included in these work packages. It would require a separate decision and review.

## 6. Metrics to define before applying

Do not invent target numbers before establishing a baseline. The applicant should define and measure:

- time required for an independent party to verify a release checkpoint;
- percentage of evidence references that can be retrieved and verified from a fresh environment;
- number of independent implementations or teams able to verify the same checkpoint;
- number of supported provenance/SBOM formats with passing interoperability vectors;
- recovery success after removing access to the original Git host, CI provider or RPC endpoint;
- critical/high security findings opened, fixed and independently retested;
- pilot teams and documented user feedback.

## 7. Budget template

No grant amount is asserted here. Prepare a transparent budget based on work packages and realistic effort.

| Cost category | Basis to document |
|---|---|
| Applicant engineering time | Role, hours, rate, work package and deliverable |
| Independent security review | Scope, provider quote, audit assumptions and remediation window |
| Test infrastructure | RPC, CI, storage and testnet costs; distinguish recurring from one-off |
| Ecosystem pilot support | Integration effort and participant consent |
| Documentation and maintenance | Deliverables, support period and handover |
| Contingency | Explicit assumptions and cap |

Exclude speculative token value, token issuance, staking rewards and unsubstantiated future revenue. State any co-funding or in-kind contribution accurately.

## 8. Applicant information still required

The applicant must supply truthful details; do not fabricate or infer them:

- applicant legal name and country of residence/entity;
- individual or organization profile;
- relevant engineering and security experience;
- prior public work and references;
- available time and delivery capacity;
- intended grant recipient wallet and operational custody plan, if requested by ESP;
- conflicts of interest and other funding;
- whether this project or applicant has applied to EF/ESP before.

## 9. Risks and mitigations

| Risk | Mitigation |
|---|---|
| Weak direct Ethereum ecosystem fit | Secure feedback from Ethereum client/tooling maintainers and run a real pilot |
| Overclaiming maturity | Publish explicit implementation status and non-claims |
| Evidence availability | Use multiple independent storage locations and retrieval tests |
| Metadata privacy leakage | Apply the Privacy Model and automated payload checks |
| Smart-contract vulnerabilities | Independent review, fuzzing, invariant tests and no mainnet deployment before gate |
| Maintainer dependency | Open specifications, public issue tracking, reproducible builds and handover |
| Scope expansion | Fixed milestones, acceptance criteria and explicit out-of-scope items |

## 10. Immediate application route

Use the ESP Office Hours form and select **Project Feedback** to ask whether the project fits ESP priorities. Provide the public repository, this readiness document, a concise summary and a specific question about the Ethereum ecosystem use case.

Do not present this preparation document as an approved grant proposal. Confirm the current application process and requirements with ESP before submission.
