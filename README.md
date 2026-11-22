# BOD — Evidence Fabric

![BOD Evidence Fabric](docs/assets/bod-mark.svg)

**Portable, independently verifiable continuity for digital project state.**

[![CI](https://github.com/BogdanXI/Blockchain-BOD/actions/workflows/ci.yml/badge.svg)](https://github.com/BogdanXI/Blockchain-BOD/actions/workflows/ci.yml)
[![License](https://img.shields.io/badge/license-MIT-111827.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.11%2B-111827.svg)](pyproject.toml)
[![Status](https://img.shields.io/badge/status-experimental-orange.svg)](docs/PROJECT_STATUS.md)

[Getting started](docs/GETTING_STARTED.md) · [Project status](docs/PROJECT_STATUS.md) · [Roadmap](docs/ROADMAP.md) · [Architecture](protocol/ARCHITECTURE_v0.1.md) · [Threat model](docs/THREAT_MODEL_v0.1.md) · [Security](SECURITY.md)

---

## Overview

BOD is an experimental Evidence Fabric for creating deterministic commitments to digital project state, binding those commitments to a versioned evidence envelope, and verifying predecessor-linked history independently of the runtime that created it.

The project addresses a specific engineering question:

> Can a portable continuity record make it materially easier to verify what state was captured, which evidence was associated with it, and how one state follows another after the original workspace is no longer available?

This is a product hypothesis under validation, not an established market claim.

## The problem

Git records source history. Provenance and signing systems describe how artifacts were produced and who attested to them. Transparency logs and blockchains can provide external witnesses.

Those systems are complementary, but a project may still need a portable record that binds a sequence of project-state commitments to references to external evidence and can be checked in a clean runtime.

**BOD focuses on that continuity layer.** It is designed to compose with existing tools, not replace them.

## How it works

```text
GIT-TRACKED PROJECT STATE
          |
          v
DETERMINISTIC SNAPSHOT
  ordered paths, digests, sizes
          |
          v
VERSIONED EVIDENCE ENVELOPE
  state root, predecessor, evidence references
          |
          v
PORTABLE CHECKPOINT
          |
          +------> REFERENCE VERIFIER
          |
          +------> INDEPENDENT VERIFIER
          |
          +------> OPTIONAL EXTERNAL ANCHOR
```

The external anchor is optional. It is a witness for a commitment; it does not determine whether the BOD envelope or the underlying evidence is semantically correct.

## What is implemented

- Deterministic snapshots of Git-tracked working-tree files.
- Versioned Evidence Envelope v0.1 with canonical serialization and self-verifying commitments.
- Predecessor-linked state history with checks for missing predecessors, duplicate roots, forks and disconnected components.
- Portable checkpoint format binding a snapshot to its evidence envelope.
- A Python CLI for demonstration, snapshot capture, evidence creation and verification.
- A second verifier that does not import the reference implementation.
- Tests and a public CI workflow.
- An experimental Arbitrum Sepolia anchoring path.

Implementation details and limits are documented in [Project Status](docs/PROJECT_STATUS.md) and the [Threat Model](docs/THREAT_MODEL_v0.1.md).

## Important scope boundary

**A BOD checkpoint is a verification record, not a backup archive.**

The repository snapshot currently records tracked file paths, SHA-256 digests and sizes. It does not embed the source files or other payloads. The `bod recover` command verifies the checkpoint and reports the captured state metadata; it does not recreate the original files.

Likewise, a successful integrity check does not prove that a claim is true, that the evidence is available, that the producer was honest, or that an external anchor is canonical.

BOD v0.1 is experimental. It is not a production blockchain, a native consensus network, a production token or a production security certification.

## Quick start

Requirements: Python 3.11 or newer.

```bash
git clone https://github.com/BogdanXI/Blockchain-BOD.git
cd Blockchain-BOD
python -m pip install --editable ".[test]"
```

Run the local demonstration:

```bash
bod demo
```

Capture a deterministic snapshot:

```bash
bod snapshot . --out snapshot.json
```

Create a portable checkpoint:

```bash
bod capture . --project my-project --out checkpoint.json
```

Verify a checkpoint:

```bash
bod verify checkpoint.json --portable
python scripts/independent_verify.py checkpoint.json
```

Verify a chain:

```bash
bod verify chain.json --portable
python scripts/independent_verify.py chain.json --chain
```

Run the full public checks:

```bash
python scripts/validate_public_surface.py
python -m pytest -q
```

See [Getting Started](docs/GETTING_STARTED.md) for the complete walkthrough.

## Architecture and standards

BOD is intended to compose with established components:

| Concern | Existing ecosystem | BOD responsibility |
|---|---|---|
| Source history | Git | Consume tracked project state |
| Build provenance | SLSA, in-toto | Bind references and digests |
| Signing and transparency | Sigstore, Rekor | Reference external evidence |
| Software inventory | CycloneDX, SPDX | Bind inventory references |
| State commitments | Hashes and Merkle structures | Define deterministic project-state roots |
| Longitudinal continuity | Project-specific workflows | Link successive state commitments |
| Independent verification | Existing verifier implementations | Verify portable BOD records |

The proposed differentiator is the continuity relationship across state commitments, evidence references and portable verification—not hashing, signing, provenance or blockchain inclusion in isolation.

## Development priorities

I am keeping the public engineering scope focused on four measurable priorities:

1. Make the implementation, specifications and CLI behavior agree exactly.
2. Strengthen reproducibility, supported-version testing and supply-chain hygiene.
3. Publish adversarial test cases and clear verification boundaries.
4. Validate whether independent engineering teams gain measurable value over their existing Git and provenance workflows.

Progress is evidence-gated. The [public roadmap](docs/ROADMAP.md) records the validation gates; it does not promise delivery dates or production readiness.

## Repository map

```text
src/          Python reference implementation and CLI
scripts/      independent verifier and public validation tools
tests/        executable regression and adversarial checks
protocol/     protocol and chain-facing specifications
docs/         product scope, status, roadmap and threat model
experiments/  reproducible engineering experiments
research/     public design records and research notes
economics/    experimental economic model
```

## Contributing and security

Reproducible counterexamples, missing invariants, implementation issues and comparison results are welcome. See [Contributing](CONTRIBUTING.md) and [Security](SECURITY.md).

## License

MIT. See [LICENSE](LICENSE).
