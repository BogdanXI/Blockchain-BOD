import pytest

from src.bod_economic_operations import (
    EconomicOperationError,
    OperationPricingPolicyV0_1,
    as_transition,
    quote_project_operation,
)
from src.bod_economy import apply, genesis


def test_operation_quote_is_deterministic_and_accounted() -> None:
    policy = OperationPricingPolicyV0_1(10, 2, 5, 7)
    quote = quote_project_operation(
        operation_id="op-1",
        payer="alice",
        payload_bytes=1025,
        artifact_count=2,
        verification_count=3,
        policy=policy,
    )

    assert quote.total_fee_bod == 45

    state = genesis({"alice": 1_000_000, "vesting:dev": 299_000_000})
    next_state = apply(state, as_transition(quote, height=1, timestamp=1, epoch=0))

    assert next_state.burned == 10
    assert next_state.balances["alice"] == 1_000_000 - quote.total_fee_bod
    assert sum(next_state.balances.values()) == next_state.supply


@pytest.mark.parametrize(
    "field,value",
    [
        ("payload_bytes", -1),
        ("artifact_count", -1),
        ("verification_count", -1),
    ],
)
def test_negative_workload_is_rejected(field: str, value: int) -> None:
    policy = OperationPricingPolicyV0_1(10, 2, 5, 7)
    workload = {
        "payload_bytes": 0,
        "artifact_count": 0,
        "verification_count": 0,
    }
    workload[field] = value

    with pytest.raises(EconomicOperationError):
        quote_project_operation(
            operation_id="op-1",
            payer="alice",
            policy=policy,
            **workload,
        )


def test_negative_policy_value_is_rejected() -> None:
    with pytest.raises(EconomicOperationError):
        OperationPricingPolicyV0_1(-1, 2, 5, 7)


def test_boolean_is_not_accepted_as_integer_workload() -> None:
    policy = OperationPricingPolicyV0_1(10, 2, 5, 7)

    with pytest.raises(EconomicOperationError):
        quote_project_operation(
            operation_id="op-1",
            payer="alice",
            payload_bytes=True,
            artifact_count=0,
            verification_count=0,
            policy=policy,
        )



def test_ec001_workload_measurement_is_deterministic() -> None:
    from src.bod_economic_operations import measure_workload_v0_1
    policy = OperationPricingPolicyV0_1(10, 2, 5, 7)
    sample = measure_workload_v0_1(sample_id="x", payload_bytes=1025, artifact_count=2, verification_count=3, policy=policy)
    assert sample.total_fee_bod == 45
    assert sample.workload_fee_bod == 35


def test_ec001_workload_sweep_has_54_unique_samples() -> None:
    from src.bod_economic_operations import workload_sweep_v0_1
    samples = workload_sweep_v0_1(policy=OperationPricingPolicyV0_1(10, 2, 5, 7))
    assert len(samples) == 54
    assert len({sample.sample_id for sample in samples}) == 54


def test_ec001_each_dimension_increases_or_preserves_cost_monotonically() -> None:
    from src.bod_economic_operations import measure_workload_v0_1
    policy = OperationPricingPolicyV0_1(10, 2, 5, 7)
    base = measure_workload_v0_1(sample_id="base", payload_bytes=1024, artifact_count=0, verification_count=0, policy=policy)
    assert measure_workload_v0_1(sample_id="b", payload_bytes=1025, artifact_count=0, verification_count=0, policy=policy).total_fee_bod > base.total_fee_bod
    assert measure_workload_v0_1(sample_id="a", payload_bytes=1024, artifact_count=1, verification_count=0, policy=policy).total_fee_bod > base.total_fee_bod
    assert measure_workload_v0_1(sample_id="v", payload_bytes=1024, artifact_count=0, verification_count=1, policy=policy).total_fee_bod > base.total_fee_bod


def test_ec001_continuity_delivery_workload_is_separately_priced() -> None:
    from src.bod_economic_operations import measure_workload_v0_1

    policy = OperationPricingPolicyV0_1(
        10, 2, 5, 7,
        state_read_fee_bod_per_kib=3,
        recovery_step_fee_bod=11,
        settlement_unit_fee_bod=13,
        availability_kib_fee_bod=17,
    )
    sample = measure_workload_v0_1(
        sample_id="continuity",
        payload_bytes=0,
        artifact_count=0,
        verification_count=0,
        state_read_bytes=1025,
        recovery_steps=2,
        settlement_units=1,
        availability_kib=4,
        policy=policy,
    )

    assert sample.workload_fee_bod == 6 + 22 + 13 + 68
    assert sample.total_fee_bod == 119


@pytest.mark.parametrize(
    "field",
    [
        "state_read_bytes",
        "recovery_steps",
        "settlement_units",
        "availability_kib",
    ],
)
def test_ec001_continuity_delivery_dimensions_are_monotonic(field: str) -> None:
    from src.bod_economic_operations import measure_workload_v0_1

    policy = OperationPricingPolicyV0_1(
        10, 2, 5, 7,
        state_read_fee_bod_per_kib=3,
        recovery_step_fee_bod=11,
        settlement_unit_fee_bod=13,
        availability_kib_fee_bod=17,
    )
    base = measure_workload_v0_1(
        sample_id="base",
        payload_bytes=0,
        artifact_count=0,
        verification_count=0,
        policy=policy,
    )
    expanded = measure_workload_v0_1(
        sample_id="expanded",
        payload_bytes=0,
        artifact_count=0,
        verification_count=0,
        policy=policy,
        **{field: 1},
    )

    assert expanded.total_fee_bod > base.total_fee_bod


def test_continuity_resource_observation_validates_without_pricing_claims() -> None:
    from src.bod_economic_operations import ContinuityResourceObservationV0_1

    observation = ContinuityResourceObservationV0_1(
        workload_id="fixture",
        payload_bytes_written=1024,
        state_read_bytes=2048,
        artifact_count=1,
        verification_count=2,
        recovery_steps=3,
        settlement_units=1,
        availability_kib_hours=4,
        wall_clock_ms=25,
        cpu_time_ms=17,
        storage_bytes_read=4096,
        storage_bytes_written=1024,
        network_bytes_in=8192,
        network_bytes_out=2048,
    )
    observation.validate()


@pytest.mark.parametrize("field", ["wall_clock_ms", "cpu_time_ms", "network_bytes_in"])
def test_continuity_resource_observation_rejects_negative_values(field: str) -> None:
    from src.bod_economic_operations import ContinuityResourceObservationV0_1

    values = {
        "workload_id": "fixture",
        "payload_bytes_written": 0,
        "state_read_bytes": 0,
        "artifact_count": 0,
        "verification_count": 0,
        "recovery_steps": 0,
        "settlement_units": 0,
        "availability_kib_hours": 0,
        "wall_clock_ms": 0,
        "cpu_time_ms": 0,
        "storage_bytes_read": 0,
        "storage_bytes_written": 0,
        "network_bytes_in": 0,
        "network_bytes_out": 0,
    }
    values[field] = -1
    with pytest.raises(EconomicOperationError):
        ContinuityResourceObservationV0_1(**values).validate()
