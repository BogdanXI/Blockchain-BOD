# BOD Evidence Fabric — Threat Model v0.1

## Security claim boundary

BOD proves only predicates that its verifier actually checks.

A successful BOD verification may establish that:
1. canonical envelope bytes match their commitment;
2. declared state roots and evidence digests are bound to that envelope;
3. predecessor relationships are valid for the supplied history;
4. a published Ethereum checkpoint matches the supplied commitments and can be read from the selected chain history.

It does **not** establish that evidence is truthful, builds are secure, referenced artifacts remain available, publishers are authorized, source code is correct, or an Ethereum transaction makes a BOD transition valid or canonical.

## Privacy and data disclosure\n\nHashes and fixed-size commitments are not anonymization. Predictable values may be guessed, and public metadata can be correlated with repositories, organizations, wallet activity or release timing. The current public-surface scanner covers selected high-confidence credential patterns and private path names only; it is not comprehensive DLP. Operators must review checkpoint contents before publication and keep source, evidence payloads, secrets and personal data off-chain. See [Privacy Model](PRIVACY_MODEL.md).\n\n## Adversaries

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

### Path, mode and symlink abuse

Repository capture hashes a tracked symlink's link target rather than dereferencing the target and reading arbitrary external file contents. Snapshot v0.2 records Git-compatible file modes (`100644`, `100755`, `120000`) so an executable-bit change alters the state root. Snapshot verification rejects absolute paths, traversal components, non-normalized paths, duplicate/unsorted entries, invalid modes and invalid size/digest types. Snapshot v0.1 remains readable but cannot prove that an executable-bit distinction was captured. These checks reduce path confusion and accidental data capture; they do not replace OS sandboxing or a review of the capture boundary.

## Data availability and exit paths\n\nA commitment proves a relationship to bytes only when those bytes can be obtained. Ethereum, EAS and a digest do not guarantee artifact availability. A production workflow must provide independently controlled artifact locations, retrieval checks and a documented recovery path if a repository host, CI provider, indexer or RPC endpoint disappears. These capabilities are not yet demonstrated end-to-end.\n\n## Ethereum contract boundaries

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
