# BOD Arbitrum Sepolia MetaMask E2E

Status: experimental testnet integration.

BOD can execute the Protocol v0.1 adapter flow on Arbitrum Sepolia through a browser wallet without placing a private key in the application.

## Network boundary

- Arbitrum Sepolia
- Chain ID: 421614
- RPC: https://sepolia-rollup.arbitrum.io/rpc
- Gas currency: ETH
- Production/mainnet execution is not enabled by this browser bridge.

## E2E flow

The browser bridge constructs the deterministic integration payloads and asks MetaMask to approve each state-changing transaction:

1. deploy disposable TestBODToken;
2. deploy BODProtocolAdapterV0_1;
3. approve 1,250 test BOD;
4. create Task;
5. submit Candidate and EvidenceRoot;
6. commit VerificationRoot;
7. settle the selected Candidate;
8. verify the final State Root and adapter token balance.

The bridge accepts the run only when the observed State Root matches the deterministic settlement root and the adapter retains zero BOD after settlement.

## Reproducibility

Browser artifacts are generated from the tracked Solidity contracts using Solidity 0.8.24, optimizer 200 and viaIR. The browser payload construction follows the same SHA-256 commitment inputs as the chain-neutral integration harness.

This tooling is for Arbitrum Sepolia experimentation. It does not define BOD consensus, finalize token economics, or authorize Arbitrum One deployment.

## Wallet boundary

The bridge uses the injected EIP-1193 wallet provider through ethers BrowserProvider. Wallet approvals happen in MetaMask. The bridge does not request or process seed phrases, private keys, or keystores.

See the official Arbitrum documentation for the application deployment path and chain parameters.
