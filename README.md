# Blockchain-BOD

Blockchain-BOD is an experimental protocol for verifiable software state transitions with explicit separation between execution, evidence, verification, canonical selection and economic settlement.

## Protocol lifecycle

`Task -> Candidate -> Evidence -> Verification -> Settlement`

The protocol treats verification and canonicality as separate concerns:

- **Task** defines accountable work and escrowed reward.
- **Candidate** proposes a state transition.
- **Evidence** commits to reproducible execution artifacts.
- **Verification** attests to validity under a named policy.
- **Settlement** applies the canonical result and economic outcome.

The v0.1 protocol does **not** claim a new consensus mechanism. The first chain-facing implementation uses an adapter boundary so the protocol can be tested without making the execution chain part of the protocol definition.

## Try to break the state machine

We published a small adversarial experiment that runs one valid transition and several deliberately invalid transitions. The reference implementation should reject the invalid cases.

- Experiment: `experiments/BREAK_STATE_MACHINE.md`
- Runner: `scripts/break_state_machine.py`
- Test: `tests/test_break_state_machine.py`

The experiment is intentionally narrow: it is a falsifiable state-machine test, not a consensus-security proof.

## Current status

This is an experimental engineering project. Economic parameters are calibration baselines, not final policy.

Current workstream: **EC-0001 — economic calibration**.

Current public artifacts include:
- protocol specifications;
- deterministic state-machine and economic implementations;
- executable tests;
- an Arbitrum adapter prototype;
- economic invariants and calibration documentation.

## Repository

Public source: https://github.com/BogdanXI/Blockchain-BOD

The engineering workspace is maintained separately and is not part of this public repository.

## Principles

- reproducible experiments over unsupported claims;
- deterministic tests over informal assurances;
- verification separated from canonicality;
- protocol-significant data on-chain, large evidence off-chain;
- provisional economic parameters remain explicitly provisional.

## License

See `LICENSE`.
