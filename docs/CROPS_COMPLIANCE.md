# CROPS alignment and project commitments

**Scope:** BOD Evidence Fabric, public repository and work proposed for external support.  
**Status:** self-assessment; not an Ethereum Foundation certification or endorsement.  
**Last reviewed:** 2026-11-22.

This document maps the project to the Ethereum Foundation's published mandate. It distinguishes project commitments from technical evidence and from principles that guide the Foundation internally. It must not be read as a claim that EF has approved BOD.

Primary source: [Ethereum Foundation Mandate](https://ethereum.foundation/ef-mandate.pdf). CROPS means censorship resistance, open source, privacy and security.

## Summary

| Principle | Project commitment | Current evidence | Remaining work |
|---|---|---|---|
| Censorship resistance | No mandatory BOD-operated service, privileged publisher, admin key or kill switch in the core verification path | Local verification works without a wallet or RPC; Ethereum registry is permissionless and has no owner or upgrade key | Test recovery and verification with Git hosting, RPC and indexing services unavailable; document alternate data paths |
| Open source | Core protocol, reference implementation, verifier, specifications, tests and grant-funded deliverables remain MIT-licensed and publicly auditable | Public repository includes MIT LICENSE | Preserve license notices and third-party attribution; review every new dependency and contribution |
| Privacy | Keep source, evidence payloads, secrets and personal data off-chain; publish only necessary commitments | Contract stores fixed-size commitments; quickstart warns against capturing secrets | Complete privacy tests, metadata analysis, data-retention guidance and documented capture exclusions |
| Security | Minimize trusted code, expose limitations, support independent verification and invite external review | Python verifier, Solidity tests, CI and threat model exist | Independent review/audit, fuzzing, invariants, reproducible dependencies, supply-chain attestations and incident-response improvements |

## Open-source and license commitment

For the BOD core and any work funded as a public BOD deliverable:

1. The project uses the MIT License.
2. The maintainers intend to keep the core protocol, reference implementation, independent verifier, specifications, tests and documentation under MIT.
3. The project will not relicense those core components as proprietary or source-available-only software.
4. Contributions accepted into the core must be compatible with the MIT License and retain required third-party notices.
5. Any separately operated commercial service or integration work must not be required to obtain the core protocol, run the verifier, inspect the specifications or use grant-funded public deliverables.

This is a project policy statement, not legal advice. Before a grant agreement is signed, the applicant must confirm that they have the rights and authority to make these commitments for all relevant contributions.

## Censorship resistance and exit paths

The core local verification path must remain usable without a BOD account, hosted BOD API, BOD-operated indexer, wallet connection or single RPC provider. Ethereum is an optional public witness, not a mandatory coordinator.

The Ethereum registry has no owner, privileged publisher, upgrade key, token gate or mutable canonical-head pointer. Publication is permissionless and forks remain visible. These properties do not prevent censorship by an RPC provider, frontend, hosting platform or chain-level validator set.

Required validation before claiming operational independence:

- retrieve contract state and events from two independently operated RPC endpoints;
- verify the contract address, chain ID, block hash, receipt and finality policy;
- retrieve portable checkpoints and evidence from more than one independently controlled location;
- run the verifier in a clean environment without the original repository host or BOD services;
- document how a user can switch RPC, hosting and storage providers.

## Privacy and data minimization

BOD does not put source files, build outputs, evidence payloads, credentials, private keys or personal data on-chain. Hashes and metadata can still leak information through correlation, timing, identifiers or low-entropy values. See [Privacy Model](PRIVACY_MODEL.md).

The project will not describe hashing as anonymization or claim that a commitment is inherently private.

## Security and verifiability

Security claims are limited to predicates actually checked by code. A passing test suite is not an audit. A digest is not proof of semantic truth, signer authorization, build integrity or artifact availability.

The project will publish known limitations, invite independent review, track security findings and avoid production-security claims until supported by external evidence. See [Threat Model](THREAT_MODEL_v0.1.md) and [Security Policy](../SECURITY.md).

## Public work and accountability

Work proposed for external support will be tracked through public issues, milestones, code, test results and release notes. Material design decisions and negative test results will be documented. Any security-sensitive disclosure will follow the security policy until coordinated disclosure is complete.

## Independence and sustainability

The core verifier and protocol must not depend on a proprietary BOD service. The project will document how maintainers and users can continue operating, forking and verifying the system if the original maintainer, grantor, hosting provider or any one vendor exits.

No grant amount, user demand, partnership or future revenue is claimed in this document.
