from src.bod_network_fee import (
    ETHEREUM_MAINNET_FEE_POLICY,
    ETHEREUM_SEPOLIA_FEE_POLICY,
    NetworkFeeError,
    quote_network_fee_v0_1,
)


def test_ethereum_policies_use_live_base_fee_without_stale_floor():
    for policy in (ETHEREUM_MAINNET_FEE_POLICY, ETHEREUM_SEPOLIA_FEE_POLICY):
        quote = quote_network_fee_v0_1(
            policy=policy,
            gas_estimate=100_000,
            latest_base_fee_wei=20_000_000_000,
        )
        assert quote.chain_id in (1, 11155111)
        assert quote.effective_base_fee_wei == 20_000_000_000
        assert quote.max_fee_per_gas_wei == 24_000_000_000
        assert quote.expected_network_fee_wei == 2_000_000_000_000_000


def test_invalid_gas_estimate_is_rejected():
    try:
        quote_network_fee_v0_1(
            policy=ETHEREUM_MAINNET_FEE_POLICY,
            gas_estimate=0,
            latest_base_fee_wei=100_000_000,
        )
    except NetworkFeeError:
        return
    raise AssertionError("zero gas estimate must be rejected")
