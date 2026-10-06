# Repository Continuity Proof — 2026-10-06

Status: reproducible engineering evidence.

## Objective

Verify that the repository-native continuity adapter captures the same durable project state from two independent checkout locations of the same software project, while keeping runtime provenance outside the durable State Root.

## Procedure

1. Capture a clean repository checkout with the repository adapter.
2. Clone the same checkout into an independent temporary location.
3. Capture the clone using the same project semantic inputs.
4. Compare durable State Roots.
5. Parse and recover the independent artifact.
6. Bind the recovered manifest to the BOD utility quote path with explicit synthetic coefficients.

The capture boundary hashes Git-tracked working-tree content. Untracked files are excluded. Absolute path and branch are runtime provenance.

## Observed result

- tracked artifacts: 30
- original State Root: `74eefb8615541b6f087ddf954567803cb2eaea48a237b156dec7f701e78e3d77`
- independent-clone State Root: `74eefb8615541b6f087ddf954567803cb2eaea48a237b156dec7f701e78e3d77`
- recovered State Root: `74eefb8615541b6f087ddf954567803cb2eaea48a237b156dec7f701e78e3d77`
- State Root equality: PASS
- recovery equality: PASS
- original artifact hash: `16060373a2381fbfe6ed86b062080028c8e653ed33b377d33d916ebd46457f53`
- independent artifact hash: `1247f3e5f56eacd4fd7db0304d351de905175d714ddf8cd8cf7f9919cb546a6e`
- artifact hashes differ due to runtime provenance: PASS
- dependency-lock hash: `4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945`
- synthetic quote: 302 BOD

The quote uses explicit experimental coefficients. It is workload/accounting evidence only and is not a token price, willingness-to-pay observation, demand estimate, or final monetary policy.

## Engineering consequence

The continuity path now has executable evidence for:

`real Git project -> deterministic tracked-file commitments -> State Root -> independent-location recovery -> BOD-denominated utility quote`

This does not establish decentralized canonicality, native BOD consensus, production availability, or market demand.
