import { createRequire } from "node:module";
import { ethers } from "ethers";
import { BOD_EAS_SCHEMA, EAS_DEPLOYMENTS } from "./schema.mjs";

const require = createRequire(import.meta.url);
const { EAS, SchemaEncoder, SchemaRegistry } = require("@ethereum-attestation-service/eas-sdk");

if (typeof EAS !== "function" || typeof SchemaRegistry !== "function" || typeof SchemaEncoder !== "function") {
  throw new Error("EAS SDK CommonJS exports are unavailable.");
}

const eas = new EAS(EAS_DEPLOYMENTS[11155111].eas);
const registry = new SchemaRegistry(EAS_DEPLOYMENTS[11155111].schemaRegistry);
if (!eas || !registry) throw new Error("EAS SDK contract clients could not be constructed.");

const encoder = new SchemaEncoder(BOD_EAS_SCHEMA);
const encoded = encoder.encodeData([
  { name: "projectId", value: ethers.ZeroHash, type: "bytes32" },
  { name: "checkpointId", value: ethers.ZeroHash, type: "bytes32" },
  { name: "gitCommit", value: ethers.ZeroHash, type: "bytes32" },
  { name: "stateRoot", value: ethers.ZeroHash, type: "bytes32" },
  { name: "manifestHash", value: ethers.ZeroHash, type: "bytes32" },
  { name: "evidenceRoot", value: ethers.ZeroHash, type: "bytes32" },
  { name: "sequence", value: 0, type: "uint64" },
]);

if (!/^0x[0-9a-f]+$/i.test(encoded) || encoded.length !== 2 + 7 * 64) {
  throw new Error("EAS schema encoding did not produce the expected seven-word payload.");
}
if (EAS_DEPLOYMENTS[11155111]?.name !== "Ethereum Sepolia") {
  throw new Error("Ethereum Sepolia deployment configuration is missing.");
}

process.stdout.write("EAS SDK runtime import and schema encoding passed\n");
