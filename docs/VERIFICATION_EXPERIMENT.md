# Evidence verification experiment

**Date:** 22 November 2026  
**Scope:** real GitHub Actions SBOM attestation; offline Sigstore verification.

## Objective

Verify that BOD can preserve and invoke an established cryptographic verifier rather than treating JSON structure or a SHA-256 reference as proof of authenticity.

## Source evidence

- Public repository: BogdanXI/Blockchain-BOD
- GitHub Actions run: 45030724173
- Run head: 8968f8f93b64f06044bc59cdb4859d6e5ae9e62f
- Artifact: sbom-python
- Artifact ID: 14757571608
- Subject file: sbom-python.cdx.json
- Subject SHA-256: f5a70d32a8fabdbe57e8932c10a84c98f7deb556856d5bf58b2f6d3dd52679fb
- Attestation bundle media type: application/vnd.dev.sigstore.bundle.v0.3+json
- Workflow identity: https://github.com/BogdanXI/Blockchain-BOD/.github/workflows/ci.yml@refs/pull/4/merge
- Workflow event: pull_request
- Source revision recorded by the attestation: 38b4249c27548a0ddba88bdc5a8bc15602678453

## Verification procedure

1. Download the SBOM artifact from GitHub Actions run 45030724173.
2. Compute the SHA-256 digest and request the corresponding repository attestation from the GitHub REST API.
3. Save the returned Sigstore bundle.
4. Install sigstore-python 4.5.1 in an isolated temporary environment.
5. Invoke BOD's evidence verification wrapper with the exact expected GitHub workflow identity, repository, event, source SHA and ref, using offline verification.

Example:

    bod evidence-verify github sbom-python.cdx.json \
      --bundle sbom-python.bundle.json \
      --offline \
      --cert-identity 'https://github.com/BogdanXI/Blockchain-BOD/.github/workflows/ci.yml@refs/pull/4/merge' \
      --trigger pull_request \
      --sha 38b4249c27548a0ddba88bdc5a8bc15602678453 \
      --workflow-name CI \
      --repository BogdanXI/Blockchain-BOD \
      --ref refs/pull/4/merge

## Result

The official sigstore-python CLI returned exit code 0 and OK for the subject. The BOD wrapper returned:

- status: VALID
- signature_verification: VALID
- offline: true
- expected workflow identity, repository, event, source SHA and ref: matched

This is a real external attestation bundle, not a synthetic fixture. It demonstrates that BOD can delegate cryptographic signature, certificate identity, GitHub workflow claim and transparency evidence verification to the upstream Sigstore implementation.

## Limits

- The attestation belongs to the earlier run and PR merge ref recorded above, not the latest public branch head.
- Offline verification used the locally available Sigstore trust root. Sigstore warned that offline mode does not refresh TUF trust metadata. A valid result therefore does not establish that the local trust root includes the latest revocations or trust-root changes.
- The result proves the attested SBOM file matches the signed subject and expected workflow identity under the supplied trust configuration. It does not prove that the SBOM is complete, accurate or semantically truthful.
- This is one manual integration experiment, not yet an automated CI gate or multi-provider interoperability result.
- BOD does not implement cryptography itself; it delegates to sigstore-python. The verifier version and trust-root policy must be recorded in a production workflow.

## Reproduction sources

- GitHub Actions run: https://github.com/BogdanXI/Blockchain-BOD/actions/runs/45030724173
- GitHub repository attestations API: https://docs.github.com/en/rest/repos/attestations
- Sigstore verification: https://sigstore.github.io/sigstore-python/verify/
- Sigstore offline verification caveats: https://sigstore.github.io/sigstore-python/advanced/offline/
