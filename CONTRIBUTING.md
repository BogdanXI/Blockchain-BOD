# Contributing

BOD is an experimental public engineering project. Contributions should be focused, reproducible, and limited to the public protocol and implementation.

## Before opening a change

1. Describe the problem and the observable failure or missing behavior.
2. Explain the chosen approach and relevant alternatives.
3. Add or update deterministic tests.
4. Keep protocol guarantees separate from implementation and testnet observations.
5. Update the relevant specification, threat model, status, or changelog.
6. Do not include credentials, private operational data, or material from private workspaces.

## Local verification

Requirements: Python 3.11 or newer.

```bash
python -m pip install -e .
python -m pip install pytest pyyaml
python scripts/validate_public_surface.py
python -m pytest -q
```

A passing local test suite is useful evidence, but reviewers should also inspect CI and the affected invariants.

## Protocol changes

Changes that alter serialized formats, commitment semantics, verification outcomes, trust policy, or transition authority should include a concise public design record. Prefer explicit versioning and negative tests for malformed or adversarial inputs.

## Pull requests

A useful pull request includes:
- a concise problem statement;
- implementation summary;
- tests run and their results;
- known limitations or follow-up work;
- links to related issues or design records.

Please do not present experimental results as production guarantees. See [Security](SECURITY.md) and [Project Status](docs/PROJECT_STATUS.md).
