# BOD Evidence Fabric v0.1

BOD Evidence Fabric is a verification layer for digital state that survives replacement of the machine, process, CI runner or model runtime that produced it.

## The product

```text
SOURCE
  ↓
DETERMINISTIC SNAPSHOT
  ↓
EVIDENCE ENVELOPE
  ├── state root
  ├── predecessor state root
  ├── provenance / SBOM / attestation digests
  └── transition boundary
  ↓
VERIFIER
  ├── integrity
  ├── lineage
  ├── replay/fork detection
  └── project boundary
  ↓
OPTIONAL EXTERNAL ANCHOR
  ├── Arbitrum
  ├── another EVM network
  └── future BOD-native provider
  ↓
FRESH RUNTIME RECOVERY
```

The blockchain is an **anchor**, not the place where large evidence payloads are stored. The durable BOD object is a compact, deterministic commitment that can be reconstructed and independently verified.

## Why this is different from a simple hash registry

A single hash answers: "Did these bytes match?"

An Evidence Fabric answers:

> "What state existed, what transition produced it, what external evidence supports it, what state came before it, where was the result anchored, and can a fresh runtime independently recover and verify the same history?"

## Interoperability

BOD does not replace existing provenance formats. SLSA/in-toto provenance, CycloneDX SBOMs, Sigstore transparency records and other evidence remain owned by their source systems. BOD records their cryptographic digests and relationships.

This avoids creating another incompatible supply-chain format while adding cross-runtime continuity and external anchoring.

## Zero-cost development path

The reference workflow is deliberately usable without a paid blockchain service:

1. Git repository provides source state.
2. Local Python implementation creates deterministic snapshots and envelopes.
3. Public CI or a self-hosted runner executes verification.
4. External blockchain anchoring is optional during development.
5. Testnet transactions use test tokens when an external anchor is useful.

Production economics are a separate gate. No experimental token parameter is implied by this product layer.

## Current maturity

- deterministic repository snapshot: implemented;
- versioned Evidence Envelope v0.1: implemented;
- lineage verification: implemented;
- adversarial verification: implemented;
- fresh-process recovery experiments: implemented;
- external anchor adapter: existing experimental path;
- production security: **not claimed**;
- production economic policy: **not final**.
