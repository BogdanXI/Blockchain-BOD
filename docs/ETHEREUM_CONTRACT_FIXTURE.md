# Ethereum contract deployment fixture: WETH9

**Assessment date:** 24 November 2026

**Fixture status:** public deployment record captured; source-to-deployment continuity incomplete

**Profile:** `bod-ethereum-release-profile-v0.1`

**Network:** Ethereum Mainnet (chain ID 1)

## 1. Purpose and limits

This fixture exercises the BOD Ethereum Release Profile against one real public contract deployment. It is deliberately a gap-preserving example, not a claim that the full historical release can be reconstructed.

The record captures the deployment transaction and block, Sourcify v2 source/compiler metadata and a current runtime-code observation, and a candidate upstream repository revision. It does **not** establish that the candidate Git revision is the exact source revision compiled for the deployment, recover the original build inputs or provenance, or reproduce the full contract lifecycle.

The machine-readable record is [weth9-mainnet-2017-12-12.json](../examples/ethereum-release-profile/weth9-mainnet-2017-12-12.json). It passes BOD structural validation with 12 explicit gaps. Structural validation does not perform cryptographic verification, query the chain, verify Sourcify, or establish semantic truth.

## 2. Deployment facts

| Field | Captured value | Source |
|---|---|---|
| Contract | WETH9 / Wrapped Ether | Sourcify and Etherscan |
| Chain | Ethereum Mainnet, chain ID 1 | Sourcify API v2 |
| Address | `0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2` | [Etherscan contract](https://etherscan.io/address/0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2) |
| Creation transaction | `0xb95343413e459a0f97461812111254163ae53467855c0d73e0f1e7c5b8442fa3` | [Etherscan transaction](https://etherscan.io/tx/0xb95343413e459a0f97461812111254163ae53467855c0d73e0f1e7c5b8442fa3) |
| Block | `4719568` | Etherscan transaction and block page |
| Block hash | `0xd6e5f60d6b2367e74cd2aa520dbeb104826c3932eb482cc16e7f7ef5f8f74799` | [Etherscan block](https://etherscan.io/block/4719568) |
| Deployment time | 12 December 2017, 11:17:35 UTC | Etherscan transaction page |
| Deployer | `0x4F26FfBe5F04ED43630fdC30A87638d53D0b0876` | Sourcify API v2 and Etherscan |

Etherscan reports the creation transaction as successful and the block status as **Finalized**. A read-only request to the public PublicNode Ethereum RPC also returned a finalized head at block `26480182`, above deployment block `4719568`. The profile records the observation time and links to the historical block page. No transaction was submitted by this project.

## 3. Sourcify and compiler metadata

A single-contract lookup was made through the official [Sourcify Server API v2](https://docs.sourcify.dev/docs/api/). The captured metadata included:

- compiler: `solc 0.4.19+commit.c4cbbb05`;
- optimizer: disabled, `runs: 200`;
- compilation target: `WETH9.sol:WETH9`;
- Sourcify source-file Keccak-256: `0x4f98b4d0620142d8bea339d134eecd64cbd578b042cf6bc88cb3f23a13a4c893`.

The durable capture available for this fixture did not preserve the API response's top-level `exact_match` versus `match` classification. The profile retains the Sourcify provider and contract-record URI, sets `deployment.source_verification.match_type` to null, and records a gap; it does not guess the classification or reduce verification to a generic boolean. Neither Sourcify classification is a security audit or proof that a contract is safe.

The settings digest in the fixture is SHA-256 over the compact, lexicographically key-sorted JSON serialization of this settings object:

```json
{"libraries":{},"optimizer":{"enabled":false,"runs":200},"remappings":[]}
```

This is a digest of the settings object captured from Sourcify metadata. It is not a digest of the original compiler input or an independently reproduced compiler run.

## 4. Source-revision investigation

The public [Dapphub `ds-weth` repository](https://github.com/dapphub/ds-weth) contains a candidate source revision committed on 1 December 2017, before the deployment:

- candidate commit: `abb410d7a927f5c9b42e3bca83fa5701ed9a36b4`;
- candidate Git tree: `b878d5c6840050be1aeff4383401695e1b31dab9`;
- candidate file: [`src/weth9.sol`](https://github.com/dapphub/ds-weth/blob/abb410d7a927f5c9b42e3bca83fa5701ed9a36b4/src/weth9.sol);
- SHA-256 of that file at the candidate commit: `763dd16d90b9b591eca5b24b733301f500fbe18eeabc7bead848f60f2771857a`;
- Keccak-256 of that file: `0xaa3a59f136a5792dd25eacd4b599758b2f6280baef604f2148e120f7a0d39b73`.

The Sourcify metadata reports a different Keccak-256 source hash for `WETH9.sol`: `0x4f98b4d0620142d8bea339d134eecd64cbd578b042cf6bc88cb3f23a13a4c893`.

Therefore the candidate Dapphub file is **not byte-identical** to the source file represented by the Sourcify metadata. The candidate commit is retained only as a research lead; it is not written into `release.source_commit` or `release.source_tree`. Those profile fields are null and the missing source revision is explicitly recorded as a gap. This avoids falsely claiming that a repository revision produced the deployed bytecode.

## 5. Runtime-code observation and historical limitation

A read-only `eth_getCode` request to `https://ethereum-rpc.publicnode.com` at `latest` returned 3,124 bytes for the WETH9 address. SHA-256 of the decoded runtime bytecode was:

`5566bf50796faf93c9b6f6adacd3b32c70bfe16b48ffc59db6cd144cbdc89739`

This digest is stored as a **current runtime-code observation**, not as the historical deployment-block runtime digest. The same public RPC endpoint reported that historical state at block `4719568` was unavailable because its retained range began at block `15500000`. Accordingly, `deployment.runtime_bytecode_digest` remains null and the profile records a gap. The current code hash must not be presented as a historical deployment hash without an archive-state comparison.

## 6. Explicit gaps

The 12 gaps in the machine-readable fixture are intentional:

1. Exact upstream source commit not established.
2. Exact upstream source tree not established.
3. Candidate Dapphub source revision not proven to correspond to Sourcify's deployed source.
4. Authenticated builder identity unavailable.
5. SLSA/in-toto build provenance unavailable.
6. Original Standard JSON compiler input unavailable.
7. Original compiler output bytecode artifact not archived.
8. ABI payload not separately archived and digested in this fixture.
9. Historical runtime bytecode at the deployment block not retrieved.
10. Sourcify's top-level `exact_match` versus `match` classification was not retained in the durable fixture record.
11. Test report for the exact deployed source revision unavailable.
12. Independent security audit for the exact deployed source revision unavailable.

The gaps are not failures of the WETH9 contract. They describe what this fixture has and has not established about the historical release evidence.

## 7. What this fixture demonstrates for BOD

- The experimental profile can represent a real contract deployment using public chain and verification records.
- The absence of a retained Sourcify match classification is explicit rather than guessed or collapsed into a boolean.
- Compiler settings can be captured independently of a build-provenance claim.
- Unknown source lineage, missing build provenance and unavailable historical state can be represented as explicit gaps.
- A current runtime-code observation is distinguished from a historical deployment artifact.

It does **not** demonstrate a complete source-to-build-to-deployment chain, an upgrade lineage, offline recovery of all historical evidence, a security assessment, a comparative advantage over existing tools, or independent reproduction by another operator.

## 8. Temporary BOD evidence-bundle recovery experiment

A temporary local BOD checkpoint was created with two evidence references: the candidate Dapphub source file and the current runtime-bytecode observation. Their exact bytes were supplied to `bod bundle-create`.

- Bundle ID: `403df2f82c29035049b4188a11b0af0199726d63a434993d54c9cea72e2a5416`.
- Checkpoint ID: `fb524b107a42f2586f75e0469efe0f8c88141c440bb6e53e60f463af3ecef03c`.
- Evidence objects: 2.
- Payload bytes: 40,772.
- `bod bundle-verify`: `VALID_SELF_CONTAINED_BUNDLE`.
- Separate `scripts/independent_verify.py`: `VALID_SELF_CONTAINED_BUNDLE`.
- Original payload files and checkpoint were deleted before extraction.
- `bod bundle-extract` recovered both payloads into a new directory; SHA-256 was recomputed and matched for both files.

This was a loss-of-origin simulation using a temporary local Git repository and a fresh extraction directory on the same workstation. It was **not** an external-machine or independent-operator reproduction. The bundle was not committed to the public repository: it contains a third-party GPL-licensed source file and a chain-observed binary payload, while the small profile fixture and reproducible instructions are sufficient for public review.

The bundle verifier reported `semantic_truth: NOT_ASSERTED`, `bundle_authenticity: NOT_ASSERTED` and `repository_source: NOT_INCLUDED`. The experiment proves selected payload recovery and digest integrity only. It does not prove that the candidate source produced the deployed bytecode or restore the upstream repository working tree.

## 9. Single-sample archive baseline comparison

A second temporary run compared the same two evidence payloads with a plain archive baseline. The baseline tarball contained the candidate source file, current runtime-code observation, a JSON evidence manifest and a SHA-256SUMS file. Both paths were recovered and checked:

| Format | Size |
|---|---:|
| Raw evidence payloads | 40,772 bytes |
| BOD self-contained JSON bundle | 56,804 bytes |
| BOD JSON compressed with gzip -9 | 21,285 bytes |
| tar.gz with manifest and SHA256SUMS | 14,724 bytes |

The compressed BOD bundle was **44.5% larger** than the tar.gz baseline in this sample. Both BOD bundle verification/extraction and tar extraction plus `sha256sum -c` succeeded. The BOD bundle additionally carries the checkpoint, snapshot commitment and typed evidence references; the tar baseline does not encode BOD predecessor/fork semantics. This fixture used a genesis checkpoint only, so it did not measure multi-release lineage or fork reconstruction.

This is one small payload-size/recovery comparison, not a performance benchmark. No elapsed-time measurement was taken, and no Chainloop, Kosli, Archivista or GUAC workflow was tested. The result does not support a storage-size advantage for BOD. It reinforces the intended boundary: BOD's possible value is checkpoint continuity and explicit evidence relationships, not replacing efficient archive formats.

## 10. Reproduction and cost boundary

All observations used for this fixture are public read-only records. No paid RPC/API subscription, wallet, ETH, transaction, contract deployment, EAS schema registration or attestation was used. The fixture itself is locally structurally validated by `bod profile-validate` and validated against the Draft 2020-12 JSON Schema.

Sourcify's API guidance requests single-contract lookups, reuse of responses, descriptive User-Agent values and exponential backoff on errors. No bulk query or crawl was performed. The WETH9 fixture uses one contract record; a separate single-contract lookup was used to inspect one alternative candidate during fixture selection.

## 11. Sources

- [Sourcify Server API v2 documentation](https://docs.sourcify.dev/docs/api/)
- [Sourcify WETH9 contract record](https://sourcify.dev/server/v2/contract/1/0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2?fields=deployment,compilation,metadata,sources,creationMatch,runtimeMatch,verifiedAt,proxyResolution)
- [Sourcify API v2 lookup endpoint](https://sourcify.dev/server/v2/contract/1/0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2?fields=deployment,compilation,metadata,sources,creationMatch,runtimeMatch,verifiedAt,proxyResolution)
- [Dapphub `ds-weth` candidate commit](https://github.com/dapphub/ds-weth/commit/abb410d7a927f5c9b42e3bca83fa5701ed9a36b4)
- [Etherscan creation transaction](https://etherscan.io/tx/0xb95343413e459a0f97461812111254163ae53467855c0d73e0f1e7c5b8442fa3)
- [Etherscan deployment block](https://etherscan.io/block/4719568)
- [PublicNode Ethereum RPC](https://ethereum-rpc.publicnode.com)
