# Ethereum software release evidence profile

**Document status:** design proposal, not an implemented protocol extension  
**Proposed profile identifier:** bod-ethereum-release-profile-v0.1  
**Prepared:** 22 November 2026  
**Depends on:** BOD Evidence Envelope v0.1 and Evidence Bundle v0.1  
**Scope:** Ethereum execution/consensus clients, developer tooling and smart-contract releases/upgrades

## 1. Purpose

This profile proposes a consistent way to associate the evidence for an Ethereum software release or smart-contract deployment with a BOD project-state checkpoint.

The goal is to make the release record portable and independently inspectable across changes in CI providers, artifact stores and maintainers. The profile does not replace the native formats or trust systems that produce the evidence.

The profile is a grant-work proposal. It is not yet a stable schema, an implemented CLI command or a production integration.

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
| Contract verification | Sourcify reference, verified source metadata, runtime bytecode digest | Sourcify or another source/bytecode verifier |
| Deployment | Chain ID, transaction hash, block hash/number, contract address and runtime code digest | Ethereum node/provider and independent chain read |
| Upgrade | Previous deployment, proxy/implementation relation, upgrade transaction and successor release | Chain state, deployment tooling and project-specific policy |
| Witness | BOD registry checkpoint and/or EAS attestation UID | Contract readback and EAS verification |

A reference to a native report is not equivalent to verifying it. The profile records which evidence exists and how to locate it; consumers must still run the relevant verifier and apply an explicit trust policy.

## 4. Proposed record structure

The following is an illustrative shape, not a finalized JSON Schema:

```json
{
  "profile": "bod-ethereum-release-profile-v0.1",
  "project": {
    "id": "example-client",
    "kind": "ethereum-client",
    "repository": "https://github.com/example/project"
  },
  "release": {
    "id": "v1.2.3",
    "sequence": 12,
    "source_commit": "0123456789abcdef0123456789abcdef01234567",
    "source_tree": "sha1:..."
  },
  "predecessor": {
    "release_id": "v1.2.2",
    "checkpoint_id": "sha256:..."
  },
  "build": {
    "builder_id": "https://github.com/example/project/.github/workflows/release.yml",
    "provenance": "sha256:...",
    "compiler": {
      "name": "solc",
      "version": "0.8.24",
      "settings_digest": "sha256:...",
      "input_digest": "sha256:...",
      "bytecode_digest": "sha256:...",
      "abi_digest": "sha256:..."
    }
  },
  "deployment": {
    "chain_id": 1,
    "transaction_hash": "0x...",
    "block_hash": "0x...",
    "block_number": 12345678,
    "contract_address": "0x...",
    "runtime_bytecode_digest": "sha256:...",
    "source_verification": {
      "provider": "Sourcify",
      "reference": "https://..."
    }
  },
  "evidence": [
    {
      "type": "cyclonedx-sbom",
      "digest": "sha256:...",
      "media_type": "application/vnd.cyclonedx+json",
      "uri": "https://...",
      "issuer": "https://..."
    }
  ],
  "gaps": [
    {
      "type": "independent-security-audit",
      "status": "not-provided",
      "reason": "No independent audit report is available for this release."
    }
  ],
  "witnesses": {
    "ethereum_registry_checkpoint": null,
    "eas_attestation_uid": null
  }
}
```

The values above are placeholders. They do not refer to a real release, deployment, address, transaction or attestation. The project kind should distinguish at least an Ethereum client from a smart-contract project. Compiler and deployment sections are conditional: client releases may omit contract deployment fields, while a contract deployment/upgrade record must include the applicable chain and deployment references.

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
- The profile must distinguish NOT_PROVIDED, NOT_CHECKED, INVALID, VALID and UNAVAILABLE states where applicable.
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
- A receipt is not finality; the consumer must apply an explicit finality policy.

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
| Ethereum release profile schema | Proposed only |
| Compiler/build/deployment profile adapter | Not implemented |
| Sourcify integration | Not implemented |
| End-to-end public contract release fixture | Not completed |
| Comparative benchmark | Planned |

## 10. Decisions before standardization

1. Select the first target workflow: Ethereum client release, standalone contract deployment, or proxy upgrade history.
2. Confirm required fields with independent maintainers and security reviewers.
3. Decide whether one profile should cover both clients and contracts or whether separate profiles are clearer.
4. Define JSON Schema, canonicalization, digest and compatibility rules.
5. Implement a public fixture and native-verifier orchestration.
6. Compare with existing tools before describing the profile as differentiated.

Until these decisions and tests are complete, this document remains a design proposal and must not be represented as an implemented standard.
