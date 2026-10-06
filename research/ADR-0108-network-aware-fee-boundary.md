# ADR-0108 — Network-aware fee boundary

Status: accepted calibration architecture; numerical parameters remain experimental.
Date: 2026-10-06

## Problem

BOD has two different costs that must not be conflated:

1. native network execution cost paid to the settlement substrate;
2. BOD protocol economics paid for useful continuity work, verification and settlement.

Using a single hard-coded fee for every network would either overcharge users on inexpensive networks or under-recover costs on expensive networks.

## Decision

Use a two-layer quote:

total user cost = native network execution quote + BOD-denominated protocol quote

The native-network quote is dynamic and network-specific. It uses the selected network's gas-estimation and fee rules rather than a global BOD constant. The BOD protocol quote remains separate and is not converted through an unverified BOD/fiat or BOD/native-token market-price oracle.

For the current Arbitrum path:

- Arbitrum Sepolia chain ID: 421614;
- Arbitrum One chain ID: 42161;
- ETH is the gas token on both current public networks;
- priority fee target is 0;
- the gas-price floor is network-specific: 0.2 gwei on Arbitrum Sepolia and 0.02 gwei on Arbitrum One;
- maxFeePerGas uses current base fee plus 20% headroom;
- eth_estimateGas is used without an additional fixed 15% gas-limit surcharge because Arbitrum documents that it returns a gas limit sufficient for the transaction at the current child-chain gas price and that the L1 posting cost is baked into the displayed single fee.

## Economic accounting correction

EC-0001 now explicitly conserves the full priority-fee amount:

- 50% proposer/arbitration;
- 30% verifier pool;
- 20% treasury;
- 0% unallocated.

This matches the existing chain-neutral economic state transition. The correction does not finalize monetary policy.

## Incentive consequence

The fee layer should minimize avoidable user cost while preserving protocol conservation. Network cost is passed through according to the substrate; BOD service pricing remains a separate experimental economic variable. A cheaper settlement network therefore lowers the native execution component without silently changing monetary accounting.

## Verification

- tests/test_bod_network_fee.py covers network-specific floors, dynamic base fees, zero priority fee and invalid inputs.
- tests/test_ec0001_fee_accounting.py covers full priority-fee conservation across multi-year stress.
- tests/test_metamask_bridge.py remains green after removing the fixed 15% gas-limit buffer.

## Arbitrum documentation checkpoint

Official Arbitrum documentation consulted on 2026-10-06:

- Inside Arbitrum Nitro — fee model and priority-fee behavior.
- How to estimate gas in Arbitrum — eth_estimateGas, NodeInterface.gasEstimateComponents(), and the L1-fee-in-gas-limit model.
- Arbitrum chain information — network IDs, RPCs and gas-price floors.
- Fast Feed documentation — current reference transaction bot defaults (PRIORITY_FEE_PER_GAS=0, 20% base-fee boost, estimate gas before sending).

These sources define the implementation boundary; no Arbitrum gas behavior is inferred from model memory.

## Non-goals

This ADR does not define a final BOD token price, final service tariff, market-price oracle, user willingness-to-pay, production gas cost, or final monetary policy.
