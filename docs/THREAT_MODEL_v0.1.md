# BOD Evidence Fabric — Threat Model v0.1

## Security claim boundary

BOD proves only predicates that its verifier actually checks.

A successful BOD verification may establish that:
1. canonical envelope bytes match their commitment;
2. declared state roots and evidence digests are bound to that envelope;
3. predecessor relationships are valid for the supplied history;
4. a published Ethereum checkpoint matches the supplied commitments and can be read from the selected chain history.

It does **not** establish that evidence is truthful, builds are secure, referenced artifacts remain available, publishers are authorized, source code is correct, or an Ethereum transaction makes a BOD transition valid or canonical.

## Adversaries

### Evidence fabricator

Can create false reports, logs or attestations. BOD can bind the resulting bytes but cannot determine whether the producer lied. Consumers must verify upstream signatures, identities and policies.

### Evidence mutator

Changes an evidence file after capture. A digest mismatch should cause verification failure when the bytes are available.

### History rewriter

Removes predecessors, injects forks, replays roots or crosses project boundaries. The local verifier checks supplied lineage; the Ethereum registry checks parent existence, project identity and sequence. Forks are allowed and deliberately visible.

### Compromised CI/runtime

Controls the machine that produced evidence. BOD preserves the declared evidence and lineage but does not turn a compromised builder into a trustworthy builder.

### Malicious publisher

Publishes arbitrary commitments or competing branches. The Ethereum registry is permissionless and records the sender, but does not authenticate repository ownership. Consumers must verify signed provenance or an independent authorization policy.

### RPC/indexer compromise

Returns incomplete or misleading chain data. Critical verification must use independent RPC providers, check chain ID, transaction receipt, contract address and event/storage data, and apply a documented finality threshold.

### Chain reorganization

A recent checkpoint may be removed by a reorg. A receipt is not finality. Clients must wait for an appropriate confirmation/finality condition and retain the block hash and transaction receipt.

### Verifier bug

One implementation may accept an invalid envelope. BOD publishes an independent verifier; cross-implementation vectors and external review remain required.

## Ethereum contract boundaries

- Permissionless publication is not repository authorization.
- Append-only storage is not canonical branch selection.
- The contract stores commitments, not source or evidence payloads.
- Block timestamps are approximate.
- No owner, upgrade key, ERC-20, custody or settlement authority exists in the Ethereum registry.
- No formal verification or external smart-contract audit has been completed.

## Required verifier result

The verifier must distinguish:
- integrity validity;
- policy acceptance;
- semantic truth (not asserted);
- evidence availability (unknown unless retrieval was performed);
- chain inclusion and finality status.

Passing a lower trust layer never upgrades a higher layer automatically.
