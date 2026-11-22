# BOD architecture overview

**Document status:** explanatory overview for the experimental v0.1 implementation.

## Purpose

BOD is a local-first continuity layer for software release evidence. It binds deterministic project-state commitments to references for evidence objects, links successive states through predecessor references, and supports independent verification and portable recovery of payload bytes included in an Evidence Bundle.

It is not a build system, provenance authority, vulnerability scanner, evidence-hosting service, blockchain, or replacement for Git, SLSA, in-toto, Sigstore, SPDX or CycloneDX.

## Data flow

1. **Capture.** The repository adapter enumerates the defined Git-tracked project boundary and computes file-level digests, byte sizes and Git-compatible file modes (regular non-executable `100644`, executable `100755`, symlink `120000`) before deriving a deterministic state root. New captures use snapshot v0.2; the verifier retains read compatibility for v0.1 snapshots, which did not commit to file mode.
2. **Describe evidence.** A versioned evidence envelope records evidence references and the project-state context. References commit to payload digests and metadata; they do not, by themselves, preserve payload availability.
3. **Link history.** A checkpoint identifies its predecessor. Graph verification checks relationships and reports forks and heads without selecting a canonical head.
4. **Package for portability.** Evidence Bundle v0.1 carries a checkpoint plus the exact bytes for referenced evidence payloads included in that bundle. The CLI can verify and safely extract those payloads into digest-derived filenames with a mapping manifest.
5. **Verify independently.** The verifier checks the encoded commitments, payload digests, metadata constraints, completeness and lineage predicates. External signature verification is delegated to the relevant upstream tooling.
6. **Optionally publish a witness.** The Ethereum registry can record compact commitments and predecessor references. This is independent of local verification and does not place evidence payloads on-chain.

## Trust boundaries

| Component | Establishes | Does not establish |
|---|---|---|
| Project snapshot | Byte digests, sizes and Git-compatible file modes for paths inside the captured boundary | That files are safe, correct or available later; full POSIX permissions, ownership, timestamps or extended attributes |
| Evidence envelope | Structured references and predecessor linkage | Truthfulness or authenticity of referenced statements |
| Evidence Bundle | Integrity and presence of payload bytes actually included | Availability of omitted evidence or semantic validity |
| Independent verifier | Conformance to implemented integrity and lineage checks | Correctness of every external format or trust policy |
| Sigstore tooling | Signature/identity verification according to its trust configuration | SBOM completeness or semantic correctness |
| Ethereum registry | Inclusion of a compact commitment in a chain history | Meaning, truth, safety or canonicality of the committed state |

## Branch semantics

The graph model preserves multiple valid successors to a predecessor. A fork is a property of the observed history, not automatically an error. Graph verification reports fork points and current heads; it does not choose a preferred head. Strict chain verification is available when a single linear path is required.

## Portability semantics

A checkpoint manifest is not a source archive. It records metadata and digests for the captured file boundary. The Evidence Bundle is the portable object that can carry actual referenced evidence payload bytes. Recovery guarantees therefore apply only to bytes included in a successfully verified bundle.

## Ethereum boundary

The Ethereum registry is an optional public witness for compact checkpoint commitments and predecessor references. It is not required for local capture, graph verification, bundle creation or bundle verification. No deployed contract, registered EAS schema, live attestation or independent contract audit is currently claimed.

## Implementation map

- `src/bod_project_state.py` — project-state capture and commitments.
- `src/bod_evidence_envelope.py` — evidence references, envelopes and lineage graph verification.
- `src/bod_portable.py` — portable checkpoints and Evidence Bundle operations.
- `src/bod_evidence_formats.py` — structural inspection of selected evidence formats.
- `src/bod_cli.py` — user-facing command-line interface.
- `scripts/independent_verify.py` — independent verification entry point.
- `protocol/ethereum/BODEthereumCheckpointRegistry.sol` — optional Ethereum checkpoint registry.
- `tools/eas/` — EAS client-side integration scripts.

## Validation still required

- Reproducible comparison against existing evidence stores and toolchains.
- Cross-platform validation of snapshot v0.2 mode semantics, especially Windows filesystems and Git `core.filemode` configurations.
- Independent review of protocol invariants and implementation.
- Broader CI-provider and evidence-format interoperability tests.
- Independent operator feedback and documented usability results.
- Smart-contract security review before any deployment.

See [Project Status](PROJECT_STATUS.md), [Threat Model](THREAT_MODEL_v0.1.md), [Evidence Bundle v0.1](EVIDENCE_BUNDLE_v0.1.md), and [Verification Experiment](VERIFICATION_EXPERIMENT.md).
