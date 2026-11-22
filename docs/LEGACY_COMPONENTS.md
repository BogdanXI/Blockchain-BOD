# Legacy components and migration boundary

## BOD token and economics

The previous BOD token/economic model is outside the current Ethereum product. See [the economics archive note](../economics/README.md) for a documented mismatch between the legacy Python simulator and token policy.

## Active Ethereum scope

Use Ethereum-native tooling only where it provides a concrete verification benefit: EAS for linked attestations and, if justified, a minimal Ethereum L1 checkpoint witness. Do not add an L2 integration merely to increase the number of supported networks. No bridge, rollup, custom chain, BOD token, staking or settlement layer is required for the current evidence-continuity product.

## Migration principle

Preserve historical code and decisions for traceability. Do not silently delete or rewrite the old research record. New product claims must describe the Ethereum checkpoint registry and its actual validation status.
