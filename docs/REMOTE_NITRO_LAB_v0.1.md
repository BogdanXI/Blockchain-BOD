# Remote Nitro laboratory

This branch provides a reproducible remote execution path for the BOD development laboratory.

## Purpose

The local Arbitrum Nitro testnode is treated as disposable compute. The reproducible source of truth is GitHub:

1. BOD branch and tests;
2. pinned Nitro testnode commit;
3. bootstrap script;
4. GitHub Actions execution;
5. test and RPC evidence.

The runtime can therefore be recreated without the developer workstation.

## Important boundary

Hugging Face Jobs were evaluated as a possible replacement runtime. Standard Jobs run inside a restricted sandbox without the kernel capabilities required for nested Docker/container orchestration. The official Nitro testnode requires Docker and Docker Compose, so the full testnode is not claimed to run inside a standard HF Job.

For this reason this branch uses a GitHub-hosted Linux runner for the full Nitro Docker topology. Hugging Face remains suitable for independent BOD calculations and other non-Docker workloads.

## Pinned dependency

The bootstrap currently pins the OffchainLabs/nitro-testnode release branch at:

`72ac4bb1f07fadc108448ad5fae01ea2e044fe69`

The pin is intentionally explicit so a future rebuild does not silently change the laboratory topology.

## Recovery

From a clean runner, the bootstrap:

- clones the pinned testnode;
- verifies Docker;
- initializes the Nitro test environment;
- disables the million-transaction background traffic;
- disables token-bridge setup;
- probes L2 JSON-RPC;
- runs the BOD deterministic regression suite.

This is a development laboratory, not a production network and not evidence of Nitro validation PASS.
