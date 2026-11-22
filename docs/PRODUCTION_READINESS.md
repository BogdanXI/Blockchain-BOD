# Production-readiness plan

**Current release classification:** experimental engineering prototype (alpha).
**Production status:** not production-ready.
**Mainnet status:** not authorized or planned as part of the current test phase.

This document defines the evidence required before describing BOD as production-ready. Passing CI is necessary but is not a production security assessment.

## Release gates

| Gate | Required evidence | Current status |
|---|---|---|
| Product scope | Stable scope, supported workflows, explicit non-goals and compatibility policy | In progress; v0.1 scope is documented |
| Core correctness | Clean-checkout tests, deterministic vectors, negative tests and independent verifier | Local/CI tests exist; independent external implementation not demonstrated |
| Protocol specification | Versioned schemas, canonical encoding, migration and compatibility rules | Partial; protocol v0.1 requires external review |
| Ethereum contract | Independent review, invariant/fuzz coverage, compiler/build reproducibility and verified Sepolia deployment | Blocked; source and local tests exist, no deployment or audit |
| EAS interoperability | Live schema registration, genesis/child attestations, independent readback and failure/reorg handling | Blocked; client code and smoke checks exist, no live flow |
| Supply-chain interoperability | Verified SLSA/in-toto provenance, SPDX/CycloneDX SBOM and Sigstore bundles from external workflows | Partial; CI produces SBOMs and artifact attestations for this repository; product adapters remain unfinished |
| Privacy | Data-flow review, metadata leakage analysis, payload allowlists, retention and deletion guidance | Policy and automated checks exist; external review and broader tests remain |
| Dependency security | Pinned/locked dependencies, vulnerability review, update policy and SBOM per release | Python hash lock and npm lock exist; CI audit is present; ongoing maintenance required |
| Build provenance | Reproducible release process, signed/attested artifacts and consumer verification instructions | CI workflow exists; public tagged release still needs end-to-end rehearsal |
| Operations | Incident response, key custody, monitoring, recovery, backup and deprecation procedures | Documentation incomplete; no production operator service is claimed |
| Independent validation | At least two external teams reproduce the workflow and publish measured results | Not started / no public pilot evidence |
| Governance and maintenance | Named maintainers, response expectations, contribution/release process and continuity plan | Public policies exist; maintenance capacity and external maintainers not yet established |

## Zero-cost testing constraint

Development and pre-production testing must remain within a **USD 0 test budget**:

- local Python and Foundry tests first;
- public Ethereum Sepolia RPC endpoints or self-hosted nodes;
- public testnet faucets only;
- free CI allowances and open-source tooling;
- no paid RPC/API subscriptions, paid test ETH, mainnet transactions or production credentials.

If a free resource is unavailable, the affected live test is deferred. No paid fallback is permitted without a separate explicit decision. Testnet ETH has no intended monetary value and is not a substitute for production funding.

## Promotion sequence

1. Freeze and review the v0.1 specification and threat model.
2. Complete local regression, fuzz, dependency and reproducibility checks from a clean clone.
3. Obtain an independent review of the contract and protocol; resolve critical/high findings.
4. Rehearse Sepolia deployment using a dedicated test-only wallet and free test ETH; verify source and bytecode independently.
5. Complete EAS registration, genesis/child attestations and independent readback on Sepolia.
6. Complete a real release-evidence workflow using externally generated provenance, SBOM and signature bundles.
7. Run comparative recovery pilots with independent maintainers and publish all results, including failures.
8. Define operational support, incident handling, upgrade/deprecation policy and maintenance ownership.
9. Only then decide whether a limited production release is justified. Mainnet requires a separate security, privacy, cost and operational approval.

## Release language

Until the gates are met, use “experimental prototype”, “testnet preparation” and “proposed workflow”. Do not use “production-ready”, “audited”, “secure by design”, “Ethereum-approved”, “market-validated” or “decentralized network” as achieved claims.
