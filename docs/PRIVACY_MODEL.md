# BOD Privacy Model

**Status:** initial design policy; implementation and testing are incomplete.  
**Last reviewed:** 2026-11-22.

## 1. Purpose and claim boundary

BOD binds project-state and evidence commitments into portable checkpoints. The design goal is to minimize disclosure while allowing an independent verifier to check byte integrity and lineage.

BOD does not claim that hashes anonymize data. Public commitments and metadata may be linkable to a person, repository, release, organization or activity pattern.

## 2. Data classes

| Class | Examples | Default handling |
|---|---|---|
| Public by intent | Public source commit, public release identifier, public SBOM reference | May be referenced after review |
| Confidential project data | Private source, internal build logs, unreleased vulnerability reports, internal artifact names | Do not include in public checkpoint payloads |
| Secrets and credentials | Private keys, seed phrases, API tokens, passwords, signing material | Never capture, serialize, upload or anchor |
| Personal data | Names, email addresses, IP addresses, employee identifiers, wallet-to-person mappings | Exclude unless strictly necessary and lawfully handled |
| Derived metadata | Hashes, timestamps, project IDs, sequence numbers, publisher addresses | Treat as potentially sensitive and linkable |

## 3. On-chain data minimization

The Ethereum registry and EAS schema are intended to carry fixed-size commitments and lineage references only. They must not carry source files, build logs, full SBOMs or provenance documents, secrets, credentials, private signing material, personal data or private vulnerability details.

The EAS schema includes project, checkpoint, commit, state, manifest, evidence-root and sequence commitments. The project identifier and hashes may still enable correlation. A zero-address recipient does not make an attestation private.

## 4. Hashes are not anonymization

A hash of a predictable value can be guessed by dictionary attack. A public digest may be correlated with a known repository, file, release or dataset. A timestamp and sequence can reveal release cadence. A publisher address can be linked to other public activity.

Before publishing a commitment, operators should ask:

1. Is the underlying value public already?
2. Could the value be guessed or enumerated?
3. Does this commitment reveal the existence or timing of a confidential project event?
4. Can the identifier be correlated with a person or organization?
5. Is the commitment necessary for the intended verification claim?

Where correlation risk is unacceptable, do not publish the value or its direct hash. A future privacy-preserving commitment scheme would require a separate threat model and review; it is not currently implemented.

## 5. Capture and storage boundaries

- Capture only explicitly intended repository inputs.
- Review the tracked-file boundary before creating a public checkpoint.
- Do not place secrets in Git-tracked files, even temporarily.
- Keep evidence payloads off-chain and apply access control and retention rules at their storage location.
- Do not upload private evidence to public issue trackers, explorers, CI logs, artifacts or public artifact stores.
- Preserve the ability to verify public commitments without disclosing confidential payloads.

The current capture implementation uses Git-tracked paths and has path/symlink checks. That is not a complete data-loss-prevention system and does not replace operator review.

## 6. Retention, deletion and immutability

On-chain commitments and public attestations may be practically irreversible. Do not publish personal or confidential data on the assumption it can later be deleted.

Off-chain evidence owners must define retention periods, access control, deletion and backup procedures. Removing an off-chain artifact may make a historical checkpoint unverifiable for availability, even though its digest remains on-chain. BOD must report this distinction rather than implying that a hash preserves the underlying data.

## 7. Privacy tests required

Before a production privacy claim, add automated tests that demonstrate:

- known secret patterns and private-key fixtures are rejected by public-surface checks;
- private file contents are not copied into checkpoint metadata;
- symlink targets outside the capture boundary are not dereferenced;
- checkpoint and EAS payloads contain only the documented fields;
- logs do not print environment secrets or credential-bearing URLs;
- deterministic identifiers do not accidentally include usernames, email addresses or local absolute paths.

These tests are planned, not all implemented. Current public-surface scanning covers selected high-confidence credential patterns and private path names only.

## 8. Incident handling

If sensitive information is published accidentally:
1. stop further publication and rotate exposed credentials immediately;
2. preserve minimal evidence needed for incident analysis without redistributing the secret;
3. assess whether the data is on-chain, in Git history, CI logs, artifacts, caches or third-party indexes;
4. request removal from controllable off-chain services, while documenting that blockchain data cannot be reliably erased;
5. notify affected parties where required and publish a sanitized incident note.

## 9. Non-claims

BOD currently does not provide zero-knowledge proofs, confidential transactions, anonymous attestations, private on-chain storage, automatic personal-data detection or guaranteed erasure. It does not make public metadata unlinkable.
