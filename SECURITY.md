# Security Policy

## Scope and status

BOD v0.1 is experimental and is not represented as production-secure. The repository includes verification code and experimental chain integration; neither is a substitute for an independent security review.

## Reporting a concern

Do not publish secrets, private keys, credentials, or exploit material in public issues. For a suspected vulnerability, open a minimal issue describing the affected component, impact, and a reproducible non-sensitive test case. If the issue requires private disclosure, contact the maintainer through a verified GitHub profile channel before sharing details.

Do not send secrets or private credentials to maintainers.

## Useful report contents

- affected commit or release;
- relevant file, function, or protocol rule;
- prerequisites and reproduction steps;
- expected versus observed behavior;
- impact and possible mitigations;
- whether the issue affects integrity, lineage, availability, authorization, or economic accounting.

## Trust boundaries

- A digest proves byte identity relative to the digest, not semantic truth.
- Valid integrity does not imply that evidence is available.
- A valid envelope does not establish that a transition is accepted or canonical.
- An external chain anchor does not certify the semantic correctness of a BOD claim.
- Testnet success is not production security evidence.

Please avoid posting live credentials, user data, or sensitive operational details. Security and economic findings should be documented with minimal, reproducible evidence.
