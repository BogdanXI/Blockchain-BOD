// Shared EAS schema for BOD release-continuity attestations.
// Register this exact schema string on each target chain; schema UIDs are chain-specific.
export const BOD_EAS_SCHEMA =
  "bytes32 projectId, bytes32 checkpointId, bytes32 portableCheckpointId, bytes32 gitCommit, bytes32 stateRoot, bytes32 manifestHash, bytes32 evidenceRoot, uint64 sequence";

export const EAS_DEPLOYMENTS = {
  1: {
    name: "Ethereum Mainnet",
    eas: "0xA1207F3BBa224E2c9c3c6D5aF63D0eb1582Ce587",
    schemaRegistry: "0xA7b39296258348C78294F95B872b282326A97BDF",
  },
  11155111: {
    name: "Ethereum Sepolia",
    eas: "0xC2679fBD37d54388Ce493F1DB75320D236e1815e",
    schemaRegistry: "0x0a7E2Ff54e76B8E6659aedc9103FB21c038050D0",
  },
};
