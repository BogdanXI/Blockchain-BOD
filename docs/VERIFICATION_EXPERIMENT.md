# Real evidence continuity and recovery experiment

**Date:** 22 November 2026  
**Scope:** real GitHub Actions SBOM and Sigstore attestation, bound to the exact PR merge tree, packaged by BOD, recovered after local origin copies were deleted, then verified offline.

## Objective

Test whether BOD can preserve a deterministic project-state commitment and carry the exact bytes of real third-party evidence, then hand the recovered payloads to the official cryptographic verifier.

The experiment checks four distinct properties:

1. The checkpoint's repository snapshot corresponds to the exact source tree recorded by the GitHub build provenance.
2. The BOD bundle contains every referenced evidence payload and passes independent integrity/completeness verification.
3. The recovered SBOM remains structurally inspectable.
4. The recovered SBOM and Sigstore bundle pass cryptographic verification against explicit GitHub workflow identity claims.

## Source build and attestation

- Public repository: BogdanXI/Blockchain-BOD
- GitHub Actions run: 45032926600
- Run head: 01cb1ecdecd782c787867299cfe4cd1e35b60b93
- PR merge commit recorded in provenance: 2cf637ada2bfb248e0126d948e5d2b287497b00a
- Exact GitHub merge-tree SHA: 21d965d40ffacb69b38e7f535977ed59bbe20ef1
- Workflow identity: https://github.com/BogdanXI/Blockchain-BOD/.github/workflows/ci.yml@refs/pull/4/merge
- Workflow event: pull_request
- Artifact: sbom-python / sbom-python.cdx.json
- Artifact ID: 14758497646
- SBOM SHA-256: 3ce448c9ecda91858d593a9312550abb88dea193e6e04469e706faa106974cea
- SBOM size: 6,665 bytes
- Sigstore bundle media type: application/vnd.dev.sigstore.bundle.v0.3+json
- Sigstore bundle SHA-256: 9495827045dd14fcfdaeb208edf13beb43cae81c8fe098dfcc92ca8a50b89592
- Sigstore bundle size: 10,684 bytes

The PR merge tree was reconstructed from the exact base and head commits. Its tree SHA matched the GitHub merge commit tree SHA returned by the GitHub API. BOD's repository snapshot covered 108 tracked files and produced state root:

    422e702cf152ad8770fc1335483a556cdedadb816fb83e7269023eb4c33f6ecd

## BOD checkpoint and bundle

One portable checkpoint was created with two evidence references:

- CycloneDX SBOM;
- Sigstore v0.3 attestation bundle.

Results:

- BOD checkpoint ID: 41774869170bc6b79ac53abd0cd9bf921e24024110a94a6069225252057bcad3
- BOD bundle ID: 69b5fd2b976cff9db6f4f9cee1c4ca826ac13e6869f054d2da82b9034dc02f8b
- Evidence objects: 2
- Total evidence payload bytes: 17,349
- Snapshot file count: 108

The BOD bundle was created through the Python API and then independently recreated through the installed CLI command bod bundle-create. Both paths produced the exact same bundle ID. The installed CLI command bod bundle-verify returned VALID_SELF_CONTAINED_BUNDLE.

## Recovery and verification

The local original-evidence directory was deleted after BOD bundle creation. Both payloads were extracted from the BOD bundle into a new recovery directory.

Then:

1. bod bundle-verify validated the BOD bundle and complete payload coverage.
2. bod evidence-inspect validated the recovered CycloneDX document: specVersion 1.4, 37 components.
3. bod evidence-verify github delegated to sigstore-python 4.5.1 with the expected workflow identity, repository, event, source SHA, workflow name and ref, using offline mode.
4. The Sigstore CLI returned exit code 0 and OK for the recovered SBOM.

BOD wrapper result:

- status: VALID
- signature_verification: VALID
- offline: true
- expected identity, repository, event, source SHA, workflow name and ref: matched

The recovered payloads passed verification without access to the deleted local original-evidence directory. The exact command and identity policy are reproducible using the details above and the CLI syntax in [Evidence format support](EVIDENCE_FORMAT_SUPPORT.md).

## Limits and interpretation

- The checkpoint contains a deterministic manifest of 108 tracked repository files (paths, sizes and hashes), not the source file contents. BOD does not restore the repository working tree from this bundle.
- The experiment proves that referenced evidence payloads can be carried, recovered and verified independently of their original local evidence directory. It does not prove that the SBOM is complete, accurate or semantically truthful.
- Offline verification used the locally available Sigstore trust root. Sigstore warned that offline mode does not refresh TUF trust metadata. A valid result does not establish that the local trust root includes the latest revocations or trust-root changes.
- The bundle ID is an unkeyed commitment, not a signature. Authenticity comes from the separately verified Sigstore attestation and its explicit identity policy, not from the BOD bundle ID alone.
- This is one manual GitHub Actions/Sigstore integration experiment. It is not yet a multi-provider benchmark, customer pilot or proof that BOD outperforms Chainloop, Kosli, Archivista or GUAC.
- BOD delegates cryptography to sigstore-python. It does not implement Sigstore signature, certificate or transparency verification itself.

## Reproduction sources

- GitHub Actions run: https://github.com/BogdanXI/Blockchain-BOD/actions/runs/45032926600
- GitHub repository attestations API: https://docs.github.com/en/rest/repos/attestations
- Sigstore verification: https://sigstore.github.io/sigstore-python/verify/
- Sigstore offline verification caveats: https://sigstore.github.io/sigstore-python/advanced/offline/
