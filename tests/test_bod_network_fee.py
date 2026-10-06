from src.bod_network_fee import (
    ARBITRUM_ONE_FEE_POLICY,
    ARBITRUM_SEPOLIA_FEE_POLICY,
    NetworkFeeError,
    quote_network_fee_v0_1,
)


def test_arbitrum_sepolia_uses_floor_and_zero_priority_fee():
    quote = quote_network_fee_v0_1(
        policy=ARBITRUM_SEPOLIA_FEE_POLICY,
        gas_estimate=377_207,
        latest_base_fee_wei=100_000_000,
    )
    assert quote.effective_base_fee_wei == 200_000_000
    assert quote.priority_fee_wei == 0
    assert quote.max_fee_per_gas_wei == 240_000_000
    assert quote.gas_limit == 377_207
    assert quote.expected_network_fee_wei == 75_441_400_000_000


def test_arbitrum_one_uses_lower_documented_floor():
    quote = quote_network_fee_v0_1(
        policy=ARBITRUM_ONE_FEE_POLICY,
        gas_estimate=100_000,
        latest_base_fee_wei=0,
    )
    assert quote.effective_base_fee_wei == 20_000_000
    assert quote.max_fee_per_gas_wei == 24_000_000


def test_dynamic_base_fee_does_not_use_stale_floor_when_higher():
    quote = quote_network_fee_v0_1(
        policy=ARBITRUM_SEPOLIA_FEE_POLICY,
        gas_estimate=100_000,
        latest_base_fee_wei=300_000_000,
    )
    assert quote.effective_base_fee_wei == 300_000_000
    assert quote.max_fee_per_gas_wei == 360_000_000


def test_invalid_gas_estimate_is_rejected():
    try:
        quote_network_fee_v0_1(
            policy=ARBITRUM_SEPOLIA_FEE_POLICY,
            gas_estimate=0,
            latest_base_fee_wei=100_000_000,
        )
    except NetworkFeeError:
        return
    raise AssertionError("zero gas estimate must be rejected")
