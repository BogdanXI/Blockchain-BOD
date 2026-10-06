# BOD Continuity MVP — v0.1

## Purpose

The MVP provides one small reusable workflow for durable project continuity:

`capture -> content-addressed artifact -> recover -> deterministic State Root -> BOD utility quote`

A repository-native adapter also captures real Git software projects without requiring a preconstructed state JSON document.

## CLI

`python3 scripts/bod_continuity.py capture STATE.json STATE.artifact.json --evidence evidence.json`

`python3 scripts/bod_continuity.py capture-repo /path/to/repo REPO.artifact.json --project-id my-project --next-action resume --evidence evidence.json`

`python3 scripts/bod_continuity.py recover STATE.artifact.json`

`python3 scripts/bod_continuity.py quote STATE.artifact.json --operation-id op-1 --payer alice --base-fee 10 --bytes-fee-per-kib 2 --artifact-fee 5 --verification-fee 7`

The quote command requires explicit coefficients. The MVP does not hide or imply final BOD monetary policy.

## Recovery guarantee

The durable State Root excludes runtime metadata. A project captured in two different runtime environments therefore has the same durable root when durable state is identical, while the complete artifact hash may differ because runtime provenance is retained.

Recovery rejects non-canonical or malformed artifacts through the existing project-state parser.

## Repository capture boundary

`capture-repo` hashes Git-tracked working-tree files, including tracked edits that are not yet committed. Untracked files are deliberately excluded so caches, local credentials and incidental runtime files do not silently become durable project state. Known dependency lockfiles are committed into a deterministic dependency-lock hash. The Git HEAD commit is durable context. Absolute repository path and branch name are retained only as runtime provenance and therefore do not alter the State Root.

## Current boundary

This is a local infrastructure MVP. It is not a hosted service, decentralized network, production wallet, final tokenomics system or proof of market demand.