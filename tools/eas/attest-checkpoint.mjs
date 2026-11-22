import { createHash } from "node:crypto";
import { execFileSync } from "node:child_process";
import { readFile } from "node:fs/promises";
import { ethers } from "ethers";
import { EAS, NO_EXPIRATION, SchemaEncoder, SchemaRegistry } from "@ethereum-attestation-service/eas-sdk";
import { BOD_EAS_SCHEMA, EAS_DEPLOYMENTS } from "./schema.mjs";

function canonical(value) {
  if (Array.isArray(value)) return `[${value.map(canonical).join(",")}]`;
  if (value && typeof value === "object") {
    return `{${Object.keys(value).sort().map(k => `${JSON.stringify(k)}:${canonical(value[k])}`).join(",")}}`;
  }
  return JSON.stringify(value);
}

function sha256Hex(value) {
  return "0x" + createHash("sha256").update(value).digest("hex");
}

const [checkpointPath] = process.argv.slice(2);
if (!checkpointPath) {
  throw new Error("Usage: npm run eas:attest-checkpoint -- checkpoint.json");
}

const rpcUrl = process.env.ETHEREUM_SEPOLIA_RPC_URL;
const privateKey = process.env.ETHEREUM_SEPOLIA_PRIVATE_KEY;
const schemaUID = process.env.BOD_EAS_SCHEMA_UID;
if (!rpcUrl || !privateKey || !schemaUID) {
  throw new Error("Set ETHEREUM_SEPOLIA_RPC_URL, ETHEREUM_SEPOLIA_PRIVATE_KEY and BOD_EAS_SCHEMA_UID.");
}
if (!/^0x[0-9a-fA-F]{64}$/.test(schemaUID)) throw new Error("BOD_EAS_SCHEMA_UID must be a bytes32 schema UID.");

const provider = new ethers.JsonRpcProvider(rpcUrl);
const network = await provider.getNetwork();
if (network.chainId !== 11155111n) {
  throw new Error(`Refusing attestation on chainId ${network.chainId}; expected Ethereum Sepolia (11155111).`);
}

const gitStatus = execFileSync("git", ["status", "--porcelain"], { encoding: "utf8" }).trim();
if (gitStatus) {
  throw new Error("Refusing to attest a dirty checkout. Commit the project state, then capture the checkpoint from that clean commit.");
}
execFileSync("python3", ["scripts/independent_verify.py", checkpointPath], { stdio: "inherit" });

const checkpoint = JSON.parse(await readFile(checkpointPath, "utf8"));
if (
  checkpoint?.schema !== "bod-portable-checkpoint-v0.1" ||
  !checkpoint.snapshot?.state_root ||
  !checkpoint.envelope?.project_id ||
  !checkpoint.checkpoint_id
) {
  throw new Error("Input is not a valid BOD portable checkpoint v0.1.");
}

const sequenceText = process.env.BOD_EAS_SEQUENCE ?? "0";
if (!/^(0|[1-9][0-9]*)$/.test(sequenceText)) {
  throw new Error("BOD_EAS_SEQUENCE must be a non-negative integer.");
}
const sequence = BigInt(sequenceText);
if (sequence > (1n << 64n) - 1n) throw new Error("BOD_EAS_SEQUENCE exceeds uint64.");

const parentUID = process.env.BOD_EAS_PARENT_UID ?? ethers.ZeroHash;
if (!/^0x[0-9a-fA-F]{64}$/.test(parentUID)) {
  throw new Error("BOD_EAS_PARENT_UID must be a bytes32 EAS attestation UID.");
}
if ((sequence === 0n) !== (parentUID === ethers.ZeroHash)) {
  throw new Error("Genesis requires sequence 0 and zero parent UID; later checkpoints require a parent UID and sequence > 0.");
}

const gitCommitText = execFileSync("git", ["rev-parse", "HEAD"], { encoding: "utf8" }).trim();
const projectId = ethers.keccak256(ethers.toUtf8Bytes(checkpoint.envelope.project_id));
const gitCommit = sha256Hex(gitCommitText);
const stateRoot = "0x" + checkpoint.snapshot.state_root;
const manifestHash = sha256Hex(canonical(checkpoint));
const evidenceRoot = sha256Hex(canonical(checkpoint.envelope.evidence));
const checkpointId = ethers.keccak256(ethers.AbiCoder.defaultAbiCoder().encode(
  ["bytes32", "uint256", "bytes32", "bytes32", "bytes32", "bytes32", "bytes32", "uint64", "bytes32"],
  [
    ethers.id("BOD_EAS_CHECKPOINT_V1"),
    network.chainId,
    projectId,
    gitCommit,
    stateRoot,
    manifestHash,
    evidenceRoot,
    sequence,
    parentUID,
  ],
));

const signer = new ethers.Wallet(privateKey, provider);
const easDeployment = EAS_DEPLOYMENTS[Number(network.chainId)];
const eas = new EAS(easDeployment.eas);
eas.connect(signer);

const schemaRegistry = new SchemaRegistry(easDeployment.schemaRegistry);
schemaRegistry.connect(provider);
const schemaRecord = await schemaRegistry.getSchema({ uid: schemaUID });
if (schemaRecord.uid === ethers.ZeroHash) throw new Error("EAS schema UID is not registered on Ethereum Sepolia.");
if (schemaRecord.schema !== BOD_EAS_SCHEMA) throw new Error("EAS schema string does not match the BOD checkpoint schema.");
if (schemaRecord.revocable !== false) throw new Error("BOD checkpoint schema must be registered as non-revocable.");
if (schemaRecord.resolver.toLowerCase() !== ethers.ZeroAddress.toLowerCase()) {
  throw new Error("BOD sample client requires the schema to use the zero-address resolver.");
}

if (sequence > 0n) {
  const parent = await eas.getAttestation(parentUID);
  if (parent.uid === ethers.ZeroHash) throw new Error("Parent EAS attestation does not exist.");
  if (parent.schema.toLowerCase() !== schemaUID.toLowerCase()) throw new Error("Parent attestation uses a different schema.");
  if (BigInt(parent.revocationTime) !== 0n) throw new Error("Parent attestation has been revoked.");
  if (parent.revocable !== false) throw new Error("Parent attestation is not immutable.");
  if (BigInt(parent.expirationTime) !== 0n && BigInt(parent.expirationTime) <= BigInt(Math.floor(Date.now() / 1000))) {
    throw new Error("Parent attestation has expired.");
  }
  const parentValues = ethers.AbiCoder.defaultAbiCoder().decode(
    ["bytes32", "bytes32", "bytes32", "bytes32", "bytes32", "bytes32", "uint64"],
    parent.data
  );
  if (parentValues[0].toLowerCase() !== projectId.toLowerCase()) throw new Error("Parent attestation belongs to a different project.");
  if (parentValues[1] === ethers.ZeroHash) throw new Error("Parent checkpoint ID is empty.");
  const parentSequence = BigInt(parentValues[6]);
  if (parentSequence + 1n !== sequence) throw new Error("BOD_EAS_SEQUENCE is not the parent's sequence plus one.");
  if ((parentSequence === 0n) !== (parent.refUID === ethers.ZeroHash)) {
    throw new Error("Parent refUID does not match its genesis/child sequence.");
  }
}

const encoder = new SchemaEncoder(BOD_EAS_SCHEMA);
const encodedData = encoder.encodeData([
  { name: "projectId", value: projectId, type: "bytes32" },
  { name: "checkpointId", value: checkpointId, type: "bytes32" },
  { name: "gitCommit", value: gitCommit, type: "bytes32" },
  { name: "stateRoot", value: stateRoot, type: "bytes32" },
  { name: "manifestHash", value: manifestHash, type: "bytes32" },
  { name: "evidenceRoot", value: evidenceRoot, type: "bytes32" },
  { name: "sequence", value: sequence, type: "uint64" },
]);

const transaction = await eas.attest({
  schema: schemaUID,
  data: {
    recipient: ethers.ZeroAddress,
    expirationTime: NO_EXPIRATION,
    revocable: false,
    refUID: parentUID,
    data: encodedData,
  },
});
const attestationUID = await transaction.wait();

process.stdout.write(JSON.stringify({
  status: "EAS_ATTESTATION_CREATED",
  network: easDeployment.name,
  chainId: network.chainId.toString(),
  eas: easDeployment.eas,
  schemaUID,
  attestationUID,
  parentUID,
  sequence: sequence.toString(),
  projectId,
  checkpointId,
  gitCommit,
  stateRoot,
  manifestHash,
  evidenceRoot,
  transaction: transaction.tx?.hash ?? null,
}, null, 2) + "\n");
