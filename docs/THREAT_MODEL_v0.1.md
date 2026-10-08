# BOD Evidence Fabric — Threat Model v0.1

## Security claim boundary

BOD proves only predicates that its verifier actually checks.

A successful BOD verification means:

1. the envelope bytes are canonical and its commitment matches;
2. the declared state root and evidence digests are bound to that envelope;
3. the predecessor relationship is valid for the supplied history;
4. the selected verification policy accepts the referenced evidence metadata.

It does **not** mean:

- the underlying evidence is truthful;
- the build was secure merely because it has provenance;
- the referenced URI is still available;
- the issuer is trustworthy unless the verifier policy says so;
- the source code is functionally correct;
- a blockchain transaction makes an invalid envelope valid;
- a local anchor is independent evidence.

## Adversaries

### A1 — evidence fabricator

Can create false reports, logs or attestations.

**BOD response:** detects later mutation of the referenced bytes when those bytes are available, but cannot determine whether the original producer lied. Trust policy and upstream attestation verification are required.

### A2 — evidence mutator

Changes an evidence file after capture.

**BOD response:** digest mismatch causes verification failure.

### A3 — history rewriter

Removes a predecessor, injects a fork, replays a state root or crosses project boundaries.

**BOD response:** chain verification fails closed on gaps, forks, duplicate roots, disconnected components and project mismatch.

### A4 — compromised CI/runtime

Controls the machine that produced the evidence.

**BOD response:** BOD preserves the declared evidence and its lineage but does not turn a compromised builder into a trustworthy builder. Consumers must verify builder identity and provenance policy independently.

### A5 — anchor compromise

Controls one external anchor provider or RPC endpoint.

**BOD response:** an anchor is an external witness, not validity. Verification must independently check the anchor and may use multiple providers. A failed or unavailable anchor must not silently become VALID.

### A6 — BOD verifier bug

A verifier implementation accepts an invalid envelope.

**BOD response:** the project publishes a second independent verifier and cross-implementation test vectors. The canonical format is deliberately small so independent implementations are practical.

### A7 — BOD service disappears

The original BOD service is unavailable.

**BOD response:** exported envelopes, evidence and anchor receipts remain self-contained. Verification must not require a BOD SaaS endpoint.

## Trust layers

CONTENT INTEGRITY -> LINEAGE -> EVIDENCE TRUST -> EVIDENCE SEMANTICS -> EXTERNAL WITNESSES

Each layer is independent. Passing a lower layer never upgrades a higher layer automatically.

## Required verifier result

The verifier MUST distinguish:

- `VALID_INTEGRITY`;
- `INVALID`;
- `semantic_truth = NOT_ASSERTED`;
- `availability = UNKNOWN` unless evidence retrieval was actually performed;
- policy acceptance separately from cryptographic validity.

This prevents the product from converting "hash matched" into "the claim was true."

## Residual risks

BOD does not eliminate malicious or compromised evidence producers, malicious builders, unavailable evidence, weak trust policies, semantic errors in tests or SBOMs, compromised upstream signing infrastructure, or chain/anchor failure.

The correct mitigation is layered verification, not a stronger marketing claim.
