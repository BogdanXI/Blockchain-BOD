# Break the State Machine

## Purpose

This is a small adversarial experiment for BOD Protocol v0.1.

The claim is intentionally narrow: when a state transition violates an explicit protocol invariant, the reference state machine rejects it rather than accepting a locally plausible result.

This is **not** a consensus-security proof and does not demonstrate a new consensus mechanism.

## Run

```bash
python3 scripts/break_state_machine.py
```

Expected output:

```text
PASS candidate-valid
REJECT invalid-signature
REJECT wrong-evidence
REJECT replay
REJECT state-conflict
REJECT policy-violation
REJECT settlement-without-valid-verification
```

The test deliberately attacks different boundaries:

| Case | Expected result | Invariant exercised |
|---|---|---|
| valid candidate | PASS | normal lifecycle |
| invalid signature | REJECT | signed-envelope authenticity |
| wrong evidence | REJECT | candidate/evidence binding |
| replay | REJECT | nonce replay protection |
| state conflict | REJECT | parent state-root consistency |
| policy violation | REJECT | verification-policy binding |
| settlement without valid verification | REJECT | verification before settlement |

## What this does not prove

A passing run does not prove that the implementation is secure against all attacks, that the economic model is final, or that the protocol provides decentralized consensus by itself. The experiment only makes a small set of falsifiable state-machine claims executable.

## Challenge

If you can construct an input that should be rejected under the documented invariant but is accepted by the reference implementation, open an issue with:

1. the exact input or minimal reproducer;
2. the expected rejection rule;
3. the observed acceptance path;
4. the smallest fix you believe is necessary.
