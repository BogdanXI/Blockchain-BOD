# Legacy components and migration boundary

## Historical BOD task, token and economics work

The earlier Task-to-Settlement protocol and BOD-denominated economic model are not part of the active Ethereum release-evidence product, grant scope or deployment plan.

The historical material is retained for traceability:

- Protocol specification: [BOD Protocol v0.1](../protocol/BOD_PROTOCOL_v0.1.md).
- Historical architecture: [Architecture v0.1](../protocol/ARCHITECTURE_v0.1.md).
- Token policy: [BOD token policy v0.1](../protocol/genesis/BOD_TOKEN_POLICY_v0.1.yml).
- Economic model and known supply mismatch: [economics archive note](../economics/README.md).
- Legacy implementation modules include bod_protocol, bod_economy, bod_economic_operations, bod_simulation, bod_continuity, bod_project_state and bod_repository_adapter under src/.

These modules and their regression tests are retained in the source tree for historical review. They are not listed in the setuptools distribution allowlist and are not included in the built Python wheel. The supported package surface is defined explicitly in pyproject.toml.

The old economic simulator and token policy disagree on maximum and genesis supply. That inconsistency is a historical research artifact, not an approved parameter set. Do not use either set of values as production tokenomics, a grant deliverable or an investor claim.

## Active Ethereum scope

Use Ethereum-native tooling only where it provides a concrete verification benefit: EAS for linked attestations and, if justified, a minimal Ethereum L1 checkpoint witness. Do not add an L2 integration merely to increase the number of supported networks. No bridge, rollup, custom chain, BOD token, staking or settlement layer is required for the current evidence-continuity product.

The active Python distribution is intentionally limited to the CLI, evidence envelope, portable checkpoint, evidence-format inspection, anchor interface and simple verifier modules declared in pyproject.toml.

## Migration principle

Preserve historical code and decisions for traceability, but keep them outside the active package and current protocol surface. New product claims must describe the portable evidence-continuity implementation and the actual validation status of its optional Ethereum registry and EAS integrations.
