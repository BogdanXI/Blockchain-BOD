
## 2026-10-06 — Network-aware Arbitrum fee preparation

- The public MetaMask bridge now reads the Arbitrum chain-reported minimum gas price before transaction preparation.
- Priority fee remains zero, max-fee headroom remains 20%, and the submitted gas limit uses the exact Arbitrum estimate without a fixed 15% padding.
- Added public ADR-0109 documenting the network fee boundary and its non-final economic status.
