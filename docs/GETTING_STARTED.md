# Getting Started

This guide runs the local BOD v0.1 prototype. It does not deploy a blockchain, require a wallet or upload project contents to a service.

## Requirements

- Python 3.11 or newer
- Git
- A clean clone of this repository

## 1. Install

```bash
git clone https://github.com/BogdanXI/Blockchain-BOD.git
cd Blockchain-BOD
python -m pip install --editable ".[test]"
```

The `test` extra installs the dependencies required by the repository's validation suite.

## 2. Run the demonstration

```bash
bod demo
```

The command creates a portable checkpoint from the current Git-tracked working tree and verifies the checkpoint with the reference implementation. A successful result covers only the behavior exercised by this local demonstration.

## 3. Capture a snapshot

```bash
bod snapshot . --out snapshot.json
```

The snapshot records ordered Git-tracked file paths, SHA-256 digests and byte sizes. It does not include file contents. Untracked files are excluded.

Treat the generated file as an artifact. Do not commit sensitive project metadata or private repository contents.

## 4. Create a portable checkpoint

```bash
bod capture . --project example-project --out checkpoint.json
```

A checkpoint binds the snapshot state root to an Evidence Envelope. A predecessor can be supplied to continue an existing history:

```bash
bod capture . --project example-project --predecessor previous-checkpoint.json --out next-checkpoint.json
```

The predecessor file must contain a valid portable checkpoint or checkpoint collection in the format accepted by the CLI.

## 5. Verify independently

Verify the portable checkpoint with the reference CLI:

```bash
bod verify checkpoint.json --portable
```

Then use the independent verifier:

```bash
python scripts/independent_verify.py checkpoint.json
```

For a chain:

```bash
bod verify chain.json --portable
python scripts/independent_verify.py chain.json --chain
```

The independent verifier does not import the BOD reference implementation. It is a second implementation check, not an external security audit.

## 6. Verify checkpoint metadata

```bash
bod recover checkpoint.json
```

The command validates the checkpoint and reports the recorded state root, envelope and file metadata. **It does not restore source files.** The current portable checkpoint format contains metadata and digests, not the original payloads.

## 7. Run repository checks

```bash
python scripts/validate_public_surface.py
python -m pytest -q
bod demo
```

The CI workflow runs these checks across the supported Python versions. Inspect the latest [CI runs](https://github.com/BogdanXI/Blockchain-BOD/actions) for the result associated with the commit you are reviewing.

## What a successful result means

A successful integrity result means the declared bytes, commitments and applicable lineage rules satisfy the verifier. It does not prove that source statements are true, that evidence remains available, that an upstream producer was honest, that a build was secure, or that an external chain anchor is canonical.

See [Project Status](PROJECT_STATUS.md), [Roadmap](ROADMAP.md) and the [Threat Model](THREAT_MODEL_v0.1.md) for the current implementation boundary.
