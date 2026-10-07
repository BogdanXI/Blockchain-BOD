# BOD checkpoint economics — experiment v0.1

Status: experimental measurement design

## Question

How often should BOD checkpoint a project's durable state so that integrity, recovery cost, transaction cost and developer friction are jointly acceptable?

The project will answer this from measurements rather than selecting the checkpoint interval from the token model.

## First workload

Blockchain-BOD itself is the first controlled workload.

Path:

`Git commit -> deterministic snapshot -> stateRoot -> Arbitrum Sepolia checkpoint -> recovery/verification`

The Arbitrum checkpoint is an external commitment/timestamp layer. It is not BOD consensus and does not prove semantic correctness.

## Zero-click operation after bootstrap

The intended runtime is:

`git push -> GitHub Actions -> snapshot -> technical signer/relayer -> Arbitrum Sepolia`

MetaMask is not required for every checkpoint. A one-time operator/bootstrap step is separated from the recurring automation path.

For the current testnet implementation, a dedicated GitHub Environment signer may be used. A mature deployment should move the signing boundary to a narrowly scoped relayer/workload-identity service.

## Measurement variables

For every successful checkpoint measure:

- checkpoint artifact size;
- Git commits batched into the checkpoint;
- capture time;
- workflow latency;
- gas used;
- effective gas price;
- native transaction fee;
- block inclusion latency;
- retry count;
- recovery verification time;
- controlled work lost before recovery.

## Policies to compare

- every meaningful commit;
- every N commits;
- fixed time interval;
- successful CI;
- release/tag;
- hybrid time + commit bound.

The current experimental branch uses a 30-minute scheduled policy to create a first controlled baseline. It is not a production recommendation.

## Economic objective

For interval T, evaluate:

`checkpoint_cost(T) + expected_recovery_loss(T) + operational_friction(T)`

The experiment must keep these components separate before mapping them into BOD token units.

The resulting feasible region becomes input to EC-0001. It must not be reverse-engineered to make the current 100M experimental supply target pass.

## Security

No source code, prompts, secrets, private project state or AI context is written to the public checkpoint contract. Only typed commitments are anchored.

No production-security or production-economics claim is made from this experiment.
