#!/usr/bin/env bash
set -euo pipefail

NITRO_TESTNODE_COMMIT="${NITRO_TESTNODE_COMMIT:-72ac4bb1f07fadc108448ad5fae01ea2e044fe69}"
WORKDIR="${WORKDIR:-${RUNNER_TEMP:-/tmp}/bod-nitro-testnode}"

if ! command -v docker >/dev/null 2>&1; then
  echo "Docker is required for the full Nitro testnode."
  exit 2
fi
if ! docker info >/dev/null 2>&1; then
  echo "Docker daemon is unavailable."
  exit 2
fi

rm -rf "$WORKDIR"
git clone --filter=blob:none https://github.com/OffchainLabs/nitro-testnode.git "$WORKDIR"
git -C "$WORKDIR" checkout --detach "$NITRO_TESTNODE_COMMIT"

echo "NITRO_TESTNODE_COMMIT=$(git -C "$WORKDIR" rev-parse HEAD)"
echo "NITRO_TESTNODE_SOURCE=https://github.com/OffchainLabs/nitro-testnode"
echo "NITRO_TESTNODE_WORKDIR=$WORKDIR"

cd "$WORKDIR"
./test-node.bash --init --no-l2-traffic --no-l3-traffic --no-tokenbridge

echo "NITRO_RPC_PROBE"
curl --fail --silent --show-error \
  -H 'content-type: application/json' \
  --data '{"jsonrpc":"2.0","method":"eth_chainId","params":[],"id":1}' \
  http://127.0.0.1:8547

echo
curl --fail --silent --show-error \
  -H 'content-type: application/json' \
  --data '{"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":2}' \
  http://127.0.0.1:8547

echo
echo "NITRO_TESTNODE_BOOT_PASS"
