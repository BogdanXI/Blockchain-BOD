# BOD — Ethereum-anchored evidence continuity

![BOD Evidence Fabric](docs/assets/bod-mark.svg)

**Portable, independently verifiable continuity for software state — with Ethereum as an optional public witness.**

[![CI](https://github.com/BogdanXI/Blockchain-BOD/actions/workflows/ci.yml/badge.svg)](https://github.com/BogdanXI/Blockchain-BOD/actions/workflows/ci.yml) [![License](https://img.shields.io/badge/license-MIT-111827.svg)](LICENSE) [![Python](https://img.shields.io/badge/python-3.11%2B-111827.svg)](pyproject.toml) [![Status: Experimental](https://img.shields.io/badge/status-experimental-orange.svg)](docs/PROJECT_STATUS.md)

[Quickstart](docs/GETTING_STARTED.md) · [Ethereum integration](docs/ETHEREUM_INTEGRATION.md) · [Market hypothesis](docs/MARKET_FIT.md) · [Threat model](docs/THREAT_MODEL_v0.1.md) · [Roadmap](docs/ROADMAP.md)

---

## The problem

Software delivery produces source commits, build provenance, SBOMs, signatures, vulnerability results, deployment records and release attestations. Those records are useful, but they are distributed across repositories, CI systems, registries and transparency services.

A consumer still needs to answer a longitudinal question:

**Can I reconstruct and independently verify the exact project state, its predecessor relationship and the evidence set associated with a release — even after the original CI runner, developer workstation or service has disappeared?**

BOD is an open-source continuity and verification layer for that problem. It does not replace Git, SLSA, in-toto, Sigstore, SPDX, CycloneDX or Ethereum Attestation Service (EAS). It binds their evidence digests to a portable, deterministic history.

## How it works

```text
SOURCE / BUILD / RELEASE
        |
        v
DETERMINISTIC PROJECT SNAPSHOT
        |
        v
VERSIONED EVIDENCE ENVELOPE
  state root + predecessor
  provenance / SBOM / attestation digests
        |
        v
INDEPENDENT LOCAL VERIFICATION
  integrity + lineage + replay/fork checks
        |
        v
OPTIONAL ETHEREUM CHECKPOINT
  compact commitments only
        |
        v
FRESH-RUNTIME RECOVERY
```

The complete evidence payload remains off-chain. Ethereum receives compact commitments only. The chain is an external timestamped witness; it does not decide whether source code is safe, whether a build is honest, or whether a BOD transition is semantically correct.

## Why Ethereum

Ethereum provides a widely accessible public execution environment, mature wallet and developer tooling, and an ecosystem of attestations and security infrastructure. BOD's Ethereum integration is deliberately narrow:

- publish a content commitment for a project checkpoint;
- link it to a predecessor checkpoint;
- make the record independently readable from Ethereum;
- preserve forks as observable evidence rather than silently selecting a canonical branch;
- keep verification and recovery usable without a wallet or RPC endpoint.

The first Ethereum contract is permissionless and append-only. It has no owner, upgrade key, token, fee logic or privileged settlement authority. It does **not** claim to implement consensus or canonicality.

## Quickstart

Requirements: Python 3.11+.

```bash
git clone https://github.com/BogdanXI/Blockchain-BOD.git
cd Blockchain-BOD
python -m pip install -e .
bod demo
```

Capture and verify a local repository snapshot:

```bash
bod snapshot . --out snapshot.json
python scripts/independent_verify.py snapshot.json
```

Run the Python checks:

```bash
python -m pip install pytest pyyaml
python scripts/validate_public_surface.py
python -m pytest -q
```

Install [Foundry](https://getfoundry.sh/) and run the Ethereum contract tests:

```bash
forge test -vvv
```

No wallet, token, RPC URL or blockchain transaction is required for local verification.

## Ethereum contract

The registry is in `protocol/ethereum/BODEthereumCheckpointRegistry.sol`. It records a project identifier, Git commit digest, BOD state root, manifest digest, evidence-set root, predecessor checkpoint, sequence, publisher and block timestamp.

It intentionally does not store source code, build logs, SBOM payloads, secrets, prompts or personal data. It does not expose a mutable “latest canonical state” pointer. Multiple branches can be recorded and independently examined.

See [Ethereum integration and deployment boundaries](docs/ETHEREUM_INTEGRATION.md).

## Product boundary

BOD's proposed differentiator is **portable continuity across successive software states**, not another hash registry or provenance format.

| Existing system | BOD relationship |
|---|---|
| Git | Captures source history; BOD commits to reproducible project snapshots |
| SLSA / in-toto | Supplies provenance semantics; BOD references evidence digests |
| Sigstore / Rekor | Supplies signatures and transparency; BOD can bind those records |
| SPDX / CycloneDX | Supplies SBOM semantics; BOD references inventory digests |
| Ethereum Attestation Service | Potential attestation transport/integration; BOD does not replace EAS |
| Ethereum | Optional public checkpoint witness; not BOD consensus |

The product hypothesis remains unproven until independent teams demonstrate a measurable improvement in release verification, audit reconstruction or recovery compared with their existing toolchain. See [Market hypothesis and validation plan](docs/MARKET_FIT.md).

## Security and maturity

**Experimental engineering prototype. Not production-secure.**

A matching digest proves byte identity relative to the digest. It does not prove truth, safety, availability, signer honesty, build integrity or semantic correctness. An Ethereum transaction proves that a commitment was included in a particular chain history; it does not validate the commitment's meaning.

No production BOD token, native BOD network, decentralized consensus, hosted service or audited mainnet deployment is claimed. The former Arbitrum adapter remains in the repository as a legacy EVM experiment; the active chain-facing development target is Ethereum.

See [Threat model](docs/THREAT_MODEL_v0.1.md), [Security policy](SECURITY.md), and [Project status](docs/PROJECT_STATUS.md).

## Repository map

```text
protocol/ethereum/  Ethereum checkpoint contract
protocol/arbitrum/  legacy Arbitrum testnet experiment
src/                Python reference implementation and CLI
scripts/            independent verifier and experiments
tests/              Python regression tests
test/               Foundry contract tests
docs/               product, security and integration documentation
research/           public architecture decisions
```

## License

MIT. See [LICENSE](LICENSE).
