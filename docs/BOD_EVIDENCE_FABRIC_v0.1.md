# BOD Evidence Fabric v0.1

## Purpose

BOD is an experimental verification layer for digital project state. It creates deterministic state commitments, binds them to versioned evidence references and predecessor relationships, and allows portable checkpoints to be verified in a separate runtime.

The project is testing a focused hypothesis:

> A portable continuity record can make it easier to verify which project state was captured, which evidence was associated with it, and how successive states relate after the original workspace is unavailable.

This hypothesis requires independent user and technical validation.

## Processing model

```text
GIT-TRACKED WORKING TREE
          |
          v
DETERMINISTIC SNAPSHOT
  ordered paths, digests, sizes
          |
          v
EVIDENCE ENVELOPE
  state root
  predecessor state root
  provenance / SBOM / attestation digests
  capture boundary
          |
          v
REFERENCE + INDEPENDENT VERIFICATION
          |
          v
OPTIONAL EXTERNAL WITNESS
```

## Current data boundary

The current repository snapshot contains file paths, SHA-256 digests and byte sizes for Git-tracked working-tree files. It does not embed source files or external evidence payloads.

A portable checkpoint can therefore be independently checked for integrity and lineage, but it is not a backup archive and does not restore the original repository contents. Actual payload retrieval or restoration requires a separately designed storage and availability layer.

## Interoperability

BOD does not replace existing provenance formats. SLSA/in-toto provenance, CycloneDX or SPDX inventories, Sigstore transparency records and other evidence remain owned by their source systems. BOD records references and cryptographic digests for those objects.

This approach avoids redefining upstream formats while testing whether a cross-system continuity layer provides additional value.

## External anchoring

A blockchain is optional infrastructure, not the definition of BOD.

## Current maturity

- deterministic repository snapshot: implemented;
- Evidence Envelope v0.1: implemented;
- predecessor-linked lineage verification: implemented;
- portable checkpoint format: implemented;
- reference CLI verification: implemented;
- independent verifier: implemented; parity hardening remains ongoing;
- source-payload restoration from portable checkpoints: **not implemented**;
- external anchor adapter: experimental;
- production security and consensus: **not claimed**;
- production economic policy: **not final**.
