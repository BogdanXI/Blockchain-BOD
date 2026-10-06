"""Deterministic pricing bridge from BOD workload operations to economic transitions."""

from __future__ import annotations

from dataclasses import dataclass
from itertools import product

from src.bod_economy import Transition


class EconomicOperationError(ValueError):
    """Invalid workload or pricing input."""


@dataclass(frozen=True)
class OperationPricingPolicyV0_1:
    base_fee_bod: int
    bytes_fee_bod_per_kib: int
    artifact_fee_bod: int
    verification_fee_bod: int
    state_read_fee_bod_per_kib: int = 0
    recovery_step_fee_bod: int = 0
    settlement_unit_fee_bod: int = 0
    availability_kib_fee_bod: int = 0
    network_in_fee_bod_per_kib: int = 0
    network_out_fee_bod_per_kib: int = 0

    def __post_init__(self) -> None:
        values = (
            self.base_fee_bod,
            self.bytes_fee_bod_per_kib,
            self.artifact_fee_bod,
            self.verification_fee_bod,
            self.state_read_fee_bod_per_kib,
            self.recovery_step_fee_bod,
            self.settlement_unit_fee_bod,
            self.availability_kib_fee_bod,
            self.network_in_fee_bod_per_kib,
            self.network_out_fee_bod_per_kib,
        )
        if any(not isinstance(value, int) or isinstance(value, bool) or value < 0 for value in values):
            raise EconomicOperationError("pricing values must be non-negative integers")


@dataclass(frozen=True)
class OperationQuote:
    operation_id: str
    payer: str
    payload_bytes: int
    artifact_count: int
    verification_count: int
    state_read_bytes: int
    recovery_steps: int
    settlement_units: int
    availability_kib: int
    network_in_bytes: int
    network_out_bytes: int
    base_fee_bod: int
    priority_fee_bod: int

    @property
    def total_fee_bod(self) -> int:
        return self.base_fee_bod + self.priority_fee_bod


def quote_project_operation(
    *,
    operation_id: str,
    payer: str,
    payload_bytes: int,
    artifact_count: int,
    verification_count: int,
    policy: OperationPricingPolicyV0_1,
    state_read_bytes: int = 0,
    recovery_steps: int = 0,
    settlement_units: int = 0,
    availability_kib: int = 0,
    network_in_bytes: int = 0,
    network_out_bytes: int = 0,
) -> OperationQuote:
    if not operation_id or not payer:
        raise EconomicOperationError("operation_id and payer are required")
    values = (payload_bytes, artifact_count, verification_count, state_read_bytes, recovery_steps, settlement_units, availability_kib, network_in_bytes, network_out_bytes)
    if any(not isinstance(value, int) or isinstance(value, bool) or value < 0 for value in values):
        raise EconomicOperationError("workload values must be non-negative integers")

    kib = (payload_bytes + 1023) // 1024
    workload_fee = (
        kib * policy.bytes_fee_bod_per_kib
        + artifact_count * policy.artifact_fee_bod
        + verification_count * policy.verification_fee_bod
        + ((state_read_bytes + 1023) // 1024) * policy.state_read_fee_bod_per_kib
        + recovery_steps * policy.recovery_step_fee_bod
        + settlement_units * policy.settlement_unit_fee_bod
        + availability_kib * policy.availability_kib_fee_bod
        + ((network_in_bytes + 1023) // 1024) * policy.network_in_fee_bod_per_kib
        + ((network_out_bytes + 1023) // 1024) * policy.network_out_fee_bod_per_kib
    )
    return OperationQuote(
        operation_id=operation_id,
        payer=payer,
        payload_bytes=payload_bytes,
        artifact_count=artifact_count,
        verification_count=verification_count,
        state_read_bytes=state_read_bytes,
        recovery_steps=recovery_steps,
        settlement_units=settlement_units,
        availability_kib=availability_kib,
        network_in_bytes=network_in_bytes,
        network_out_bytes=network_out_bytes,
        base_fee_bod=policy.base_fee_bod,
        priority_fee_bod=workload_fee,
    )


@dataclass(frozen=True)
class ContinuityResourceObservationV0_1:
    """Observed infrastructure workload, kept separate from BOD quote coefficients."""

    workload_id: str
    payload_bytes_written: int
    state_read_bytes: int
    artifact_count: int
    verification_count: int
    recovery_steps: int
    settlement_units: int
    availability_kib_hours: int
    wall_clock_ms: int
    cpu_time_ms: int
    storage_bytes_read: int
    storage_bytes_written: int
    network_bytes_in: int
    network_bytes_out: int

    def validate(self) -> None:
        if not self.workload_id:
            raise EconomicOperationError("workload_id is required")
        values = (
            self.payload_bytes_written,
            self.state_read_bytes,
            self.artifact_count,
            self.verification_count,
            self.recovery_steps,
            self.settlement_units,
            self.availability_kib_hours,
            self.wall_clock_ms,
            self.cpu_time_ms,
            self.storage_bytes_read,
            self.storage_bytes_written,
            self.network_bytes_in,
            self.network_bytes_out,
        )
        if any(not isinstance(value, int) or isinstance(value, bool) or value < 0 for value in values):
            raise EconomicOperationError("observed resource values must be non-negative integers")


def as_transition(
    quote: OperationQuote,
    *,
    height: int,
    timestamp: int,
    epoch: int,
) -> Transition:
    if height < 1 or timestamp < 0 or epoch < 0:
        raise EconomicOperationError("invalid transition coordinates")
    return Transition(
        height=height,
        timestamp=timestamp,
        epoch=epoch,
        fees=((quote.payer, quote.base_fee_bod, quote.priority_fee_bod),),
    )


@dataclass(frozen=True)
class WorkloadSampleV0_1:
    sample_id: str
    payload_bytes: int
    artifact_count: int
    verification_count: int
    state_read_bytes: int
    recovery_steps: int
    settlement_units: int
    availability_kib: int
    network_in_bytes: int
    network_out_bytes: int
    base_fee_bod: int
    workload_fee_bod: int
    total_fee_bod: int


def measure_workload_v0_1(
    *,
    sample_id: str,
    payload_bytes: int,
    artifact_count: int,
    verification_count: int,
    policy: OperationPricingPolicyV0_1,
    state_read_bytes: int = 0,
    recovery_steps: int = 0,
    settlement_units: int = 0,
    availability_kib: int = 0,
    network_in_bytes: int = 0,
    network_out_bytes: int = 0,
) -> WorkloadSampleV0_1:
    quote = quote_project_operation(
        operation_id=sample_id,
        payer="measurement",
        payload_bytes=payload_bytes,
        artifact_count=artifact_count,
        verification_count=verification_count,
        state_read_bytes=state_read_bytes,
        recovery_steps=recovery_steps,
        settlement_units=settlement_units,
        availability_kib=availability_kib,
        network_in_bytes=network_in_bytes,
        network_out_bytes=network_out_bytes,
        policy=policy,
    )
    return WorkloadSampleV0_1(
        sample_id,
        payload_bytes,
        artifact_count,
        verification_count,
        state_read_bytes,
        recovery_steps,
        settlement_units,
        availability_kib,
        network_in_bytes,
        network_out_bytes,
        quote.base_fee_bod,
        quote.priority_fee_bod,
        quote.total_fee_bod,
    )


def workload_sweep_v0_1(*, policy: OperationPricingPolicyV0_1, payload_bytes=(0, 1, 1024, 1025, 4096, 16384), artifact_counts=(0, 1, 4), verification_counts=(0, 1, 4)) -> tuple[WorkloadSampleV0_1, ...]:
    return tuple(measure_workload_v0_1(sample_id=f"ec001-{p}b-{a}a-{v}v", payload_bytes=p, artifact_count=a, verification_count=v, policy=policy) for p, a, v in product(payload_bytes, artifact_counts, verification_counts))
