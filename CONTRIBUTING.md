# Contributing

Contributions should be reproducible and focused on the public protocol surface.

Before opening a change:
1. explain the problem;
2. identify the mechanism or implementation change;
3. add or update deterministic tests;
4. keep protocol claims separate from implementation experiments;
5. do not include secrets, private operational data or internal workflow material.

Run:

    python -m pytest -q

Changes that alter protocol semantics should include a concise public design record or specification update.
