# BOD GitHub → Arbitrum Sepolia Anchoring

Status: testnet integration path.

## Purpose

Arbitrum Sepolia is used as an external, independently timestamped commitment layer for BOD development checkpoints.

The public GitHub repository remains the source of public code. The chain stores only repository identifier, Git commit commitment, BOD state-root commitment, canonical manifest commitment, block timestamp and submitting address.

No source code, prompts, internal repository state, credentials, or AI context is written on-chain.

## Development role

Each successful anchor is a verifiable external checkpoint: GitHub commit → deterministic BOD snapshot → stateRoot → Arbitrum Sepolia transaction. A later runtime can independently compare a recovered snapshot with the historical chain commitment.

This is an external testnet commitment layer, not BOD consensus and not a claim of semantic correctness.

## Network

Arbitrum Sepolia is chain ID 421614.

## Deployment

Deploy BODGitCommitmentRegistryV0_1 once on Arbitrum Sepolia. The automated anchor workflow is gated on BOD_SEPOLIA_RPC_URL, BOD_SEPOLIA_PRIVATE_KEY and BOD_SEPOLIA_REGISTRY_ADDRESS. The private key must belong to a dedicated testnet signer and must never be committed.

## Anchor identity

anchorId is the hash of repository identity, Git commit, stateRoot and manifest commitment. The same checkpoint therefore cannot be anchored twice under the same identity.

## Promotion path

1. Deploy and verify the registry on Arbitrum Sepolia.
2. Execute one manual anchor and verify the event and transaction in the explorer.
3. Enable GitHub Actions automatic anchoring on main.
4. Treat the anchor transaction as an external checkpoint for subsequent recovery/conformance work.
5. Later replace or supplement the external testnet anchor with the appropriate BOD settlement layer.