# Blockchain-BOD

[![CI](https://github.com/BogdanXI/Blockchain-BOD/actions/workflows/ci.yml/badge.svg)](https://github.com/BogdanXI/Blockchain-BOD/actions/workflows/ci.yml)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

Blockchain-BOD is an experimental protocol for verifiable software state transitions with explicit separation between execution, evidence, verification, canonical selection, and economic settlement.

## Protocol lifecycle

`Task -> Candidate -> Evidence -> Verification -> Settlement`

The protocol separates validity from canonicality:

- **Task** defines accountable work and the associated reward.
- **Candidate** proposes a state transition.
- **Evidence** commits to reproducible execution artifacts.
- **Verification** evaluates a candidate under a named policy.
- **Settlement** records the canonical outcome and economic result.

BOD Protocol v0.1 is an application protocol. It does **not** claim a new consensus mechanism. The chain-facing implementation uses an adapter boundary so protocol semantics can be tested independently of a specific execution chain.

## Verification-first development

The repository is built around deterministic specifications, executable tests, and falsifiable experiments.

The public adversarial state-machine experiment executes one valid transition and several deliberately invalid transitions. The reference implementation is expected to reject the invalid cases.

- Experiment: [`experiments/BREAK_STATE_MACHINE.md`](experiments/BREAK_STATE_MACHINE.md)
- Runner: [`scripts/break_state_machine.py`](scripts/break_state_machine.py)
- Test: [`tests/test_break_state_machine.py`](tests/test_break_state_machine.py)

The experiment is intentionally narrow. It is a falsifiable state-machine test, not a consensus-security proof.

## Current status

**Experimental — v0.1 protocol baseline**

Current workstream: **EC-0001 — economic calibration**.

Public artifacts include:

- protocol specifications;
- deterministic state-machine and economic implementations;
- executable tests;
- an Arbitrum adapter prototype;
- economic invariants and calibration documentation;
- reproducible validation and readiness checks.

Economic parameters are calibration baselines, not final policy.

## Quick start

Requirements:

- Python 3.12+
- `pytest`
- `PyYAML`

Install the test dependencies:

~~~bash
python -m pip install -U pytest pyyaml
~~~

Run the public-surface validation:

~~~bash
python scripts/validate_public_surface.py
~~~

Run the test suite:

~~~bash
python -m pytest -q
~~~

## Repository structure

~~~text
protocol/       Protocol specifications and chain adapters
economics/      Economic invariants and calibration
experiments/    Reproducible falsification experiments
src/            Reference implementation
tests/          Executable verification
scripts/        Validation and experiment runners
research/       Public design records
~~~

## Design principles

- reproducible experiments over unsupported claims;
- deterministic tests over informal assurances;
- verification separated from canonicality;
- protocol-significant data on-chain, large evidence off-chain;
- provisional economic parameters remain explicitly provisional.

## Security

The v0.1 implementation is experimental and is not presented as production-secure. See [`SECURITY.md`](SECURITY.md) for the security policy.

## License

Released under the MIT License. See [`LICENSE`](LICENSE).
