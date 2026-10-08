# BOD Tokenomics v0.1 — Experimental Calibration Boundary

**Status:** experimental; not final monetary policy.

## Current calibration candidate

EC-0001 currently uses:

| Parameter | Candidate |
|---|---:|
| Maximum supply | 100,000,000 BOD |
| Genesis minted supply | 25,000,000 BOD |
| Unissued capacity | 75,000,000 BOD |

These values are **calibration inputs**, not a production-token launch specification.

## Economic direction

The current EC-0001 model is revenue-first:

1. real service demand creates protocol revenue;
2. verifier, proposer and treasury operating costs are explicit;
3. candidate bonds cover modeled invalid-work harm;
4. bootstrap issuance is bounded rather than treated as permanent revenue;
5. usage-linked burn may be used as a monetary-policy mechanism, but burn is not treated as the source of business revenue.

The feasible region is solved first in abstract economic units. Only surviving regions are mapped into BOD units.

## Allocation status

Founder, community, treasury, liquidity, security and research allocation percentages are **not final** in this public v0.1 surface. They must not be inferred from historical parameter sets.

Older 1,000,000,000 BOD / 300,000,000 genesis configurations are historical calibration baselines and are not the current EC-0001 candidate.

## Promotion gate

No numerical parameter is promoted to final policy until the coupled EC-0001 constraints survive deterministic multi-year and adversarial verification, including:

- supply conservation;
- sustainable service pricing;
- verifier/proposer cost coverage;
- invalid-work bond coverage;
- treasury runway;
- concentration limits;
- deterministic accounting.

A failing scenario is preserved as evidence rather than removed by weakening the acceptance criteria.

## Security boundary

The token model does not establish consensus authority or production security. Arbitrum integration evidence is an application/integration test boundary only.

See economics/EC_0001_INVARIANTS_v0.1.md for the public invariant boundary.
