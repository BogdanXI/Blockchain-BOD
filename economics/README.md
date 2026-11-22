# Historical BOD token and economics experiments

**Status: archived experimental material. Not part of the active Ethereum product or deployment plan.**

The current Ethereum product is an ETH-gas-paid, tokenless checkpoint registry. It has no BOD ERC-20, token issuance, staking, rewards, treasury, verifier economics or token-based fee requirement.

The repository retains earlier BOD token and economic experiments for research traceability. Related source modules and tests remain in the repository but are excluded from the active Python wheel. They are not final policy and must not be used in a grant application, deployment, investor presentation or production implementation as approved economics.

## Known reconciliation issue

The historical files are internally inconsistent:

- `protocol/genesis/BOD_TOKEN_POLICY_v0.1.yml` specifies a 100,000,000 BOD maximum supply and 25,000,000 genesis minted supply.
- `src/bod_economy.py` currently models a 1,000,000,000 BOD maximum supply and 300,000,000 genesis minted supply.
- The Python economic tests exercise the latter model.

This mismatch is a known unresolved research artifact. No token contract should be deployed and no supply figure should be represented as final until a separate, explicit protocol decision reconciles the model, tests, policy and implementation.

## Scope rule

Do not add a BOD token to the Ethereum checkpoint registry merely to make the product appear more blockchain-native. Ethereum gas is paid in ETH. Revisit token economics only if independent user research demonstrates a necessary protocol-level function that cannot be served more simply without a token.
