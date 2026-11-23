# Evidence format inspection

**Status:** dependency-free structural inspection; not full standards validation.

BOD can inspect selected evidence payload formats before they are added to a checkpoint or reviewed after recovery.

## Supported JSON structures

| Format | Current inspection boundary |
|---|---|
| in-toto Statement v1 | Checks statement type, subject array, digest descriptors and predicate type. |
| SLSA Build Provenance v1 | Checks the in-toto Statement v1 wrapper plus required buildDefinition/buildType/externalParameters and runDetails/builder.id structure. |
| DSSE with in-toto JSON payload | Checks payload type, base64 encoding, statement structure and signature field encoding/count. It does not verify signatures. |
| CycloneDX JSON | Checks BOM format marker, specification version type, optional BOM version, components array and metadata object. |
| SPDX JSON 2.x | Checks core document identity, CC0-1.0 data license, namespace, creation metadata and package array. SPDX 3.x is not implemented. |

## Command

    bod evidence-inspect provenance.json
    bod evidence-inspect sbom.cdx.json
    bod evidence-inspect report.spdx.json
    bod evidence-inspect envelope.dsse.json --format dsse

The default format is auto-detection. The command reports STRUCTURE VALID only when the supported structural checks pass.

## Cryptographic verification

BOD can delegate actual Sigstore verification to the official sigstore-python CLI through the evidence-verify command. GitHub Actions provenance claims can be checked with the github mode; generic identity and OIDC issuer constraints can be checked with identity mode. The CLI must be installed separately (sigstore-python 4.x).

See the [real offline verification experiment](VERIFICATION_EXPERIMENT.md) for a completed check against a GitHub-generated SBOM attestation.

## Trust boundary

This is intentionally not advertised as full JSON Schema or CUE validation. The structural inspector does not verify DSSE/Sigstore signatures, certificate chains, transparency inclusion proofs, signer identity, builder trust, policy compliance, SBOM completeness or semantic truth. The separate evidence-verify command delegates Sigstore bundle verification to sigstore-python when explicitly invoked with expected identity claims.

Use the format's dedicated verifier and trust policy for cryptographic and semantic validation. BOD's evidence-verify wrapper delegates to sigstore-python and records the expected identity claims and result; it does not implement Sigstore cryptography itself. For Sigstore bundles, the official sigstore-python CLI supports identity/issuer verification and offline modes; offline operation requires an appropriately current trust root. GitHub documents offline artifact-attestation verification with a downloaded bundle and trusted root. BOD records and transports the resulting evidence; it must not silently substitute a lightweight structural check for the actual verifier.

## Primary specifications

- in-toto Statement v1: https://github.com/in-toto/attestation/blob/main/spec/v1/statement.md
- SLSA v1.2 Build Provenance: https://slsa.dev/spec/v1.2/build-provenance
- CycloneDX JSON 1.7: https://cyclonedx.org/docs/1.7/json/
- SPDX 2.3 document creation information: https://spdx.github.io/spdx-spec/v2.3/document-creation-information/
- Sigstore offline verification: https://sigstore.github.io/sigstore-python/advanced/offline/
- GitHub artifact attestations offline verification: https://docs.github.com/en/actions/how-tos/secure-your-work/use-artifact-attestations/verify-attestations-offline
