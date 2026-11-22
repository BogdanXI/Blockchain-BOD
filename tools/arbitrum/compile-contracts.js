const fs = require("node:fs");
const path = require("node:path");
const solc = require("./node_modules/solc");

const sourceDirectory = path.resolve(__dirname, "../../protocol/arbitrum");
const sources = {};

for (const fileName of fs.readdirSync(sourceDirectory).sort()) {
  if (!fileName.endsWith(".sol")) continue;
  sources[fileName] = {
    content: fs.readFileSync(path.join(sourceDirectory, fileName), "utf8"),
  };
}

if (Object.keys(sources).length === 0) {
  throw new Error("No Solidity sources were found");
}

const input = {
  language: "Solidity",
  sources,
  settings: {
    optimizer: { enabled: true, runs: 200 },
    viaIR: true,
    outputSelection: { "*": { "*": ["abi", "evm.bytecode.object"] } },
  },
};

const output = JSON.parse(solc.compile(JSON.stringify(input)));
const diagnostics = output.errors || [];
for (const diagnostic of diagnostics) {
  if (diagnostic.severity === "error") {
    process.stderr.write(diagnostic.formattedMessage);
  }
}

if (diagnostics.some((diagnostic) => diagnostic.severity === "error")) {
  process.exit(1);
}

const contractCount = Object.values(output.contracts || {}).reduce(
  (total, contracts) => total + Object.keys(contracts).length,
  0,
);
console.log(
  `Solidity compilation passed: ${Object.keys(sources).length} source files, ` +
    `${contractCount} contracts, solc ${solc.version()}`,
);
