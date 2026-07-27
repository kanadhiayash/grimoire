# Definition of Done for Grimoire 1.0

Grimoire 1.0 is done only when all sections below are proven on the release commit.

## Product

- product vision and non-goals are internally consistent;
- repository identity is consistent;
- human and AI entrypoints are accurate;
- Standards Orchestrator and Zeref boundaries are explicit;
- no stale temporary naming remains.

## Validation

- complete manifest schema;
- strict nested types;
- stable error model;
- unsupported versions rejected;
- 10,000-case fuzz suite with zero unhandled exceptions.

## Compiler

- actual standards registry;
- deterministic predicates;
- selected controls;
- excluded controls;
- uncertain controls;
- conflicts;
- source provenance;
- document requirements;
- bounded context;
- atomic output;
- no symlink or path escape.

## Verification

- separate pack verifier;
- hashes;
- file-set verification;
- freshness;
- source authenticity modes;
- future timestamp rejection;
- plan and commit binding;
- evidence expiry;
- signed release receipt.

## Status

- no false project `PASS`;
- no false release `PASS`;
- no automated legal `COMPLIANT`;
- aggregate status cannot hide hard-gate failure.

## Standards

- 100% enforced standards conform to the normative schema;
- every enforced standard has sources;
- legacy content is classified;
- duplicate IDs fail;
- superseded sources do not compile.

## Security

- NIST SSDF mapping;
- ASVS mapping;
- MASVS mapping;
- AISVS mapping;
- threat model;
- adversarial suite;
- no critical or high finding;
- SBOM;
- provenance;
- pinned CI.

## Accessibility

- WCAG 2.2 mapping;
- criterion-level trace;
- automated and manual evidence;
- no false conformance claim.

## Legal and privacy

- source authority classes;
- source freshness;
- applicability and escalation;
- privacy documents and controls;
- counsel-review path;
- no legal certification.

## AI and Zeref

- AI RMF and GenAI mappings;
- agent permission controls;
- prompt injection protection;
- Zeref profile v2;
- Zeref receipt verifier;
- one real end-to-end pilot;
- memory boundary verified.

## Benchmarks

- executable runner;
- 15 or more gold scenarios;
- fuzz;
- security;
- performance;
- compatibility;
- reproducible evidence;
- historical comparison;
- all hard gates pass;
- every domain at least 9.5;
- weighted score at least 9.7.

## Compatibility

- 0.5.x migration documented;
- deprecated aliases tested;
- old packs either verify or fail with precise migration instructions.

## CI

- Python 3.11, 3.12, and 3.13;
- supported OS matrix;
- schema validation;
- unit, integration, fuzz, security, compatibility, and benchmark gates;
- exact-head evidence;
- release artifacts retained.

## Documentation

- README;
- AGENTS;
- quickstart;
- CLI reference;
- schema reference;
- standards authoring guide;
- source guide;
- benchmark guide;
- Zeref integration guide;
- migration guide;
- release notes;
- rollback.

## Final approval

Before release:

```text
Concept score: >= 9.5
Enforcement score: >= 9.5
Weighted score: >= 9.7
Hard gates: all PASS
Critical findings: 0
High findings: 0
Independent reproduction: PASS
Human approval: REQUIRED
```

Until all evidence is fresh, the release status is:

```text
NOT_VERIFIED
```
