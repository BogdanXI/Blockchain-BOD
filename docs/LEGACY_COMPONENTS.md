# Legacy components and migration boundary

## Arbitrum

The former Arbitrum Sepolia adapter and browser-wallet integration are retired from the active product scope. Their source, tests and historical records remain in the repository solely for traceability and reproducibility; they are not supported deployment targets.

The active chain-facing experiment is Ethereum L1, with Ethereum Sepolia as the only planned testnet. The old browser bridge and adapter are not part of the active roadmap, release path or grant proposal. Their historical tests do not establish current operational correctness.

No Arbitrum One deployment is claimed. No Ethereum Sepolia or Ethereum mainnet deployment is claimed either.

## BOD token and economics

The previous BOD token/economic model is outside the current Ethereum product. See [the economics archive note](../economics/README.md) for a documented mismatch between the legacy Python simulator and token policy.

## Active Ethereum scope

Use Ethereum-native tooling only where it provides a concrete verification benefit: EAS for linked attestations and, if justified, a minimal Ethereum L1 checkpoint witness. Do not add an L2 integration merely to increase the number of supported networks. No bridge, rollup, custom chain, BOD token, staking or settlement layer is required for the current evidence-continuity product.

## Migration principle

Preserve historical code and decisions for traceability. Do not silently delete or rewrite the old research record. New product claims must describe the Ethereum checkpoint registry and its actual validation status.
