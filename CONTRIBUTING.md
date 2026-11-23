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
python3 -m pip install --editable ".[test,lint]"
python3 scripts/validate_public_surface.py
ruff check --select E4,E7,E9,F src scripts tests
python3 -m pytest -q
forge test
```

A passing local test suite is useful evidence, but reviewers should also inspect CI and the affected invariants.

## Ethereum changes

- Prefer EAS for attestations rather than introducing another generic attestation format.
- Keep checkpoint evidence payloads off-chain; publish only commitments.
- Document chain ID, contract address, schema UID, issuer policy and finality assumptions.
- Never commit wallets, private keys, seed phrases or RPC credentials.
- Do not use mainnet for tests.

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
