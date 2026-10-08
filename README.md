# BOD

## Evidence Fabric for verifiable digital state

**Prove what existed. Prove how it changed. Recover it on another runtime. Verify it independently.**

[![CI](https://github.com/BogdanXI/Blockchain-BOD/actions/workflows/ci.yml/badge.svg)](https://github.com/BogdanXI/Blockchain-BOD/actions/workflows/ci.yml) [![License](https://img.shields.io/badge/license-MIT-111827.svg)](LICENSE) [![Python](https://img.shields.io/badge/python-3.11%2B-111827.svg)](pyproject.toml)

---

## The problem

Software projects lose trustworthy history when the machine, CI runner, agent, model runtime or local workspace disappears.

A Git commit proves that bytes existed in a repository. A blockchain transaction can prove that a commitment was anchored. Neither alone gives a complete, machine-verifiable answer to what project state was captured, what evidence supported it, which state came before it, whether a result was replayed/forked, or whether a fresh runtime can reconstruct the same history.

**BOD connects those layers.**

## The product

```text
SOURCE / GIT / BUILD
        |
        v
DETERMINISTIC STATE SNAPSHOT
        |
        v
EVIDENCE ENVELOPE
  state root + predecessor
  provenance/SBOM/attestation digests
        |
        v
BOD VERIFIER
  integrity + lineage + replay/fork detection
        |
        v
OPTIONAL EXTERNAL ANCHOR
  Arbitrum / another EVM / future BOD network
        |
        v
FRESH RUNTIME RECOVERY
        |
        v
VALID / INVALID
```

The blockchain is an **external anchor**, not a database for large evidence payloads.

## Why this is useful

- **Deterministic:** machine-specific runtime metadata is excluded from durable commitments.
- **Lineage-aware:** state transitions form a verifiable chain and missing predecessors, forks and replayed roots are rejected.
- **Evidence-native:** BOD references SLSA/in-toto, CycloneDX, Sigstore/Rekor and other evidence by digest instead of duplicating their payload formats.
- **Runtime-independent:** verification can restart in a fresh process or on another machine.
- **Anchor-agnostic:** external blockchain anchoring is a provider, not the definition of BOD.

## Try it locally

No wallet. No blockchain account. No paid service.

```bash
git clone https://github.com/BogdanXI/Blockchain-BOD.git
cd Blockchain-BOD
python -m pip install -e .
bod demo
```

The demo creates three linked state transitions and verifies the complete chain.

Create a deterministic repository state root:

```bash
bod snapshot . --out snapshot.json
```

Verify an envelope or chain:

```bash
bod verify envelope.json
bod verify chain.json --chain
```

Run the tests:

```bash
python -m pytest -q
```

Full walkthrough: [docs/GETTING_STARTED.md](docs/GETTING_STARTED.md)

## Architecture

| Layer | Responsibility | Current implementation |
|---|---|---|
| State | deterministic project snapshot | `bod snapshot` |
| Evidence | versioned durable envelope | Evidence Envelope v0.1 |
| Verification | integrity + lineage + adversarial checks | Python reference verifier |
| Provenance | references to external evidence | digest-only evidence records |
| Anchor | independent external checkpoint | experimental Arbitrum path |
| Recovery | fresh-runtime reconstruction | executable recovery experiments |
| Economics | service-backed token policy | **separate, not final** |

**BOD protocol validity is not the same thing as blockchain consensus, and a successful testnet transaction is not a production-security claim.**

## Technology strategy

BOD composes mature technologies rather than rebuilding them:

- Git and content hashing for source identity;
- deterministic canonical serialization for durable commitments;
- SLSA/in-toto for provenance semantics;
- CycloneDX for software inventory;
- Sigstore/Rekor for transparency evidence;
- EVM networks for independent external anchoring;
- public or self-hosted CI for reproducible verification.

The differentiating layer is the **continuity relationship** between state, evidence, lineage, external anchoring and fresh-runtime recovery.

## Cost strategy

The development stack is intentionally close to zero incremental infrastructure cost:

1. local deterministic verification is free;
2. public CI executes the open-source test surface;
3. a self-hosted runner can execute heavier experiments on existing hardware;
4. external testnet anchors use test assets;
5. production anchoring is optional and costed separately.

## Security model

BOD v0.1 is experimental. It does not claim production consensus security, censorship resistance, availability of external evidence, correctness of upstream evidence producers, economic finality, or that EVM inclusion makes a BOD transition valid.

See [SECURITY.md](SECURITY.md).

## Project status

**Experimental / public engineering release**

Implemented:

- deterministic state commitments;
- Evidence Envelope v0.1;
- canonical evidence ordering;
- self-verifying envelope IDs;
- predecessor-linked state history;
- adversarial lineage verification;
- local CLI;
- reproducible test suite;
- experimental external-anchor integration.

Still gated:

- production economic policy;
- production token launch;
- native BOD network;
- production security audit.

## Repository map

```text
protocol/     protocol and chain-facing specifications
src/          reference implementation and CLI
tests/        executable verification
docs/         product and architecture documentation
economics/    experimental economic model
experiments/ reproducible falsification work
research/     public research and decision records
scripts/      validation and experiment runners
```

## Design principle

> **Don't market the blockchain. Market the experiment.**

Every important claim should be backed by code, a reproducible experiment, an explicit invariant or independently verifiable evidence.

## License

MIT — see [LICENSE](LICENSE).