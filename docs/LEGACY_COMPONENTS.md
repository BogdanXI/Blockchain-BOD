# Legacy components and migration boundary

## Arbitrum

The original Arbitrum Sepolia work remains in `protocol/arbitrum/`, `tools/metamask/` and the workflows whose names include `bod-sepolia`. It is retained as historical experimental material.

It is not the active product target. The current public roadmap targets an Ethereum Sepolia checkpoint-registry pilot. The old browser bridge and adapter have not been re-certified as production-ready; do not infer their current operational correctness from historical tests or documentation.

No Arbitrum One or Ethereum mainnet deployment is claimed.

## BOD token and economics

The previous BOD token/economic model is outside the current Ethereum product. See [the economics archive note](../economics/README.md) for a documented mismatch between the legacy Python simulator and token policy.

## Migration principle

Preserve historical code and decisions for traceability. Do not silently delete or rewrite the old research record. New product claims must describe the Ethereum checkpoint registry and its actual validation status.
