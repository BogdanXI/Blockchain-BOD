# ADR-0109 — Dynamic network fee floor and affordability boundary

Status: accepted calibration architecture; numerical parameters remain experimental.
Date: 2026-10-06

## Decision

The BOD EVM integration must not hard-code a permanent gas-price floor when the selected Arbitrum network exposes the current minimum through its protocol precompile.

The browser signer reads ArbGasInfo.getMinimumGasPrice() from precompile 0x000000000000000000000000000000000000006c immediately before preparing a transaction. It then uses the larger of the current block base fee and that chain-reported minimum, with zero priority fee and 20% headroom.

This creates three layers:

1. Network minimum — supplied by the selected chain.
2. Current congestion price — current base fee.
3. BOD protocol fee — separate BOD-denominated utility price.

They must not be collapsed into one global constant.

## Why this is cheaper

The transaction is prepared against current chain conditions rather than a stale global floor. The bridge also submits the exact eth_estimateGas result instead of adding a fixed 15% gas-limit surcharge.

For users, the result is:

- no unnecessary priority fee;
- no stale overpayment when the network minimum changes;
- no fixed wallet-visible gas-limit padding;
- protocol BOD pricing remains independently calibratable;
- network-specific gas economics are inherited from the selected substrate.

This does not promise a particular fiat cost. It minimizes avoidable protocol-side and transaction-construction overhead.

## Arbitrum documentation checkpoint

Official Arbitrum documentation consulted on 2026-10-06:

- Chain Information: Arbitrum One chain ID 42161, Arbitrum Sepolia chain ID 421614, and network-specific gas-price floors.
- Precompiles Reference: ArbGasInfo, including getMinimumGasPrice() and getCurrentTxL1GasFees().
- Fast Feed reference bot: PRIORITY_FEE_PER_GAS=0, 20% BASE_FEE_BOOST_PERCENT, and gas estimation before transactions.
- Solidity Quickstart: Arbitrum Sepolia/One EVM deployment path and fee-estimation reference.

## Live Arbitrum Sepolia observation — 2026-10-06

Direct RPC observation: ArbGasInfo.getMinimumGasPrice() returned 20,000,000 wei (0.02 gwei). The same public RPC returned 86,060,000 wei (0.08606 gwei) for eth_gasPrice. The dynamic policy therefore avoids treating the older documented 0.2 gwei floor as a mandatory transaction price when the live chain reports a lower minimum. This is an observation, not a permanent network guarantee.

## Live Arbitrum Sepolia observation — 2026-10-06

Direct RPC observation: ArbGasInfo.getMinimumGasPrice() returned 20,000,000 wei (0.02 gwei). The same public RPC returned 86,060,000 wei (0.08606 gwei) for eth_gasPrice. The dynamic policy therefore avoids treating the older documented 0.2 gwei floor as a mandatory transaction price when the live chain reports a lower minimum. This is an observation, not a permanent network guarantee.

## Non-goals

This ADR does not set a final BOD token price, final service tariff, or final monetary policy. It also does not introduce a BOD/ETH oracle. Native gas remains a network infrastructure cost; BOD utility pricing remains a separate protocol-economic variable.

## Verification

- Static bridge tests assert use of ArbGasInfo.getMinimumGasPrice().
- Fee-policy tests cover network-specific floors and dynamic base-fee behavior.
- The live Sepolia E2E remains testnet-only and must be re-run after this change.
