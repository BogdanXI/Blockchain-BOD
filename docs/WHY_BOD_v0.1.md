# Why BOD Exists — v0.1 Product Boundary

## The problem we are actually solving

BOD is **not** a replacement for SLSA, in-toto, Sigstore, CycloneDX or Git.

Those systems already solve important parts of provenance, signing, transparency and software inventory.

BOD's product hypothesis is narrower:

> **Digital evidence often exists as separate artifacts and attestations, but a project also needs a portable, deterministic history that binds successive project states to those external evidence objects and can be independently reconstructed after the original runtime disappears.**

That hypothesis is not yet a proven market fact. The repository treats it as an engineering hypothesis and measures it with executable recovery tests.

## What BOD owns

BOD owns:

- deterministic state-root creation;
- versioned Evidence Envelope serialization;
- predecessor/state continuity;
- replay and fork detection;
- project-boundary checks;
- portable verification reports;
- optional external witnessing.

## What BOD does not own

BOD deliberately does not redefine:

- SLSA provenance semantics;
- in-toto statement semantics;
- SBOM semantics;
- Sigstore signing or transparency semantics;
- source-control semantics;
- build correctness;
- business correctness.

External evidence is referenced by digest and remains governed by its originating system.

## Comparison

| Capability | Existing ecosystem | BOD role |
|---|---|---|
| Source history | Git | consume source state |
| Build provenance | SLSA / in-toto | reference and bind |
| Signing/transparency | Sigstore / Rekor | reference and optionally anchor |
| Software inventory | CycloneDX / SPDX | reference |
| Single state commitment | hashes/Merkle trees | deterministic state root |
| Longitudinal project continuity | fragmented across systems | BOD evidence chain |
| Cross-runtime reconstruction | tool-specific | BOD verification artifact |
| External witnessing | transparency logs / blockchains | provider-neutral optional layer |

The differentiator is therefore **continuity and portability**, not hashing, signatures, provenance or blockchain inclusion by themselves.

## Why the blockchain is optional

A blockchain is useful only when an independent external witness is valuable.

Local development:

```text
state -> envelope -> verify
```

Public transparency:

```text
state -> envelope -> verify -> transparency log
```

External chain witness:

```text
state -> envelope -> verify -> EVM anchor
```

A BOD deployment must remain useful when no blockchain is available.

## Why this survives the strongest criticism

The product does not claim:

> "BOD proves the evidence is true."

It claims:

> "BOD proves exactly which evidence and state history were committed, and exposes the trust boundaries that still require independent verification."

That is a smaller claim, but it is testable.

## Exit condition for the product hypothesis

BOD should not be marketed as a differentiated product until independent users can demonstrate that the continuity/recovery layer saves them a material verification or audit step compared with their existing SLSA/Sigstore/Git workflow.

The next product experiment is therefore not another blockchain transaction. It is a reproducible cross-system recovery scenario with independent verification.
