# Competitive landscape: software supply-chain evidence

**Research snapshot:** 22 November 2026  
**Purpose:** identify direct substitutes and define a defensible comparison boundary. This is a public-documentation review, not a hands-on benchmark or market-share study.

## Direct and adjacent products

| Project | What its public documentation says it does | Overlap with BOD | What BOD must prove beyond it |
|---|---|---|---|
| [Chainloop](https://github.com/chainloop-dev/chainloop) | Open-source SDLC evidence store and policy engine. Collects SBOMs, SLSA provenance, VEX, SARIF, QA reports and other evidence; crafts signed in-toto attestations; supports content-addressable storage and integrations. | Very high: evidence collection, signing, storage, workflow context and policy enforcement. | A portable, self-contained evidence package and predecessor-linked state history that can be verified without its control plane or configured storage. Test against Chainloop's own export/storage and offline deployment capabilities; do not assume those are absent. |
| [Kosli Evidence Store](https://www.kosli.com/evidence-store/) | Append-only record of SDLC events, connecting pipeline attestations and runtime environment changes; supports search across evidence trails, attachments and artifacts. | Very high: immutable evidence history and release/runtime traceability. | Independent transfer and verification of a checkpoint lineage and all required evidence bytes after the source service is unavailable, with measurable operator/time advantage. |
| [Archivista](https://github.com/in-toto/archivista) | Graph and storage service for in-toto attestations; stores signed attestations, supports relationship queries, policy validation and export/download for air-gapped transfer. | Very high: attestation graph, storage, discovery and portability. | Demonstrate a distinct state-transition continuity model and clean-room recovery benefit beyond exported attestations and their graph relationships. |
| [GUAC](https://docs.guac.sh/guac/) | Ingests SBOMs, SLSA attestations, DSSE/in-toto and other metadata into a graph for querying supply-chain relationships, vulnerabilities and known/unknown information. | High: evidence ingestion and graph-based reasoning. | Demonstrate durable, portable, predecessor-linked snapshots and recovery of the evidence bytes—not merely another graph or query layer. |
| [Sigstore / Rekor](https://docs.sigstore.dev/) | Artifact signing and transparency infrastructure, including public log records and verification material. | Medium/high: tamper evidence, public transparency and independent verification. | Prove longitudinal continuity across complete evidence sets and checkpoints, while respecting the existing signing/log trust model. |
| [GitHub Artifact Attestations](https://docs.github.com/en/actions/concepts/security/artifact-attestations) | Signed attestations for artifact provenance and related verification in GitHub workflows. | Medium: verifiable release provenance. | Show useful portability across providers and time after the GitHub workflow/account is unavailable, not merely a second way to verify provenance. |
| [SLSA / in-toto](https://slsa.dev/spec/v1.2/) | Standards for describing and verifying build/source provenance and supply-chain steps. | Foundational standards rather than a direct BOD product competitor. | Integrate their native statements and verification tools; never imply that BOD replaces their semantic or signature checks. |

## What this review establishes

1. Evidence collection, signed attestation storage, immutable SDLC histories, metadata graphs, and export are already implemented by real projects.
2. Portability and air-gap export are not unique to BOD. Archivista explicitly documents export for transfer across air gaps; Chainloop documents content-addressable storage and self-hosted deployment; GUAC supports local ingestion and graph queries.
3. A blockchain anchor is not a differentiator by itself. Existing transparency logs already provide independently verifiable records.
4. The only plausible BOD wedge remaining is a narrowly scoped combination: deterministic project/evidence state checkpoints, explicit predecessor and branch relationships, self-contained payload packaging, and independent clean-room verification without a BOD service.
5. This wedge is still a hypothesis. Public documentation cannot establish whether these competitors already satisfy the same user workflow when configured correctly.

## Required head-to-head test

Use identical source commits, provenance statements, SBOMs and test reports. Give each toolchain the same task: recover and independently inspect the evidence supporting a historical release after the original CI workspace and evidence-store credentials have been revoked.

Measure:

- payloads and metadata recovered;
- missing, corrupt and unverifiable evidence;
- correctness of predecessor/fork reconstruction;
- clean-room setup time and operator actions;
- whether vendor/service credentials are required;
- storage size and infrastructure cost;
- whether signatures and format-specific trust policies are actually verified.

Compare at least:
- Git + signed tags + exported SLSA/in-toto + Sigstore bundles;
- Chainloop OSS;
- Kosli (with its documented export/API path);
- Archivista;
- GUAC plus its source evidence stores;
- BOD with and without Ethereum anchoring.

Publish exact versions, configuration, scripts, raw non-sensitive results and negative findings. Do not claim BOD wins unless the measurements show it.

## Product boundary after this review

BOD should not build another central evidence store, policy engine, SBOM graph database, signing service or transparency log. It should consume existing evidence, preserve a deterministic longitudinal record of what evidence belonged to each project state, and make the relevant payloads independently portable and verifiable.

If the head-to-head test shows that Chainloop, Archivista or another existing tool already provides equivalent clean-room recovery with lower complexity, BOD should integrate with that tool or narrow its scope rather than duplicate it.

## Sources

- Kosli Evidence Store: https://www.kosli.com/evidence-store/
- Chainloop open-source project: https://github.com/chainloop-dev/chainloop
- Chainloop product tiers: https://chainloop.com/pricing/
- Archivista: https://github.com/in-toto/archivista
- GUAC documentation: https://docs.guac.sh/guac/
- GUAC supported ingestion and components: https://docs.guac.sh/guac/guac-components/
- Sigstore documentation: https://docs.sigstore.dev/
- GitHub Artifact Attestations: https://docs.github.com/en/actions/concepts/security/artifact-attestations
- SLSA v1.2: https://slsa.dev/spec/v1.2/
