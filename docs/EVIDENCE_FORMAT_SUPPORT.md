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

## Trust boundary

This is intentionally not advertised as full JSON Schema or CUE validation. It does not verify DSSE/Sigstore signatures, certificate chains, transparency inclusion proofs, signer identity, builder trust, policy compliance, SBOM completeness or semantic truth.

Use the format's dedicated verifier and trust policy for cryptographic and semantic validation. BOD records and transports the resulting evidence; it must not silently substitute a lightweight structural check for the actual verifier.

## Primary specifications

- in-toto Statement v1: https://github.com/in-toto/attestation/blob/main/spec/v1/statement.md
- SLSA v1.2 Build Provenance: https://slsa.dev/spec/v1.2/build-provenance
- CycloneDX JSON 1.7: https://cyclonedx.org/docs/1.7/json/
- SPDX 2.3 document creation information: https://spdx.github.io/spdx-spec/v2.3/document-creation-information/
