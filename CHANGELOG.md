## 2026-10-08 — Evidence Fabric public product baseline

- Reframed the public repository around BOD Evidence Fabric: deterministic state -> evidence envelope -> verification -> optional external anchor -> fresh-runtime recovery.
- Published deterministic Evidence Envelope v0.1 and adversarial lineage verification.
- Added an installable `bod` CLI with repository snapshots, envelope creation, verification and local demonstration.
- Added an anchor-provider abstraction with a free local provider for development.
- Added product quickstart, architecture documentation and public product identity assets.
- Hardened the public-surface validator so legitimate identifiers containing blocked substrings are not rejected.
- Verified the public tree locally: public-surface validation passed, product demo returned `VALID`, and **97 tests passed**.

## 2026-10-06 — Network-aware Arbitrum fee preparation

- The public MetaMask bridge now reads the Arbitrum chain-reported minimum gas price before transaction preparation.
- Priority fee remains zero, max-fee headroom remains 20%, and the submitted gas limit uses the exact Arbitrum estimate without a fixed 15% padding.
- Added public ADR-0109 documenting the network fee boundary and its non-final economic status.
