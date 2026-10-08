# BOD GitHub → Arbitrum Sepolia Anchoring

Status: testnet integration path.

## Purpose

Arbitrum Sepolia is used as an external, independently verifiable commitment layer for BOD development checkpoints.

The PUBLIC GitHub repository remains the source of public code. The chain stores only public-safe commitments: repository identifier, Git commit commitment, BOD state-root commitment, manifest commitment and submitting address.

No source code, prompts, INTERNAL repository state, credentials or AI context is written on-chain.

## Development role

Each successful anchor is a verifiable external checkpoint:

`PUBLIC Git commit → deterministic BOD snapshot → stateRoot/manifest commitments → Arbitrum Sepolia transaction`.

A later runtime can independently reconstruct the public snapshot and compare it with the historical chain commitment.

This is an external testnet commitment layer, not BOD consensus and not a claim of semantic correctness.

## Network

Arbitrum Sepolia is chain ID 421614.

## Execution boundary

The reusable public workflow is:

`.github/workflows/bod-sepolia-reusable-anchor.yml`

It is intentionally a `workflow_call` boundary. The signer is supplied by the INTERNAL repository, never by PUBLIC.

The INTERNAL caller is:

`.github/workflows/bod-arbitrum-sepolia-live.yml`

The INTERNAL workflow owns the signer secret `BOD_ARBITRUM_SEPOLIA_PRIVATE_KEY` and passes it to the public reusable workflow. The public workflow then checks out PUBLIC `main`, computes the deterministic checkpoint, deploys `BODGitCommitmentRegistryV0_1`, anchors the checkpoint and verifies the stored commitment.

For the first checkpoint, execution is intentionally manual/controlled from INTERNAL. Automatic anchoring on every PUBLIC push is not enabled.

## Signer boundary

The private key must never be committed, placed in PUBLIC, or sent through chat. The signer is a dedicated Arbitrum Sepolia account with sufficient testnet ETH for gas.

The public workflow uses the fixed Arbitrum Sepolia RPC:

`https://sepolia-rollup.arbitrum.io/rpc`

and verifies chain ID `421614`.

## Anchor identity

`anchorId` is derived deterministically from repository identity, Git commit, state root and manifest commitment. The same checkpoint therefore has a stable cryptographic identity.

## Verification requirement

A checkpoint is not considered complete until the resulting deployment and anchor transaction are independently verified for:

1. chain ID;
2. registry address;
3. deployment transaction and block;
4. anchor transaction and block;
5. stored repository/Git/stateRoot/manifest commitments;
6. equality with the deterministic snapshot reconstructed from the referenced PUBLIC commit.

Only after that gate is satisfied should the project use the checkpoint for fresh-runtime recovery evidence.

## Promotion path

1. Execute the first INTERNAL-controlled anchor.
2. Independently verify the deployment and checkpoint transaction.
3. Record the verified evidence in INTERNAL state.
4. Implement fresh-runtime recovery against the verified checkpoint.
5. Later evaluate continuous anchoring as a separate engineering decision.
