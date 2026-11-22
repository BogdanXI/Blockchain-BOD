# Zero-Cost Testing Plan

## Policy

The project test budget is **USD 0**. Development, regression testing, contract
testing, and testnet integration must not require paid infrastructure, paid
RPC plans, subscriptions, credit cards, or real-value cryptocurrency.

If a test cannot be completed with the free options described here, it must be
run locally or deferred. Do not silently switch to a paid provider.

## Test layers

### 1. Local deterministic tests

These tests require no blockchain account, RPC provider, faucet, or transaction
fee:

- Python regression suite and independent checkpoint verification;
- static analysis and public-surface validation;
- Foundry unit, fuzz, and invariant tests against the local EVM;
- EAS SDK import, schema encoding, and script validation;
- dependency installation from committed lockfiles.

The local EVM is the default for repeatable contract tests. A local test does
not claim that a contract has been deployed to Ethereum.

### 2. Ethereum Sepolia integration tests

Sepolia is the public Ethereum application-development testnet. Use it only
for integration checks that cannot be established by local tests.

- Use test ETH from public faucets only. Sepolia ETH has no intended monetary
  value and must never be purchased.
- Use a public/free RPC endpoint or a self-hosted node. Do not use a metered
  paid endpoint, paid API key, paid explorer, or service requiring a payment
  card.
- Prefer endpoints that do not require an account. If a provider requires an
  account, verify that the selected plan is genuinely free and has no paid
  commitment.
- Keep requests low-volume and cache read-only results where practical.
- If free faucet or RPC access is temporarily unavailable, defer the live
  test; do not pay to unblock it.

Ethereum's network guide identifies Sepolia as the recommended default for
application development and lists public testnet faucets:
https://ethereum.org/developers/docs/networks/

### 3. EAS end-to-end rehearsal

The EAS rehearsal is limited to Sepolia and must use test ETH from a faucet.
It may register the BOD schema and create test attestations only after the
operator explicitly authorizes the test transaction.

- Use a dedicated disposable test wallet with no mainnet funds.
- Keep the signing key in a local ignored environment file or protected local
  secret store. Never commit it, print it in logs, or send it in chat.
- Validate chain ID, EAS deployment addresses, schema UID, parent attestation,
  project ID, sequence, and revocation/expiration state.
- Record transaction hashes and verification evidence in the test report.
- Never use a mainnet signer or mainnet RPC for this rehearsal.

The live EAS test is not considered complete until the transactions and
independent read-back verification have actually succeeded.

## Cost guardrails

| Item | Allowed approach | Paid approach |
| --- | --- | --- |
| Python / Node dependencies | Open-source packages, committed lockfiles | Paid package service |
| Solidity execution | Local Foundry EVM | Paid hosted EVM |
| CI | Public-repository free runner allocation | Paid runner upgrade |
| Ethereum integration | Sepolia + faucet ETH | Mainnet ETH or purchased test ETH |
| RPC | Free public endpoint or self-hosted node | Metered paid RPC |
| Block explorer | Public explorer read-only access | Paid explorer subscription |

**Hard stop:** any workflow that asks for a card, requires a paid tier, spends
mainnet assets, or introduces a non-zero project charge is outside this plan.
Stop and use the local test path instead.

## Current execution status

- Python tests: run locally and passed in the current working environment.
- Ruff CI rule set: run locally and passed.
- Public-surface validation: run locally and passed.
- npm production dependency audit: run locally and reported zero vulnerabilities.
- EAS SDK runtime import/schema smoke test: run locally and passed.
- GitHub Actions for the current reviewed commit: successful.
- Local Foundry binary: not installed in the current workstation environment;
  the pinned Foundry job is exercised by GitHub Actions.
- Sepolia deployment and live EAS transactions: not yet performed.
- No mainnet transaction has been authorized or performed.

This document is a cost-control policy, not a claim that the live testnet flow
has already been completed.
