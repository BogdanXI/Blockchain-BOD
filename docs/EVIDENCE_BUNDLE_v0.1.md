# BOD Evidence Bundle v0.1

**Status:** experimental format; not a stable interoperability standard.

## Purpose

A portable checkpoint records a deterministic repository-state commitment and references external evidence by SHA-256 digest. A checkpoint alone does not contain the bytes of those external evidence documents.

The Evidence Bundle format closes that specific availability gap: it packages one portable checkpoint together with the exact byte payload for every evidence digest referenced by that checkpoint. A verifier can validate the checkpoint and payload hashes without contacting the original CI service, evidence store or BOD service.

This is deliberately narrower than a full repository backup.

## Format

A bundle contains:

- schema: bod-evidence-bundle-v0.1;
- checkpoint: one complete bod-portable-checkpoint-v0.1;
- objects: sorted evidence payload objects;
- bundle_id: SHA-256 commitment over the canonical bundle document, excluding bundle_id.

Each object contains:

- digest: sha256:<lowercase hex>;
- media_type: must match the corresponding checkpoint evidence reference;
- size: exact payload size in bytes;
- data_base64: base64 encoding of the exact payload bytes.

The bundle verifier checks the outer commitment, portable checkpoint, strict object ordering, reference coverage, media type, base64 validity, byte length and SHA-256 digest. It rejects missing and unreferenced objects.

## Create and verify

Given a checkpoint and its evidence payload files, run:

    bod bundle-create checkpoint.json \
      --payload <sha256-hex>=./provenance.json \
      --payload <another-sha256-hex>=./sbom.cdx.json \
      --out release-evidence.bundle.json

    bod bundle-verify release-evidence.bundle.json
    python scripts/independent_verify.py release-evidence.bundle.json

The payload digest is the lowercase SHA-256 hex value without the sha256: prefix. Every evidence reference in the checkpoint must have exactly one supplied payload. The command intentionally fails closed if the set is incomplete.

## Security and trust boundaries

A successful verification proves only that:

1. the bundle has not changed relative to its own commitment;
2. the checkpoint is internally consistent;
3. every referenced evidence payload is present;
4. each payload matches its declared digest and media type.

It does not prove that the evidence is truthful, that a build was safe, that an issuer was authorized, or that a signature/DSSE envelope is cryptographically valid. The bundle_id is an unkeyed commitment, not a signature: anyone can rebuild a modified bundle and calculate a new bundle_id. Authenticity must come from a separately trusted signature or external checkpoint/anchor. Those checks remain the responsibility of format-specific verifiers and trust policy.

The format does not include repository source files. The portable checkpoint's repository snapshot is a manifest of paths, sizes and hashes, not a source archive. This prevents accidental publication of proprietary source code and avoids implying that a metadata manifest can restore file contents.

The v0.1 representation embeds payloads as base64 in JSON. This is simple and independently portable, but increases size and memory use. It is not intended for large build artifacts. A future version may define external content-addressed object storage or a streaming archive while preserving the same digest semantics.

Bundles are not encrypted or access-controlled. Evidence may contain confidential metadata, source fragments, credentials or personal data. Review payloads before packaging or publishing them. Do not include secrets.

## Structural evidence inspection\n\nBOD also provides a separate, deliberately limited structural inspector for selected in-toto, SLSA, DSSE, CycloneDX and SPDX JSON documents. It does not perform signature verification or full schema validation. See [Evidence format support](EVIDENCE_FORMAT_SUPPORT.md).\n\n## Current limitations

- One bundle contains one checkpoint; lineage is verified separately through the checkpoint graph/chain formats.
- The bundle carries raw evidence bytes but does not yet implement SLSA, in-toto, Sigstore, SPDX or CycloneDX semantic/signature validation.
- No independent external implementation has yet adopted this experimental format.
- No claim is made that BOD can restore the repository working tree from a checkpoint.

## Why this matters to BOD

This is a concrete step from “the checkpoint remembers evidence hashes” toward “the checkpoint can carry the evidence bytes needed for independent inspection.” It creates a falsifiable recovery capability that can be compared with exporting the same evidence from GitHub, Sigstore, Chainloop, Kosli or Archivista.

The next validation is to run a loss-of-origin scenario: remove access to the original evidence store and CI account, transfer only the bundle to a clean machine, and measure which evidence can still be verified and inspected. Compare that result with the same task using each alternative toolchain.
