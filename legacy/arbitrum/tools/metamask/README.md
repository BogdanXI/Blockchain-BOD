# BOD MetaMask bridge

This browser bridge is the signing surface for the Arbitrum Sepolia integration.

## Boundary

- Network: Arbitrum Sepolia, chain ID 421614.
- Provider: injected EIP-1193 provider from MetaMask.
- Signer: ethers.BrowserProvider(window.ethereum) and the connected wallet signer.
- Private keys, seed phrases and keystores never enter the page, repository or runner.
- Arbitrum One/mainnet execution is not exposed by this bridge.
- Every state-changing transaction is submitted through MetaMask and requires wallet approval.

## E2E sequence

The Run Sepolia E2E action executes the deterministic integration flow:

1. deploy disposable TestBODToken;
2. deploy BODProtocolAdapterV0_1;
3. approve 1,250 BOD;
4. create Task;
5. submit Candidate;
6. commit VerificationRoot;
7. settle the selected Candidate;
8. read the final State Root and token balances;
9. require adapter BOD balance to be zero.

The browser payload construction mirrors BODArbitrumHarness. The bridge is an execution surface, not a second protocol implementation.

## Artifacts

tools/metamask/artifacts contains deterministic Solidity 0.8.24, optimizer-200, viaIR artifacts generated from the tracked contracts. They are testnet execution artifacts only.

## Run locally

Serve this directory over HTTP rather than opening the HTML directly:

    python3 -m http.server 8765 --bind 127.0.0.1 --directory tools/metamask

Then open http://127.0.0.1:8765/bridge.html in Chromium with MetaMask installed.

The bridge checks Arbitrum Sepolia before enabling the E2E controls. A wallet must hold Arbitrum Sepolia ETH for gas and must explicitly approve each transaction in MetaMask.

This bridge does not claim that a live deployment has occurred until transaction hashes and on-chain verification output are observed.
