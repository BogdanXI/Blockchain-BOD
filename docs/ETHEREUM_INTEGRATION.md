# Ethereum integration

**Status:** source and local tests only. No testnet or mainnet deployment is claimed.

## Design objective

Use Ethereum L1 as an optional, independently readable witness for compact BOD project checkpoints. Keep project files, build outputs and evidence payloads off-chain. The continuity core remains useful without a blockchain connection.

The contract is `protocol/ethereum/BODEthereumCheckpointRegistry.sol`.

## Checkpoint fields

| Field | Meaning |
|---|---|
| projectId | Stable project namespace commitment |
| gitCommit | Digest of the source-control commit identifier |
| stateRoot | BOD deterministic project-state root |
| manifestHash | Digest of the portable checkpoint/manifest |
| evidenceRoot | Digest or Merkle root of the evidence references |
| previousCheckpointId | Parent checkpoint, or zero for genesis |
| sequence | Project-local sequence number |
| publisher | Transaction sender |
| anchoredAt | Ethereum block timestamp |

The contract checks that a non-genesis checkpoint references an existing parent from the same project and increments its sequence by one. It does not choose a canonical branch. Two children of the same parent are both recordable; consumers must apply their own trust and release policy.

## Permissionless publication

The registry is an append-only evidence log, not an access-control system. Any account may publish a commitment. The publisher address is recorded, but the contract does not claim that the publisher is authorized to speak for a repository.

Repository authorization belongs in signed provenance/attestations and consumer policy. The EAS SDK integration is now provided separately: it records attester identity and predecessor references using a non-revocable BOD schema. The registry remains optional; see [EAS Integration](EAS_INTEGRATION.md). Do not infer repository authorization from an arbitrary transaction.

## No token or fee layer

Ethereum gas is paid in ETH by the transaction sender. The registry has no ERC-20 dependency, reward, staking, slashing, bridge or treasury logic. This removes unrelated token-economics assumptions from the first Ethereum use case.

## Supply-chain interoperability

BOD should compose existing standards rather than invent another attestation format:

- SLSA/in-toto for build provenance;
- SPDX or CycloneDX for SBOMs;
- Sigstore/Rekor for signing and transparency;
- Ethereum Attestation Service (EAS) where an on-chain/off-chain attestation schema and issuer model are useful.

The executable EAS SDK clients are present in tools/eas. They support Sepolia schema registration and checkpoint attestations using the shared schema. This repository has not registered the schema or submitted a live attestation; the integration is therefore source-implemented but not live-validated. The current schema carries projectId, checkpointId, gitCommit, stateRoot, manifestHash, evidenceRoot and sequence; the predecessor is linked through EAS refUID. See [EAS Integration](EAS_INTEGRATION.md).

## Local verification

Install Foundry, then run `forge test -vvv`. No RPC endpoint or wallet is needed for local tests.

## Sepolia deployment rehearsal

Only after independent review:

1. Create a dedicated test wallet; never use a production wallet.
2. Fund it with Sepolia ETH from a reputable faucet.
3. Set ETHEREUM_SEPOLIA_RPC_URL and ETHEREUM_SEPOLIA_PRIVATE_KEY in the local shell or protected CI environment.
4. Deploy using Foundry:

```bash
forge create protocol/ethereum/BODEthereumCheckpointRegistry.sol:BODEthereumCheckpointRegistry \
  --rpc-url "$ETHEREUM_SEPOLIA_RPC_URL" \
  --private-key "$ETHEREUM_SEPOLIA_PRIVATE_KEY"
```

5. Record the deployment transaction, address, chain ID and compiler settings.
6. Verify the source and deployed bytecode using an independent explorer/API.
7. Publish a synthetic checkpoint and read it back from at least two independent RPC providers.

Never commit private keys, seed phrases, RPC credentials or signed transaction payloads. Do not deploy to mainnet based only on passing unit tests.

## Chain parameters

| Network | Chain ID | Role |
|---|---:|---|
| Ethereum Mainnet | 1 | Production target only after separate approval |
| Ethereum Sepolia | 11155111 | Testnet pilot |

No L2-specific adapter or deployment is part of the active Ethereum integration scope.

## Known limitations

- Block timestamps are approximate and are not trusted wall-clock time.
- Ethereum reorgs mean a receipt is not final immediately; clients must define confirmation/finality policy.
- The contract stores commitments, not evidence bytes.
- Permissionless publication allows spam and competing branches.
- The contract does not authenticate repository ownership.
- The contract does not prove the source/build/evidence is correct.
- No formal verification or external audit has been completed. No fuzz/invariant campaign or independently reviewed security report is currently claimed.
