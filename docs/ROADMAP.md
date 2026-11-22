# Public roadmap

The project advances by reproducible evidence, not promotional dates. The active chain-facing scope is limited to an optional Ethereum L1 checkpoint witness and Ethereum Sepolia validation; the continuity core remains chain-independent.

## 1. Portable continuity core

**Status: implemented; regression-gated.**

- deterministic repository snapshots;
- versioned evidence envelopes and predecessor links;
- independent verification;
- portable checkpoints and fresh-process recovery.

Gate: clean-checkout reproduction and passing CI for the reviewed commit.

## 2. Ethereum checkpoint registry

**Status: implemented in source; testnet deployment not started.**

- permissionless append-only checkpoint records;
- parent-project and sequence validation;
- no mutable canonical-head pointer;
- explicit fork visibility;
- no token, custody, owner or upgrade authority.

Gate: Foundry tests, independent contract review, deployment rehearsal on Sepolia, verified source/bytecode and a public verification procedure.

## 3. Supply-chain evidence integration

**Status: partially implemented.**

- EAS SDK schema-registration and linked-attestation scripts are present; no live schema registration is claimed.
- ingest SLSA/in-toto provenance references;
- ingest SPDX/CycloneDX SBOM digests;
- bind Sigstore/Rekor and/or EAS attestation references;
- publish an end-to-end example from a real GitHub Actions build;
- define privacy and retention boundaries.

Gate: an independent maintainer can reproduce the release record, verify EAS lineage and validate referenced evidence without BOD-hosted services.

## 4. Product-value experiment

**Status: planned.**

Compare BOD with a baseline built from Git, SLSA/in-toto and Sigstore/EAS. Measure time to reconstruct a release, missing context, integrity failures, operator steps, gas cost and recovery correctness. Publish methodology, datasets and negative results.

Gate: at least two independent project maintainers reproduce the experiment.

## 5. Independent security review

**Status: required before public testnet promotion.**

Review contract invariants, chain reorg/finality assumptions, checkpoint identity, event indexing, off-chain evidence availability, key management and CI workflow permissions.

Gate: findings published, critical/high issues resolved, and regression tests added.

## 6. Ethereum Sepolia pilot

**Status: blocked pending review.**

- deploy the registry to chain ID 11155111;
- anchor synthetic and then public-safe release checkpoints;
- verify reads through independent RPC providers and a block explorer;
- publish reproducible gas and cost observations.

Gate: independently reproducible transaction, deployed bytecode, source verification and checkpoint reconstruction.

## 7. Mainnet decision

**Status: not started.**

Requires demonstrated user value, independent security review, operational monitoring, reorg/finality policy, incident response, privacy review and measured sustainable cost. Mainnet deployment is not a current milestone promise.

## Explicit non-goals

- creating or operating an Ethereum L2 or other BOD-owned chain;
- issuing a BOD token to make the product work;
- replacing Git, SLSA, in-toto, Sigstore, SPDX, CycloneDX or EAS;
- treating an anchor as proof of semantic truth or canonicality.
