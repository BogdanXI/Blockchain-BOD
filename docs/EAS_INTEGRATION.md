# Ethereum Attestation Service integration

**Status:** executable Sepolia schema-registration and checkpoint-attestation clients are included. No schema has been registered and no attestation has been submitted by this repository.

## Why EAS

BOD should not invent a generic attestation system. EAS already provides schema registration, issuer identity, on-chain/off-chain attestations, attestation UIDs and parent references. BOD contributes the deterministic project snapshot, portable evidence bundle and recovery verifier.

The division of responsibility is:

- BOD computes and verifies the project checkpoint and evidence digests.
- EAS records an issuer-attributed attestation using a shared schema.
- EAS `refUID` links a child attestation to its predecessor.
- Consumers independently decode the attestation, verify the BOD checkpoint and apply their own issuer/release policy.

EAS does not make evidence semantically true. A schema UID is chain-specific, and the schema string must match exactly.

## Official EAS deployments

The addresses below are taken from the official EAS deployment documentation (version 0.26):

| Network | Chain ID | EAS | Schema Registry |
|---|---:|---|---|
| Ethereum Mainnet | 1 | `0xA1207F3BBa224E2c9c3c6D5aF63D0eb1582Ce587` | `0xA7b39296258348C78294F95B872b282326A97BDF` |
| Ethereum Sepolia | 11155111 | `0xC2679fBD37d54388Ce493F1DB75320D236e1815e` | `0x0a7E2Ff54e76B8E6659aedc9103FB21c038050D0` |

Source: [Official EAS contract deployments](https://docs.attest.org/docs/quick--start/contracts).

## BOD schema

The exact schema string is stored in `tools/eas/schema.mjs`:

```text
bytes32 projectId, bytes32 checkpointId, bytes32 gitCommit, bytes32 stateRoot, bytes32 manifestHash, bytes32 evidenceRoot, uint64 sequence
```

The schema is non-revocable. The parent relationship is represented by EAS `refUID`, not by placing a mutable pointer in the BOD data.

Before registering a schema, search the EAS schema explorer for an existing compatible schema. Do not register duplicates without a reason. Registration produces a chain-specific schema UID.

## Setup

Node.js 20+ is required.

```bash
npm install --ignore-scripts
```

Create a dedicated Ethereum Sepolia wallet. Never use a production key. Set the following variables in your local shell:

```bash
export ETHEREUM_SEPOLIA_RPC_URL="https://your-sepolia-rpc"
export ETHEREUM_SEPOLIA_PRIVATE_KEY="0x..."
```

Register the schema once:

```bash
npm run eas:register-schema
```

Record the returned schema UID, then set it:

```bash
export BOD_EAS_SCHEMA_UID="0x..."
```

Create a BOD portable checkpoint and attest it:

```bash
bod capture . --project my-project --out checkpoint.json
npm run eas:attest-checkpoint -- checkpoint.json
```

For the first checkpoint, omit parent variables. For a later checkpoint, provide the preceding EAS UID and the next sequence:

```bash
export BOD_EAS_PARENT_UID="0x..."
export BOD_EAS_SEQUENCE="1"
npm run eas:attest-checkpoint -- checkpoint.json
```

The client refuses to send transactions unless the RPC reports Ethereum Sepolia chain ID 11155111. It does not automatically deploy contracts or use mainnet.

## Verification model

A consumer should:
1. fetch the EAS attestation by UID from the chain;
2. confirm the chain ID and schema UID;
3. decode the schema data;
4. verify attester identity against a project-specific trust policy;
5. follow `refUID` to the predecessor and check project ID and sequence continuity;
6. retrieve the portable BOD checkpoint and run the independent verifier;
7. verify each referenced SLSA/in-toto, SBOM, signature or release artifact using its native verifier.

The EAS UID and transaction hash are external locators, not substitutes for BOD verification. EAS indexing APIs and explorers are conveniences; chain data and independently retrievable artifacts remain the verification basis.

## Important limitations

- The EAS schema is not yet registered by this repository.
- The scripts have not been used to submit a live attestation.
- EAS issuer identity is not automatically repository authorization.
- The sample client derives the Git commit digest from the current checkout's HEAD; the checkpoint must be captured from the same commit context.
- EAS references do not guarantee availability of the portable checkpoint or evidence payloads.
- Mainnet use requires independent review, a project-specific issuer policy and cost analysis.
