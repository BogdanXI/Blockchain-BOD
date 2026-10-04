import pytest

from src.bod_economy import (
    MAX_SUPPLY,
    EconomicError,
    State,
    Transition,
    Vesting,
    apply,
    genesis,
    scheduled_release,
)
from src.bod_simulation import run


def base_state():
    return genesis({"alice": 150_000_000, "vesting:dev": 150_000_000})


def test_genesis_conserves_cap():
    state = base_state()
    assert state.minted == 300_000_000
    assert state.unissued == 700_000_000
    assert state.minted + state.unissued == MAX_SUPPLY
    assert sum(state.balances.values()) == state.supply


def test_emission_is_deterministic_and_envelope_bounded():
    state = base_state()
    allowed = scheduled_release("ecosystem", 0, state.envelope_remaining["ecosystem"])
    tx = Transition(1, 1, 0, emissions=(("ecosystem", allowed),))
    a = apply(state, tx)
    b = apply(state, tx)
    assert a == b
    assert a.minted == state.minted + allowed
    assert a.unissued == state.unissued - allowed
    assert a.balances["ecosystem"] == allowed


def test_emission_above_schedule_is_rejected_without_parent_mutation():
    state = base_state()
    allowed = scheduled_release("ecosystem", 0, state.envelope_remaining["ecosystem"])
    with pytest.raises(EconomicError):
        apply(state, Transition(1, 1, 0, emissions=(("ecosystem", allowed + 1),)))
    assert state.height == 0
    assert state.minted == 300_000_000
    assert "ecosystem" not in state.balances


def test_priority_fee_split_and_base_fee_burn_conserve_supply():
    state = base_state()
    nxt = apply(state, Transition(1, 1, 0, fees=(("alice", 100, 200),)))
    assert nxt.burned == 100
    assert nxt.balances["alice"] == 149_999_700
    assert nxt.balances["proposer_arbitration"] == 100
    assert nxt.balances["verifier_pool"] == 60
    assert nxt.balances["treasury"] == 40
    assert sum(nxt.balances.values()) == nxt.supply


def test_bond_refund_distinguishes_noncanonical_from_invalid():
    state = base_state()
    locked = apply(state, Transition(1, 1, 0, bonds=(("alice:c1", "lock", 1_000),)))
    refunded = apply(locked, Transition(2, 2, 0, bonds=(("alice:c1", "noncanonical", 1_000),)))
    assert refunded.balances["alice"] == state.balances["alice"]

    relocked = apply(refunded, Transition(3, 3, 0, bonds=(("alice:c2", "lock", 2_000),)))
    slashed = apply(relocked, Transition(4, 4, 0, bonds=(("alice:c2", "invalid", 2_000),)))
    assert slashed.balances["alice"] == state.balances["alice"] - 2_000
    assert slashed.balances["treasury"] == 2_000


def test_developer_vesting_has_cliff_and_does_not_mint():
    vesting = Vesting("dev", 150_000_000, start_timestamp=0)
    state = genesis(
        {"alice": 150_000_000, "vesting:dev": 150_000_000},
        vestings={"dev": vesting},
    )
    with pytest.raises(EconomicError):
        apply(state, Transition(1, 31_536_000, 0, vesting_claims=(("dev", 1),)))

    timestamp = 31_536_000 + 31_536_000
    amount = vesting.vested(timestamp)
    nxt = apply(state, Transition(1, timestamp, 0, vesting_claims=(("dev", amount),)))
    assert nxt.minted == state.minted
    assert nxt.balances["dev"] == amount
    assert nxt.balances["vesting:dev"] == 150_000_000 - amount


def test_replay_and_time_regression_are_rejected():
    state = base_state()
    nxt = apply(state, Transition(1, 10, 0))
    with pytest.raises(EconomicError):
        apply(nxt, Transition(1, 11, 0))
    with pytest.raises(EconomicError):
        apply(nxt, Transition(2, 9, 0))


def test_simulation_is_reproducible_and_cap_safe():
    state = base_state()
    transitions = tuple(Transition(i + 1, i + 1, i) for i in range(8))
    a_state, a_results = run(state, transitions)
    b_state, b_results = run(state, transitions)
    assert a_state == b_state
    assert a_results == b_results
    assert all(row.supply <= MAX_SUPPLY for row in a_results)


def test_declining_schedule_is_monotone():
    values = [scheduled_release("security_verification", i, 250_000_000) for i in range(10)]
    assert all(a >= b for a, b in zip(values, values[1:]))


def test_failed_multi_operation_transition_is_atomic():
    state = base_state()
    allowed = scheduled_release("community", 0, state.envelope_remaining["community"])
    tx = Transition(
        1,
        1,
        0,
        emissions=(("community", allowed),),
        fees=(("alice", 999_999_999, 0),),
    )
    with pytest.raises(EconomicError):
        apply(state, tx)
    assert state.minted == 300_000_000
    assert state.unissued == 700_000_000
    assert state.balances["alice"] == 150_000_000


def test_treasury_spend_is_bounded_and_conservative():
    state = base_state()
    funded = apply(state, Transition(1, 1, 0, fees=(("alice", 0, 1_000),)))
    assert funded.balances["treasury"] == 200

    spent = apply(
        funded,
        Transition(2, 2, 0, treasury_spends=(("public_goods", 150),)),
    )
    assert spent.balances["treasury"] == 50
    assert spent.balances["public_goods"] == 150
    assert spent.minted == funded.minted
    assert spent.burned == funded.burned
    assert sum(spent.balances.values()) == spent.supply

    with pytest.raises(EconomicError):
        apply(
            spent,
            Transition(3, 3, 0, treasury_spends=(("public_goods", 51),)),
        )


def test_invalid_bond_settlement_and_duplicate_envelope_are_rejected():
    state = base_state()
    with pytest.raises(EconomicError):
        apply(state, Transition(1, 1, 0, bonds=(("alice:missing", "invalid", 100),)))

    with pytest.raises(EconomicError):
        apply(
            state,
            Transition(
                1,
                1,
                0,
                emissions=(("community", 1), ("community", 1)),
            ),
        )
