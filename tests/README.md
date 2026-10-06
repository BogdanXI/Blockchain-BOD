# Tests

The test suite is the executable verification layer for the public protocol implementation.

## Run the suite

~~~bash
python -m pytest -q
~~~

## Scope

The suite covers protocol state transitions, economic invariants, adapter behavior, continuity capture/recovery, readiness checks, and the published adversarial state-machine experiment.

Individual experiments and checks can be run directly from their corresponding scripts in `scripts/` and `experiments/`.
