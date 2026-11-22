# ADR-0105 — EC-0001 continuity resource-to-utility measurement boundary

Date: 2026-10-06
Status: Accepted for v0.1 measurement/calibration

## Context

The Phase 1.5 continuity MVP already measures durable state capture, delivery and recovery. The next executable boundary requires settlement execution, artifact availability/storage retention and network transfer observations, followed by a deterministic connection of those workload dimensions to the existing BOD utility-operation quote.

## Decision

## Rejected alternatives

- Convert measured CPU/wall time directly into BOD: rejected because infrastructure cost and token price are different quantities.
- Treat successful local transfer as network production evidence: rejected because the socketpair measures a reproducible transfer primitive, not public-network latency/bandwidth.
- Add network fees as mandatory non-zero policy values: rejected because current economic coefficients remain calibration-only.

## Invariants

- Existing quote vectors remain unchanged when new dimensions are zero.
- Negative/boolean workload values are rejected.
- Network bytes in/out are deterministic inputs to the quote.
- Settlement conservation remains exact.
- Durable State Root remains independent of runtime metadata.
