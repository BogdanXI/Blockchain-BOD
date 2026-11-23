import { ethers } from "ethers";
import { createRequire } from "node:module";
const require = createRequire(import.meta.url);
const { SchemaRegistry } = require("@ethereum-attestation-service/eas-sdk");
import { BOD_EAS_SCHEMA, EAS_DEPLOYMENTS } from "./schema.mjs";

const rpcUrl = process.env.ETHEREUM_SEPOLIA_RPC_URL;
const privateKey = process.env.ETHEREUM_SEPOLIA_PRIVATE_KEY;

if (!rpcUrl || !privateKey) {
  throw new Error("Set ETHEREUM_SEPOLIA_RPC_URL and ETHEREUM_SEPOLIA_PRIVATE_KEY.");
}

const provider = new ethers.JsonRpcProvider(rpcUrl);
const network = await provider.getNetwork();
if (network.chainId !== 11155111n) {
  throw new Error(`Refusing schema registration on chainId ${network.chainId}; expected Ethereum Sepolia (11155111).`);
}

const signer = new ethers.Wallet(privateKey, provider);
const deployment = EAS_DEPLOYMENTS[Number(network.chainId)];
const registry = new SchemaRegistry(deployment.schemaRegistry);
registry.connect(signer);

const transaction = await registry.register({
  schema: BOD_EAS_SCHEMA,
  resolverAddress: ethers.ZeroAddress,
  revocable: false,
});
const schemaUID = await transaction.wait();

process.stdout.write(JSON.stringify({
  status: "SCHEMA_REGISTERED",
  network: deployment.name,
  chainId: network.chainId.toString(),
  schemaRegistry: deployment.schemaRegistry,
  schema: BOD_EAS_SCHEMA,
  schemaUID,
  revocable: false,
  transaction: transaction.tx?.hash ?? null,
}, null, 2) + "\n");
