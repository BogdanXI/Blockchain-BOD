# Graph-Coupled Finality Reduction Test v0.2

## Result sought

The decisive question is not whether graph-coupled finality changes **which validators** sign.

It is whether the graph changes **which certificates signed by the same validators are valid**.

The experiment constructs two certificates with exactly the same 3 signers:
- one satisfies all graph dependencies;
- one violates a dependency.

Any scalar PoS rule based only on signer weights must assign the same validity to both.

Run:

```bash
python3 tests/test_graph_coupled_finality.py
```

This is a finite semantic counterexample, not a security proof.

## Interpretation

If the test passes, graph dependency validity cannot be reduced to scalar signer weight.

That still does **not** prove a new consensus protocol: the next reduction test is against an ordinary BFT protocol augmented with a dependency/communication rule.

