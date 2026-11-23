# Ethereum software release evidence profile

**Document status:** experimental v0.1 profile with a published JSON Schema and local structural validator; not a stable standard or deployed integration

**Profile identifier:** bod-ethereum-release-profile-v0.1

**Prepared:** 24 November 2026

**Depends on:** BOD Evidence Envelope v0.1 and Evidence Bundle v0.1

**Scope:** Ethereum execution/consensus clients, developer tooling and smart-contract releases/upgrades

## 1. Purpose

This profile proposes a consistent way to associate the evidence for an Ethereum software release or smart-contract deployment with a BOD project-state checkpoint.

The goal is to make the release record portable and independently inspectable across changes in CI providers, artifact stores and maintainers. The profile does not replace the native formats or trust systems that produce the evidence.

The profile remains experimental. A versioned JSON Schema, a dependency-free Python structural validator, a CLI command, a public Reth v2.11.0 client-release fixture and a partial WETH9 mainnet contract-deployment fixture with explicit missing-evidence gaps are now present. This does not yet implement build-system adapters, compiler capture, chain-state verification, Sourcify verification or a production integration.

## 2. Design requirements

A conforming implementation should:

1. identify the source repository and immutable source revision;
2. identify the builder and build configuration;
3. bind compiler inputs and outputs, where relevant;
4. reference test, analysis, audit and SBOM evidence;
5. connect deployed contract bytecode to a chain, transaction and address;
6. represent predecessor releases and upgrade relationships;
7. preserve missing evidence as explicit gaps;
8. package selected evidence bytes for offline recovery;
9. allow native verifiers to validate signatures, provenance, SBOMs and source/bytecode correspondence;
10. remain useful without Ethereum RPC, a wallet or an EAS schema.

## 3. Evidence model

The profile groups evidence into the following domains.

| Domain | Evidence examples | Native authority / verifier |
|---|---|---|
| Source | Repository URI, commit, Git tree identity, submodule references | Git and repository host |
| Build | SLSA/in-toto provenance, builder identity, build type, invocation parameters | SLSA/in-toto verifier and trust policy |
| Compiler | Compiler name/version, settings digest, input bundle digest, output bytecode and ABI digests | Compiler toolchain and reproducible-build procedure |
| Tests | Unit, integration, fuzz, invariant and regression test reports | Test runner, report format and CI identity |
| Security analysis | Static analysis, formal verification, vulnerability scan and audit report references | Each tool's verifier and reviewer policy |
| SBOM | SPDX or CycloneDX document | SPDX/CycloneDX validators and policy |
| Contract verification | Sourcify reference, exact-match versus match classification, verified source metadata, runtime bytecode digest | Sourcify or another source/bytecode verifier |
| Deployment | Chain ID, transaction hash, block hash/number, contract address, runtime code digest and explicit finality observation | Ethereum node/provider and independent chain read |
| Upgrade | Previous deployment, proxy/implementation relation, upgrade transaction and successor release | Chain state, deployment tooling and project-specific policy |
| Witness | BOD registry checkpoint and/or EAS attestation UID | Contract readback and EAS verification |

A reference to a native report is not equivalent to verifying it. The profile records which evidence exists and how to locate it; consumers must still run the relevant verifier and apply an explicit trust policy.

## 4. Versioned record structure

The machine-readable contract is published in:

- [JSON Schema — bod-ethereum-release-profile-v0.1](../schemas/bod-ethereum-release-profile-v0.1.schema.json)
- [Reth v2.11.0 public release fixture](../examples/ethereum-release-profile/reth-v2.11.0.json)
- Reference validator: `src/bod_ethereum_release_profile.py`
- CLI: `bod profile-validate FILE`

The top-level record contains:

| Field | Required content | Meaning |
|---|---|---|
| `profile` | Exact profile identifier | Version dispatch |
| `project` | Stable project ID, project kind, repository URI | Project namespace |
| `release` | Release label/kind, local sequence, source commit and Git tree ID; commit/tree may be null only with matching gap records | Immutable source identity when established, plus BOD lineage position |
| `predecessor` | Null or prior release label plus checkpoint ID | Explicit release continuity |
| `build` | Null or builder identity, provenance digest and compiler record; unavailable builder/provenance fields may be null only with matching gap records | Build context; compiler metadata is mandatory for contract deployments/upgrades, but unavailable compiler digests must remain explicit gaps |
| `deployment` | Null or chain ID, transaction/block IDs, block number, contract address and runtime-code digest; unavailable historical runtime digest may be null only with a gap | Chain-specific deployment reference |
| `evidence` | Typed SHA-256 references, media types, optional URI/issuer and verification status | Evidence inventory |
| `gaps` | Typed missing/unavailable/unverified/invalid items with reasons | Explicit incompleteness |
| `witnesses` | Optional BOD registry checkpoint and EAS attestation UID | External witness references |

The `release.sequence` is a non-negative sequence within the BOD continuity history being represented. It is not inferred from a semantic version or claimed to be a project's global release number. A single-release fixture may use sequence 1 with a null predecessor because it is the first record in that fixture's local lineage.

For `contract-deployment` and `contract-upgrade` records, the validator requires a smart-contract project, compiler metadata, and deployment identifiers. It permits unavailable source commit/tree, builder/provenance and compiler/deployment digests only when each unavailable field has a matching explicit gap record. This prevents the profile from forcing fabricated historical provenance. Ethereum client releases do not fabricate contract or compiler deployment fields.

The Reth fixture is a real public release reference populated from the documented recovery experiment. It intentionally records the binary-to-source relationship and SLSA provenance as gaps. The [WETH9 mainnet fixture](../examples/ethereum-release-profile/weth9-mainnet-2017-12-12.json) records a real deployment, Sourcify compiler/source metadata with its match classification explicitly marked as unavailable, and a finalized block reference while leaving the exact source revision, original build provenance and historical runtime-bytecode digest unresolved. See the [contract fixture report](ETHEREUM_CONTRACT_FIXTURE.md) for the evidence and hash comparison. Structural validity does not re-run GPG, independently re-verify Sourcify, or query Ethereum.

## 5. Required semantics

### 5.1 Identity and canonical encoding

- Profile identifier and version must be explicit.
- Project identity must be stable within the BOD project namespace.
- Source commit must be an immutable commit identifier, not a branch name.
- Digests must declare their algorithm; SHA-256 is the current BOD evidence-reference default.
- JSON canonicalization and profile hashing rules must be specified before a profile digest is used as a protocol commitment.
- Human-readable release labels are metadata and must not replace immutable identifiers.

### 5.2 Evidence completeness and gaps

- Each evidence reference must include a type, digest and media type.
- A URI is a retrieval hint, not proof of availability.
- Missing evidence must be represented explicitly in the gaps list.
- An absent audit, test report or source-verification record must never be interpreted as a successful result.
- Evidence verification states are `NOT_CHECKED`, `VALID`, `INVALID` and `UNAVAILABLE`; `VALID` and `INVALID` entries require a `verification_method` description.
- A `VALID` value is a recorded upstream-verifier result, not a result produced by `bod profile-validate`; consumers must inspect the method, identity policy and original verification output.
- Missing-evidence gap states are `NOT_PROVIDED`, `NOT_CHECKED`, `UNAVAILABLE` and `INVALID`.
- A null or absent Sourcify classification must be represented by a `sourcify-match-classification` gap; do not infer `exact_match` or `match` from the presence of a source record.
- A bundle is self-contained only for payload bytes actually included and successfully verified.

### 5.3 Trust and verification

- Verify provenance with the upstream SLSA/in-toto implementation and a documented builder identity policy.
- Verify signatures and transparency inclusion with Sigstore or the native signing system.
- Validate SBOMs with their native schema validators and policy.
- Verify contract source/bytecode correspondence using Sourcify or an equivalent independent verifier.
- Verify deployment and upgrade references against independently queried chain data.
- Treat EAS attester identity as distinct from repository authorization.
- Treat a BOD registry inclusion as a timestamped commitment witness, not as proof that the release is safe or canonical.

### 5.4 Ethereum and privacy

- Only compact commitments and public identifiers may be considered for on-chain publication.
- Source files, compiler inputs, SBOMs, logs, vulnerability details, audit reports and personal data remain off-chain.
- Hashes are not anonymization; predictable values may be guessed or correlated.
- Chain ID is mandatory for deployment records.
- Block hash and transaction hash should be retained so reorg-sensitive observations can be rechecked.
- A receipt is not finality; the profile requires a finality status, observation time and source for contract deployment records. The consumer must still apply its own explicit finality policy.
- Sourcify source verification must preserve its match classification. An exact metadata match is stronger than a bytecode match without exact metadata correspondence; neither is a formal security proof.

## 6. Relationship to existing standards and tools

The profile composes existing systems:

- Git identifies source history.
- SLSA and in-toto describe build provenance and supply-chain steps.
- Sigstore and Rekor provide signing and transparency.
- SPDX and CycloneDX describe software inventories.
- Sourcify provides source/bytecode verification for deployed contracts.
- EAS provides attestation schemas, issuer identity and predecessor references.
- Ethereum L1 can provide an optional public witness for compact BOD commitments.

The profile should not duplicate their cryptographic formats or claim authority over their verification results.

## 7. Integration with BOD

The proposed integration path is:

1. Capture the source repository using BOD snapshot v0.2.
2. Create the profile document and validate it against a versioned schema.
3. Add the profile document as a typed evidence payload in a BOD envelope.
4. Include the profile bytes and selected referenced payload bytes in an Evidence Bundle.
5. Verify the bundle and profile locally.
6. Run each native evidence verifier according to a declared policy.
7. Optionally anchor the compact checkpoint and publish an EAS attestation after independent review and explicit authorization.

No change to the current Evidence Envelope or Evidence Bundle format should be made until the profile has been exercised against at least one real public release and its compatibility requirements are understood.

## 8. Validation plan

A reference implementation should be tested against at least one public Ethereum client release and one public smart-contract deployment/upgrade history, if suitable fixtures can be obtained.

The evaluation should record:

- which evidence types were available and missing;
- whether all payloads could be recovered without the original CI workspace;
- whether provenance, signatures, SBOM and bytecode correspondence passed native verification;
- whether deployment and upgrade links matched independent chain reads;
- whether forks and conflicting release histories remained visible;
- operator time and actions;
- which external services, accounts and credentials were required.

A comparative baseline must use the project's existing Git, CI, provenance, signature, SBOM and evidence-store workflow without BOD. The profile is useful only if the measured workflow provides a material benefit or exposes a documented gap that existing tools do not address efficiently.

## 9. Current implementation status

| Component | Status |
|---|---|
| BOD snapshot v0.2 | Implemented locally; regression tests pass |
| Evidence envelope and lineage | Implemented prototype |
| Evidence Bundle v0.1 | Implemented experimental format |
| Independent bundle/checkpoint verifier | Implemented |
| Solidity checkpoint registry | Source and tests present; no deployment or audit |
| EAS client tooling | Source and SDK smoke test; no schema registration or live attestation |
| Ethereum release profile schema | Experimental JSON Schema v0.1, dependency-free validator, CLI, Reth client fixture and WETH9 deployment fixture |
| Compiler/build/deployment profile adapter | Not implemented; one historical compiler record is manually captured |
| Sourcify integration | One API v2 record captured manually; no automated adapter or verification orchestration |
| Public contract deployment fixture | Partial: WETH9 deployment facts captured with 12 explicit gaps; two selected evidence payloads recovered from a temporary BOD bundle; no complete source/build/test/audit/upgrade chain |
| Comparative benchmark | Planned |

## 10. Decisions before standardization

1. Validate the current v0.1 fields with independent Ethereum client and smart-contract maintainers.
2. Resolve or further characterize the WETH9 source-revision mismatch; do not substitute the candidate repository revision for an exact source commit.
3. Obtain a second contract fixture with an independently traceable source commit and, preferably, an upgrade/proxy history.
4. Decide whether client releases and contract deployment/upgrade histories should remain one profile or become separate profiles.
5. Define canonicalization and a profile commitment only if a concrete consumer requires one.
6. Add native-verifier orchestration and a complete fixture.
7. Compare with existing tools before describing the profile as differentiated.

The v0.1 data shape and structural validator are implemented as an experiment, not standardized. Contract deployment records carry a finality observation and preserve Sourcify classification (`exact_match` or `match`) when captured; an absent classification must be accompanied by an explicit gap. Null source/build/compiler/runtime fields are allowed only when accompanied by matching explicit gaps. Do not represent the profile as a stable standard, complete integration, independently reviewed format or deployed Ethereum workflow.
