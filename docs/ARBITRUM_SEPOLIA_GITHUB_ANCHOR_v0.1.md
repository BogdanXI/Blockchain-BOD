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

Use the manual GitHub Actions workflow `Deploy BOD Sepolia Registry` to deploy `BODGitCommitmentRegistryV0_1`. The anchor workflow is initially safe to run manually and then supports a scheduled zero-click checkpoint loop.

Configure the `bod-sepolia` GitHub Environment with:
- `BOD_SEPOLIA_PRIVATE_KEY` — dedicated testnet signer only;
- `BOD_SEPOLIA_RPC_URL` — optional; if omitted, the workflow uses the official Arbitrum Sepolia public RPC;
- `BOD_SEPOLIA_REGISTRY_ADDRESS` — set after deployment.

The private key must never be committed or sent through chat. The signer must have Arbitrum Sepolia ETH for gas. After deployment, copy the printed registry address into `BOD_SEPOLIA_REGISTRY_ADDRESS`, then run `BOD Sepolia Anchor` manually for the first checkpoint. Once that transaction is independently verified, the scheduled checkpoint loop may remain enabled without MetaMask interaction.

## Anchor identity

anchorId is the hash of repository identity, Git commit, stateRoot and manifest commitment. The same checkpoint therefore cannot be anchored twice under the same identity.

## Promotion path

1. Deploy and verify the registry on Arbitrum Sepolia.
2. Execute one manual anchor and verify the event and transaction in the explorer.
3. Enable GitHub Actions automatic anchoring on main.
4. Treat the anchor transaction as an external checkpoint for subsequent recovery/conformance work.
5. Later replace or supplement the external testnet anchor with the appropriate BOD settlement layer.

## Checkpoint observation policy

The experimental branch uses a 30-minute scheduler as a **measurement policy**, not as a final product policy.

Each run:
1. validates the public surface;
2. runs the registry-boundary regression;
3. captures the latest deterministic BOD snapshot;
4. checks whether the checkpoint already exists;
5. submits exactly one new anchor only when the checkpoint is new;
6. records transaction gas and checkpoint identity as workflow evidence.

This deliberately batches multiple Git commits into a checkpoint when development is faster than the schedule. The experiment can later compare 30-minute batching against commit-based, CI-based and release-based policies.

The scheduler is not BOD consensus and does not imply that 30 minutes is economically optimal.
