# BOD GitHub → Arbitrum Sepolia Anchoring

**Status:** experimental testnet integration.

## Purpose

Arbitrum Sepolia is used as an optional external witness for public BOD development checkpoints.

The chain stores commitments only: repository identifier, Git commit commitment, BOD state-root commitment, manifest commitment and submitting address. Source code, repository contents and evidence payloads remain off-chain.

## Development role

The intended flow is:

`public Git commit → deterministic BOD snapshot → state and manifest commitments → Arbitrum Sepolia transaction`.

A reviewer can check out the referenced public commit, reproduce the snapshot and compare the resulting commitments with the values recorded on-chain.

This is an external testnet commitment path. It is not BOD consensus and does not establish semantic correctness.

## Network

- Network: Arbitrum Sepolia
- Chain ID: `421614`
- RPC: `https://sepolia-rollup.arbitrum.io/rpc`

## Execution boundary

The public reusable workflow is:

`.github/workflows/bod-sepolia-reusable-anchor.yml`

It accepts a signing key through a protected workflow secret. The signing workflow should be controlled separately from the public source repository and must pass only the minimum required secret to the reusable workflow. Node dependencies are locked in `tools/arbitrum/package-lock.json`; the workflows use Node 22, ethers 6.17.0 and solc 0.8.24.

The private key must never be committed to this repository, placed in a public artifact or shared in chat. Use a dedicated testnet account with no production funds.

The workflow checks out the public repository at `main`, computes a deterministic checkpoint, deploys the experimental registry, anchors the checkpoint and verifies the stored values. CI compilation of Solidity sources does not constitute behavioral contract testing or an audit. Because it checks out `main`, the exact commit being anchored must be confirmed in the workflow output before relying on the result.

## Anchor identity

`anchorId` is derived deterministically from repository identity, Git commit, state root and manifest commitment. The same inputs therefore produce the same identifier.

## Verification requirements

A testnet checkpoint is considered verified only after checking:

1. chain ID;
2. registry address and deployment transaction;
3. anchor transaction and block;
4. stored repository, Git, state-root and manifest commitments;
5. equality with the snapshot recomputed from the referenced public Git commit.

The resulting evidence supports checkpoint verification. It does not demonstrate source-payload restoration, production availability or consensus security.

## Promotion path

1. Execute a controlled testnet anchor.
2. Independently verify deployment and checkpoint transactions.
3. Publish a minimal, reproducible verification record that contains no signing material.
4. Reproduce the snapshot from the referenced public commit in a clean runtime.
5. Evaluate continuous anchoring only after the controlled flow is reliable.
