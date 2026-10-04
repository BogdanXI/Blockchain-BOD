# EC-0001 Economic Invariants v0.1

Status: analysis baseline; numerical parameters are not final protocol policy.

## Scope

These invariants define the minimum deterministic safety boundary for the BOD economic model. They are separate from consensus authority and do not claim a new consensus mechanism.

## Invariants

### I1 — Supply conservation

For every reachable epoch:

    minted + unissued = MAX_SUPPLY

and:

    minted <= MAX_SUPPLY
    unissued >= 0

Fee burn may reduce circulating supply but cannot create new supply.

### I2 — Verifier-budget coverage

For every admitted workload:

    admitted_candidates * candidate_reward <= verifier_budget

where:

    verifier_budget = base_verifier_budget + congestion_surcharge

No candidate is admitted merely because it was requested.

### I3 — Deterministic admission bound

For every epoch:

    0 <= admitted_candidates <= requested_candidates

and admission is a deterministic function of the finalized economic inputs.

### I4 — Invalid-work collateral coverage

For modeled invalid work:

    slashed_bond >= modeled_invalidity_harm

This invariant is required before a parameter set can be called robust against the modeled invalid-candidate harm envelope. A bond is collateral; it is not a substitute for verifier-work funding.

### I5 — Treasury runway

For every epoch:

    treasury_balance >= minimum_treasury

Congestion pricing routed to verifier capacity must not be silently counted as unrestricted treasury revenue.

### I6 — Developer concentration

For every epoch:

    developer_unlocked / circulating_supply <= max_developer_concentration

### I7 — Determinism

Identical finalized inputs, parameters and prior state must produce identical accounting outputs, including admission, fees, emission, bond accounting and state roots.

## Hybrid-control frontier evidence

The severe compound workload used by EC-0001 is a 25% fee-demand floor after year 3 and a 10x candidate-load multiplier from year 4 onward.

Across the complete 9,216-case bounded parameter grid:

- 7,872 cases retain full requested-work admission under the hybrid admission + congestion-pricing rule.
- 1,344 cases retain partial admission only.
- The worst tested minimum throughput is 35.00%; the best partial case is 97.81%.
- Partial-admission cases occur only at 500 or 1,000 BOD candidate reward in this grid; all 3,072 cases with a 250 BOD reward retain full admission.
- The congestion surcharge scales with the workload multiplier and reaches 9x the base reward, making the total modeled candidate cost 10x the base reward during the 10x-load years.

Within the previously stress-robust 96-case economic region, the hybrid preserves full admission for all 96 cases.

This frontier is capacity/affordability evidence only. It does not override I4 bond coverage, treasury constraints, or future verifier-staking rules, and it does not select final token parameters.

## Promotion gate

No numerical parameter is promoted to final policy until a candidate parameter set simultaneously satisfies I1-I6 across the declared baseline and adversarial workload envelope, with deterministic executable tests and recorded boundary cases.
