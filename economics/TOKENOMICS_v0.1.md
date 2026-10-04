# BOD Tokenomics v0.1

Status: proposed economic architecture

## 1. Monetary objective

Native token: BOD (provisional symbol).

Maximum supply: 1,000,000,000 BOD.

The protocol has a hard maximum supply. There is no discretionary admin mint and no perpetual inflation target.

This separates the economic design into:

- fixed maximum supply;
- deterministic release/emission from the unissued reserve;
- fee recycling and fee burning;
- rewards for verified protocol work.

## 2. Genesis allocation

| Allocation | BOD | Share | Purpose |
|---|---:|---:|---|
| Developer / founder | 150,000,000 | 15% | Long-term development incentive |
| Network security & verification reserve | 250,000,000 | 25% | Validator/verifier/arbitration incentives |
| Ecosystem & applications | 200,000,000 | 20% | Grants, integrations, adoption incentives |
| Treasury | 150,000,000 | 15% | Long-term protocol and operating reserve |
| Community | 150,000,000 | 15% | Public distribution and participation |
| Liquidity & market infrastructure | 50,000,000 | 5% | Initial and maintenance liquidity |
| Research & public goods | 50,000,000 | 5% | Protocol research, audits, tooling |
| **Total** | **1,000,000,000** | **100%** | |

The 15% developer allocation is a contractual allocation, not an immediate unrestricted transfer.

## 3. Initial issuance and unissued reserve

Proposed genesis issuance: 300,000,000 BOD.

Genesis buckets:

- 150,000,000 BOD developer/founder vesting contract;
- 100,000,000 BOD community distribution pool;
- 50,000,000 BOD liquidity/market infrastructure reserve.

The remaining 700,000,000 BOD is unissued protocol reserve.

The unissued reserve can only enter circulation through deterministic emission rules. It is not a discretionary treasury balance and cannot be transferred by an operator.

## 4. Developer vesting

Developer/founder allocation:

- 12-month cliff;
- then 36-month linear vesting;
- no acceleration by ordinary governance;
- no protocol-level privileged transfer path;
- every unlock is visible on-chain.

This is intended to reduce early concentration and align the developer allocation with continued protocol development.

## 5. Emission architecture

The 700M unissued reserve is divided into protocol-controlled emission envelopes:

- security & verification: 250M;
- ecosystem: 200M;
- treasury: 150M;
- community: 50M;
- research/public goods: 50M.

Each envelope has:

- a maximum lifetime amount;
- an emission start epoch;
- an emission end epoch;
- a deterministic per-epoch release function;
- an unused-balance rule.

### Default emission policy

The v0.1 implementation should use declining annual envelopes rather than permanent inflation.

For each envelope:

    release_e = min(remaining_envelope, scheduled_release(e))

The schedule must be deterministic from genesis parameters and epoch number.

A later parameter change may reduce future release but must never increase the hard cap or retroactively mint missed emissions.

### Current simulation baseline

For executable v0.1 simulations only, the current provisional schedule releases at most 5% of each envelope's original amount in epoch 0 and multiplies that annual release by 90% for each subsequent epoch, for at most 100 epochs. This is a calibration baseline, not a final monetary-policy decision. Any replacement must remain deterministic and preserve the hard cap and envelope ceilings.

## 6. Fees

The protocol should use two fee components:

1. Base fee — protocol-computed congestion price.
2. Priority fee — optional payment for ordering/inclusion service.

Proposed initial split:

- base fee: 100% burned;
- priority fee: 50% proposer/arbitration reward, 30% verifier reward pool, 20% treasury.

The split is a design parameter for simulation and may change after adversarial economic testing.

The base-fee mechanism should be history-dependent and deterministic so a block producer cannot directly set the base fee for its own transactions.

## 7. Candidate bond

Every candidate transition carries a BOD bond.

- Valid + canonical: bond returned, less protocol-defined processing cost if any.
- Valid + non-canonical: bond returned unless the protocol defines an explicit anti-spam cost.
- Invalid: bond is partially or fully slashed according to the fault class.
- Proven fraud/equivocation: stronger slash.

A bond is economic accountability, not consensus authority by itself.

## 8. Verification rewards

Verification rewards are paid only for protocol-defined verification work.

A verifier must produce evidence that can be linked to:

- candidate hash;
- parent state;
- verification policy;
- execution environment;
- verification result.

The protocol must avoid paying for duplicate low-value attestations merely because more signatures were submitted.

## 9. Treasury

The treasury is a protocol account with no private key.

Treasury inflows:

- scheduled treasury emissions;
- 20% of priority fees under the v0.1 proposal;
- penalties/bonds only where the protocol explicitly routes them to treasury.

Treasury outflows require the protocol's governance/authorization mechanism and cannot exceed the available treasury balance.

## 10. Supply accounting

Let:

- M = cumulative minted BOD;
- B = cumulative burned BOD;
- U = remaining unissued reserve.

Then:

    M + U = 1,000,000,000 BOD

and circulating/effective supply is derived from minted balances minus burned balances.

For every state transition:

    M_next = M + mint
    U_next = U - mint
    Supply_next = Supply + mint - burn

with:

    0 <= U_next
    M_next <= 1,000,000,000

No fee burn can create new minting authority.

## 11. Economic attack surface

The implementation and simulations must test:

- validator/verifier collusion;
- Sybil verifier flooding;
- candidate spam;
- fake evidence;
- duplicate verification;
- self-dealing through proposer/verifier roles;
- fee manipulation;
- emission timing games;
- treasury capture;
- developer allocation concentration;
- governance capture;
- short-term liquidity extraction;
- coordinated selling around unlocks;
- invalid-candidate griefing;
- withholding valid candidates;
- concurrent-candidate arbitration games.

## 12. Design status

This is a protocol design baseline, not a claim that the economic parameters are optimal.

Before mainnet, the parameters require executable simulation and adversarial mechanism testing.
