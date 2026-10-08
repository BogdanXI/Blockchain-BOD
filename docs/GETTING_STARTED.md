# BOD in 5 minutes

## 1. Install

```bash
python -m pip install -e .
```

No blockchain account and no paid service are required for the local product demonstration.

## 2. Run the end-to-end demo

```bash
bod demo
```

The command creates three linked state transitions, verifies the lineage and prints a machine-readable `VALID` result.

## 3. Create a deterministic project state root

```bash
bod snapshot . --out snapshot.json
```

The resulting `state_root` is derived from the ordered paths, file digests and sizes in the snapshot.

## 4. Verify evidence

```bash
bod verify envelope.json
bod verify chain.json --chain
```

The verifier returns either `VALID` or `INVALID` and a reason suitable for automation.

## 5. Run the complete test suite

```bash
python -m pytest -q
```
