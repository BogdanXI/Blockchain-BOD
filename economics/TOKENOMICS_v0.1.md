# BOD Tokenomics v0.1 — Experimental Calibration Boundary

**Status:** experimental; not final monetary policy.

## Current EC-0001 candidate

| Parameter | Candidate |
|---|---:|
| Maximum supply | 100,000,000 BOD |
| Genesis minted supply | 25,000,000 BOD |
| Founder allocation | 5,000,000 BOD (5%), locked at genesis |
| Initial circulation | 20,000,000 BOD |
| Unissued issuance capacity | 75,000,000 BOD |

The founder allocation is a fixed ownership-policy variable. It does not create privileged future minting authority. Unissued capacity is not an account balance and is not owned by the founder or treasury.

## Economic direction

EC-0001 is calibrated revenue-first:

1. real service demand creates protocol revenue;
2. verifier, proposer and treasury operating costs are explicit;
3. candidate bonds cover modeled invalid-work harm;
4. bootstrap issuance is bounded;
5. usage-linked burn may be used as a monetary-policy mechanism, but burn is not treated as the source of business revenue.

The feasible region is solved first in abstract economic units. Only surviving regions are mapped into BOD units.

## Remaining allocation policy

The current candidate fixes the founder boundary and initial circulation boundary above. Final long-term allocations for security, treasury, ecosystem, liquidity, research and community are **not promoted** by this document.

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
