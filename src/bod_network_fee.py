"""Network-aware native-gas fee quoting for BOD application operations."""
from __future__ import annotations

from dataclasses import dataclass

BPS = 10_000


class NetworkFeeError(ValueError):
    pass


@dataclass(frozen=True)
class NetworkFeePolicyV0_1:
    network: str
    chain_id: int
    native_symbol: str
    gas_price_floor_wei: int
    priority_fee_wei: int = 0
    base_fee_boost_bps: int = 2_000
    gas_limit_buffer_bps: int = 0

    def __post_init__(self) -> None:
        if not self.network or not self.native_symbol or self.chain_id <= 0:
            raise NetworkFeeError("network, chain_id and native_symbol are required")
        if min(self.gas_price_floor_wei, self.priority_fee_wei, self.base_fee_boost_bps, self.gas_limit_buffer_bps) < 0:
            raise NetworkFeeError("fee policy values must be non-negative")
        if self.base_fee_boost_bps >= BPS or self.gas_limit_buffer_bps >= BPS:
            raise NetworkFeeError("fee buffers must be below 10000 bps")


@dataclass(frozen=True)
class NetworkFeeQuoteV0_1:
    network: str
    chain_id: int
    native_symbol: str
    gas_estimate: int
    gas_limit: int
    latest_base_fee_wei: int
    effective_base_fee_wei: int
    priority_fee_wei: int
    max_fee_per_gas_wei: int
    expected_network_fee_wei: int
    max_network_fee_wei: int


def _ceil_div(a: int, b: int) -> int:
    return (a + b - 1) // b


def quote_network_fee_v0_1(*, policy: NetworkFeePolicyV0_1, gas_estimate: int, latest_base_fee_wei: int) -> NetworkFeeQuoteV0_1:
    if not isinstance(gas_estimate, int) or isinstance(gas_estimate, bool) or gas_estimate <= 0:
        raise NetworkFeeError("gas_estimate must be a positive integer")
    if not isinstance(latest_base_fee_wei, int) or isinstance(latest_base_fee_wei, bool) or latest_base_fee_wei < 0:
        raise NetworkFeeError("latest_base_fee_wei must be a non-negative integer")
    base = max(latest_base_fee_wei, policy.gas_price_floor_wei)
    max_fee = _ceil_div(base * (BPS + policy.base_fee_boost_bps), BPS) + policy.priority_fee_wei
    gas_limit = _ceil_div(gas_estimate * (BPS + policy.gas_limit_buffer_bps), BPS)
    expected_price = base + policy.priority_fee_wei
    return NetworkFeeQuoteV0_1(
        network=policy.network,
        chain_id=policy.chain_id,
        native_symbol=policy.native_symbol,
        gas_estimate=gas_estimate,
        gas_limit=gas_limit,
        latest_base_fee_wei=latest_base_fee_wei,
        effective_base_fee_wei=base,
        priority_fee_wei=policy.priority_fee_wei,
        max_fee_per_gas_wei=max_fee,
        expected_network_fee_wei=gas_estimate * expected_price,
        max_network_fee_wei=gas_limit * max_fee,
    )


ARBITRUM_SEPOLIA_FEE_POLICY = NetworkFeePolicyV0_1("Arbitrum Sepolia", 421614, "ETH", 200_000_000)
ARBITRUM_ONE_FEE_POLICY = NetworkFeePolicyV0_1("Arbitrum One", 42161, "ETH", 20_000_000)
