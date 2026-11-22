# BOD quickstart

This guide verifies the portable continuity core locally. It does not deploy a blockchain or require a wallet, RPC endpoint, token or paid service.

## 1. Install

Requirements: Python 3.11 or newer.

```bash
git clone https://github.com/BogdanXI/Blockchain-BOD.git
cd Blockchain-BOD
python -m pip install -e .
python -m pip install pytest pyyaml
```

## 2. Run the local demonstration

```bash
bod demo
```

The command creates a deterministic checkpoint and prints its identifiers. It only demonstrates the behavior exercised by this local example.

## 3. Capture a portable checkpoint

```bash
bod capture . --project my-project --out checkpoint.json
```

Do not include private repositories, secrets, credentials, private keys or sensitive file contents in a public checkpoint. The repository capture boundary is based on Git-tracked files.

## 4. Verify independently

```bash
bod verify checkpoint.json --portable
python scripts/independent_verify.py checkpoint.json
bod recover checkpoint.json
```

The independent verifier is a separate implementation and does not import the BOD package. A successful result establishes only the encoded integrity and lineage predicates; it does not prove semantic truth or evidence availability.

## 5. Run Python checks

```bash
python scripts/validate_public_surface.py
python -m pytest -q
```

## 6. Run Ethereum contract tests

Install [Foundry](https://getfoundry.sh/) and run:

```bash
forge test -vvv
```

This compiles and tests the Ethereum checkpoint registry locally. It does not submit a transaction.

## 7. Ethereum Sepolia deployment

Deployment is intentionally not automated. Read [Ethereum integration](ETHEREUM_INTEGRATION.md) first. The contract has not been independently audited or deployed; use a disposable Sepolia wallet only after review.

See [Project Status](PROJECT_STATUS.md), [Roadmap](ROADMAP.md), and [Threat Model](THREAT_MODEL_v0.1.md).
