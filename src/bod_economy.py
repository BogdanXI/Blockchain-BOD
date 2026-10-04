"""Deterministic BOD economic state transition."""
from dataclasses import dataclass, field, replace
from typing import Mapping, Tuple

MAX_SUPPLY = 1_000_000_000
GENESIS_MINTED = 300_000_000
GENESIS_UNISSUED = 700_000_000
BPS = 10_000
EMISSION_INITIAL_BPS = 500
EMISSION_DECAY_BPS = 9_000
EMISSION_MAX_EPOCHS = 100

ENVELOPE_CAPS = {
    "security_verification": 250_000_000,
    "ecosystem": 200_000_000,
    "treasury": 150_000_000,
    "community": 50_000_000,
    "research_public_goods": 50_000_000,
}


class EconomicError(ValueError):
    pass


@dataclass(frozen=True)
class Vesting:
    beneficiary: str
    total: int
    start_timestamp: int
    cliff_seconds: int = 31_536_000
    linear_seconds: int = 94_608_000
    claimed: int = 0

    def vested(self, timestamp: int) -> int:
        cliff_end = self.start_timestamp + self.cliff_seconds
        if timestamp <= cliff_end:
            return 0
        elapsed = min(timestamp - cliff_end, self.linear_seconds)
        return self.total * elapsed // self.linear_seconds

    def claimable(self, timestamp: int) -> int:
        return self.vested(timestamp) - self.claimed


@dataclass(frozen=True)
class Bond:
    owner: str
    amount: int


@dataclass(frozen=True)
class State:
    height: int
    timestamp: int
    balances: Mapping[str, int]
    minted: int
    burned: int
    unissued: int
    envelope_remaining: Mapping[str, int]
    vestings: Mapping[str, Vesting] = field(default_factory=dict)
    bonds: Mapping[str, Bond] = field(default_factory=dict)

    @property
    def supply(self) -> int:
        return self.minted - self.burned


@dataclass(frozen=True)
class Transition:
    height: int
    timestamp: int
    epoch: int
    emissions: Tuple[Tuple[str, int], ...] = ()
    fees: Tuple[Tuple[str, int, int], ...] = ()
    bonds: Tuple[Tuple[str, str, int], ...] = ()
    vesting_claims: Tuple[Tuple[str, int], ...] = ()
    treasury_spends: Tuple[Tuple[str, int], ...] = ()


def genesis(balances: Mapping[str, int], timestamp: int = 0, vestings: Mapping[str, Vesting] | None = None) -> State:
    copy = dict(balances)
    if any(not isinstance(v, int) or v < 0 for v in copy.values()):
        raise EconomicError("invalid genesis balance")
    if sum(copy.values()) != GENESIS_MINTED:
        raise EconomicError("genesis balances must sum to configured minted supply")
    return State(
        height=0,
        timestamp=timestamp,
        balances=copy,
        minted=GENESIS_MINTED,
        burned=0,
        unissued=GENESIS_UNISSUED,
        envelope_remaining=dict(ENVELOPE_CAPS),
        vestings=dict(vestings or {}),
        bonds={},
    )


def scheduled_release(envelope: str, epoch: int, remaining: int) -> int:
    if envelope not in ENVELOPE_CAPS or epoch < 0 or remaining < 0:
        raise EconomicError("invalid emission schedule input")
    if epoch >= EMISSION_MAX_EPOCHS:
        return 0
    annual = ENVELOPE_CAPS[envelope] * EMISSION_INITIAL_BPS // BPS
    for _ in range(epoch):
        annual = annual * EMISSION_DECAY_BPS // BPS
    return min(remaining, annual)


def apply(state: State, tx: Transition) -> State:
    if tx.height != state.height + 1:
        raise EconomicError("non-sequential height")
    if tx.timestamp < state.timestamp:
        raise EconomicError("time moved backwards")
    if tx.epoch < 0:
        raise EconomicError("negative epoch")

    balances = dict(state.balances)
    remaining = dict(state.envelope_remaining)
    vestings = dict(state.vestings)
    bonds = dict(state.bonds)
    minted_delta = 0
    burned_delta = 0

    seen = set()
    for envelope, amount in tx.emissions:
        if envelope in seen:
            raise EconomicError("duplicate envelope")
        seen.add(envelope)
        if amount <= 0 or envelope not in remaining:
            raise EconomicError("invalid emission")
        if amount > scheduled_release(envelope, tx.epoch, remaining[envelope]):
            raise EconomicError("emission exceeds schedule")
        remaining[envelope] -= amount
        balances[envelope] = balances.get(envelope, 0) + amount
        minted_delta += amount

    for payer, base_fee, priority_fee in tx.fees:
        if base_fee < 0 or priority_fee < 0:
            raise EconomicError("negative fee")
        total = base_fee + priority_fee
        if balances.get(payer, 0) < total:
            raise EconomicError("fee exceeds balance")
        balances[payer] -= total
        burned_delta += base_fee
        proposer = priority_fee * 5_000 // BPS
        verifier = priority_fee * 3_000 // BPS
        treasury = priority_fee - proposer - verifier
        balances["proposer_arbitration"] = balances.get("proposer_arbitration", 0) + proposer
        balances["verifier_pool"] = balances.get("verifier_pool", 0) + verifier
        balances["treasury"] = balances.get("treasury", 0) + treasury

    for candidate, action, amount in tx.bonds:
        if amount <= 0:
            raise EconomicError("invalid bond amount")
        if action == "lock":
            if candidate in bonds:
                raise EconomicError("duplicate bond")
            owner = candidate.split(":", 1)[0]
            if balances.get(owner, 0) < amount:
                raise EconomicError("bond exceeds balance")
            balances[owner] -= amount
            balances["bond:" + candidate] = amount
            bonds[candidate] = Bond(owner, amount)
        else:
            bond = bonds.pop(candidate, None)
            if bond is None or bond.amount != amount:
                raise EconomicError("invalid bond settlement")
            escrow = "bond:" + candidate
            if balances.get(escrow, 0) != amount:
                raise EconomicError("bond escrow mismatch")
            balances[escrow] -= amount
            if action in ("canonical", "noncanonical"):
                balances[bond.owner] = balances.get(bond.owner, 0) + amount
            elif action == "invalid":
                balances["treasury"] = balances.get("treasury", 0) + amount
            else:
                raise EconomicError("unknown bond action")

    for beneficiary, amount in tx.vesting_claims:
        if amount <= 0:
            raise EconomicError("invalid vesting claim")
        vesting = vestings.get(beneficiary)
        if vesting is None or amount > vesting.claimable(tx.timestamp):
            raise EconomicError("claim exceeds vested amount")
        source = "vesting:" + beneficiary
        if balances.get(source, 0) < amount:
            raise EconomicError("vesting source underfunded")
        balances[source] -= amount
        balances[beneficiary] = balances.get(beneficiary, 0) + amount
        vestings[beneficiary] = replace(vesting, claimed=vesting.claimed + amount)

    for recipient, amount in tx.treasury_spends:
        if not recipient or amount <= 0:
            raise EconomicError("invalid treasury spend")
        if balances.get("treasury", 0) < amount:
            raise EconomicError("treasury spend exceeds balance")
        balances["treasury"] -= amount
        balances[recipient] = balances.get(recipient, 0) + amount

    minted = state.minted + minted_delta
    burned = state.burned + burned_delta
    unissued = sum(remaining.values())

    if minted > MAX_SUPPLY or minted + unissued != MAX_SUPPLY:
        raise EconomicError("supply cap invariant failed")
    if any(v < 0 for v in balances.values()):
        raise EconomicError("negative balance")
    if sum(balances.values()) != minted - burned:
        raise EconomicError("balance conservation failed")

    return State(tx.height, tx.timestamp, balances, minted, burned, unissued, remaining, vestings, bonds)
