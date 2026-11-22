# Project status

**Release status:** experimental public engineering prototype  
**Protocol version:** v0.1  
**License:** MIT  
**Primary chain integration target:** Ethereum  
**Ethereum deployment status:** not deployed / not audited

## Implemented and reviewable

- deterministic repository snapshots;
- versioned evidence envelopes and predecessor-linked history;
- independent verification and portable checkpoint recovery;
- Python CLI and regression suite;
- a permissionless, append-only Ethereum checkpoint registry;
- Foundry tests for checkpoint creation, lineage validation, duplicate rejection and fork visibility;
- CI coverage for Python and Solidity;
- EAS SDK schema-registration and linked-checkpoint scripts with parent-attestation checks.

## Ethereum integration boundary

The Ethereum contract records compact commitments and predecessor references. It does not store evidence payloads, determine semantic truth, select a canonical branch, execute software, verify SLSA attestations, or implement BOD consensus.

The Ethereum contract is source code with local tests. It has not been deployed to Sepolia or Ethereum mainnet. The EAS schema has not yet been registered and no live attestation is claimed. A passing local test suite is not a security audit.

## Legacy Arbitrum work

The previous Arbitrum Sepolia adapter, browser bridge and workflows remain as historical experimental work. They are not the primary product narrative or deployment target. No Arbitrum One or Ethereum mainnet deployment is claimed.

## Legacy research boundary

The earlier BOD token/economic experiments are not part of the active Ethereum product. The legacy Python simulator and token-policy YAML contain unreconciled supply parameters; they are explicitly archived and must not be presented as final tokenomics. The Arbitrum adapter and browser bridge remain historical experimental components. See [Legacy components](LEGACY_COMPONENTS.md) and [economics archive note](../economics/README.md).

## Explicit non-claims

- No production-ready BOD blockchain or native consensus mechanism.
- No production token launch or final tokenomics.
- No audited or production-secure smart contract.
- No proof that referenced evidence is truthful or available.
- No claim that an on-chain checkpoint makes a software release safe or canonical.
- No demonstrated market demand or paying customer.

## Current validation gates

1. Run Python tests and independent verification from a clean checkout.
2. Run Foundry tests and review Solidity compiler output.
3. Obtain independent smart-contract and protocol review.
4. Deploy only to Ethereum Sepolia after review and verify contract bytecode and transactions independently.
5. Integrate a real CI provenance/SBOM/attestation workflow.
6. Compare BOD with Git + SLSA/in-toto + Sigstore/EAS using reproducible release-recovery experiments.
7. Interview independent maintainers and security/release teams; publish positive and negative findings.

See [Ethereum integration](ETHEREUM_INTEGRATION.md), [Roadmap](ROADMAP.md), and [Threat model](THREAT_MODEL_v0.1.md).
