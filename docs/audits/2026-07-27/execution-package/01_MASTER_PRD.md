# Product Requirements Document: Grimoire 1.0

## Document control

| Field | Value |
|---|---|
| Product | Grimoire |
| Descriptor | Global Product Engineering Standards Orchestrator |
| Current audited release | 0.5.0 |
| Target release | 1.0.0 |
| Primary implementation agent | Codex |
| Execution model | Senior-engineer council roster with bounded per-PR teams |
| Runtime partner | Zeref |
| Status | Approved for implementation planning |
| Evidence date | July 27, 2026 |

## 1. Executive summary

Grimoire is intended to be one canonical repository that converts product facts into a bounded, traceable, human-readable and machine-readable standards pack. The pack should identify the standards, obligations, documents, controls, tests, evidence, gates, exceptions, and Zeref execution profile relevant to a specific project.

The audited 0.5.0 release has a strong repository foundation, instruction system, packaging surface, and operating vocabulary. It does not yet perform the core orchestration claim. The current compiler mostly reacts to lifecycle stage and a few booleans. It does not resolve real standards, does not prove project readiness, and can return `PASS` while every acceptance item is `NOT_VERIFIED`.

Grimoire 1.0 must close the gap between declared standards and actual enforcement.

## 2. Problem statement

Human and AI product teams commonly suffer from six failures:

1. Standards are scattered across repositories, documents, prompts, and memory.
2. AI receives too much context or the wrong context.
3. Requirements are expressed as prose without executable controls.
4. Projects are marked complete without current evidence.
5. Legal, accessibility, security, privacy, and AI rules are applied inconsistently.
6. Agent operations cannot prove which instruction, standard, source, plan revision, or approval governed an action.

Grimoire must solve these failures without becoming a giant context dump or an unreviewable automated compliance oracle.

## 3. Product vision

Grimoire should provide one command that:

1. validates a project manifest and all referenced project records;
2. determines applicable product, design, engineering, security, privacy, legal, accessibility, AI, stack, platform, and risk controls;
3. explains why every control was selected or excluded;
4. compiles one bounded context pack;
5. emits required documents and exact document schemas;
6. identifies missing facts, conflicts, expired sources, exceptions, and counsel-review requirements;
7. prepares a Zeref execution profile tied to an approved plan revision;
8. verifies evidence and calculates assurance status without false `PASS` results;
9. creates a signed, reproducible receipt;
10. supports human inspection, machine enforcement, and historical audit.

## 4. Product principles

### 4.1 Evidence before status

A successful compilation is not proof that a project is ready, compliant, secure, accessible, or releasable.

### 4.2 Detailed at rest, selective during execution

The canonical repository may be extensive. Generated packs must include only the controls needed for the declared project and active task.

### 4.3 Human and AI parity

Human-authored and AI-authored changes receive the same controls, tests, review, evidence, and approval requirements.

### 4.4 Minimum Correct Change

Implementation must prefer the smallest complete change that satisfies the approved requirements without weakening safeguards.

### 4.5 Source authority is explicit

Binding law, regulation, regulator guidance, consensus standards, industry frameworks, best practices, trends, proposals, drafts, and superseded sources are separate classes.

### 4.6 No automated legal certification

Grimoire may identify applicability, evidence, gaps, and escalation requirements. It must not issue final legal advice or a universal compliance certification.

### 4.7 One canonical truth

Generated packs are immutable artifacts, not alternate sources of standards.

### 4.8 Honest runtime boundaries

Grimoire defines controls. Zeref routes and records execution. Project repositories own product facts, plans, code, and evidence.

## 5. Primary users

### 5.1 Human product and engineering teams

Need clear standards, document requirements, acceptance gates, and evidence expectations.

### 5.2 AI coding and design agents

Need one bounded pack with machine-readable controls and explicit stop conditions.

### 5.3 Zeref

Needs a versioned execution profile with plan binding, model and tool constraints, approval gates, cost ceilings, and receipt requirements.

### 5.4 Reviewers and auditors

Need traceability from source to standard to control to implementation to test to evidence to final status.

### 5.5 Maintainers

Need safe versioning, compatibility, source freshness, benchmark regression detection, and release governance.

## 6. Non-goals

Grimoire 1.0 will not:

- replace qualified legal counsel;
- execute production deployments by itself;
- own Zeref memory or routing internals;
- load the full standards corpus for every operation;
- claim every jurisdiction and industry is covered;
- infer undisclosed product facts;
- make autonomous external changes without approval;
- optimize for the smallest line count at the expense of correctness;
- treat a benchmark aggregate as proof that every control passes.

## 7. Core capabilities

### 7.1 Strict project manifest validation

The compiler must validate the complete manifest against Draft 2020-12 schemas or an explicitly documented equivalent.

Requirements:

- reject wrong types;
- reject unknown properties where the schema says they are not allowed;
- enforce lengths and collection limits;
- normalize enums;
- reject unsupported standards versions;
- return stable machine-readable errors;
- never crash on malformed input;
- treat all manifest text as untrusted data;
- report every validation issue in one pass where safe.

### 7.2 Standards registry

Every normative standard must have:

- stable ID;
- version;
- status;
- domain;
- requirement level;
- applicability predicate;
- non-applicability predicate;
- source records;
- expected outcomes;
- required actions;
- required documents;
- document schemas;
- acceptance criteria;
- verification methods;
- evidence requirements;
- failure conditions;
- exceptions;
- owner;
- review date;
- Zeref behavior;
- machine-readable representation.

### 7.3 Applicability engine

The engine must resolve controls using:

- lifecycle stage;
- product type;
- user types;
- target markets;
- company and processing locations;
- platforms;
- languages;
- frameworks;
- services;
- cloud providers;
- data categories;
- sensitive data;
- age groups;
- AI capabilities;
- automated decisions;
- external models;
- industry;
- public or private sector;
- risk level;
- approved exceptions.

Every selected control must include a reason. Every excluded high-risk control must include a reason.

### 7.4 Conflict engine

Detect conflicts among:

- applicable law and regulation;
- platform requirements;
- repository contract;
- approved plan;
- project facts;
- project decisions;
- exceptions;
- stack overlays;
- personal instructions;
- generated controls.

Same-level conflicts must return `BLOCKED` or `COUNSEL_REVIEW_REQUIRED`, not silent resolution.

### 7.5 Safe atomic compiler

The compiler must:

- reject symlinked output paths and symlinked target files;
- compile into a new temporary directory;
- fail closed on unexpected output content;
- validate every output before promotion;
- atomically replace the final directory;
- support deterministic mode;
- preserve a full source manifest;
- produce hashes for every artifact;
- support signed attestations in release mode;
- never include stale unrelated files.

### 7.6 Bounded context pack

Required artifacts:

- `AI_CONTEXT.md`
- `CONTROL_PACK.json`
- `PROJECT_STATUS.json`
- `EXPECTED_OUTCOMES.md`
- `REQUIRED_DOCUMENTS.md`
- `DOCUMENT_SCHEMAS.json`
- `REQUIRED_GATES.md`
- `ACCEPTANCE_MATRIX.md`
- `VERIFICATION_PLAN.md`
- `SOURCE_MANIFEST.json`
- `ZEREF_EXECUTION_PROFILE.json`
- `EXECUTION_RECEIPT.json`
- `CONTROL_TRACE.json`
- `CONFLICT_REPORT.json`
- `EXCLUSIONS.json`

The one-read `AI_CONTEXT.md` must summarize the pack without introducing untrusted manifest text as executable instructions.

### 7.7 Pack verifier

A separate verifier must check:

- schema validity;
- source versions;
- source commit existence when network verification is enabled;
- freshness;
- file hashes;
- unexpected files;
- receipt consistency;
- control trace completeness;
- standard version compatibility;
- plan revision binding;
- approval status;
- acceptance evidence;
- future timestamps;
- replay or substitution;
- forbidden compliance claims;
- Zeref receipt linkage.

### 7.8 Status model

Separate status dimensions:

- `PACK_GENERATION_STATUS`
- `MANIFEST_VALIDATION_STATUS`
- `APPLICABILITY_STATUS`
- `CONTROL_VERIFICATION_STATUS`
- `PROJECT_READINESS_STATUS`
- `RELEASE_ASSURANCE_STATUS`
- `LEGAL_REVIEW_STATUS`
- `ZEREF_EXECUTION_STATUS`

Rules:

- generated pack success may be `PASS`;
- missing evidence must keep control and project assurance `NOT_VERIFIED`;
- unresolved critical unknowns must produce `BLOCKED`;
- automated legal status may never be `COMPLIANT`;
- project readiness may be `PASS` only when all release-blocking controls have current evidence;
- aggregate status must never hide a failed hard gate.

### 7.9 Evidence engine

Each control must link to:

- evidence type;
- evidence location;
- evidence timestamp;
- subject commit or build;
- command or method;
- result;
- reviewer;
- expiry;
- environment;
- confidence;
- exceptions.

### 7.10 Standards normalization

All normative standards must conform to the standard-authoring schema before entering compiled packs.

Legacy documents must be classified as:

- `NORMATIVE`
- `LEGACY_NORMATIVE`
- `GUIDANCE`
- `TEMPLATE`
- `EXAMPLE`
- `DRAFT`
- `SUPERSEDED`

Only valid `NORMATIVE` controls may be enforced automatically.

### 7.11 Benchmark runner

Grimoire must include an executable benchmark command:

```bash
python3 scripts/grimoire.py benchmark run \
  --suite all \
  --output artifacts/benchmarks
```

The runner must produce machine and human reports, historical comparisons, regressions, and reproducibility metadata.

### 7.12 Zeref integration

Grimoire must emit a profile that Zeref can consume and a contract that Zeref must return.

The round trip must prove:

```text
Grimoire pack
-> Zeref execution
-> project changes and evidence
-> Zeref receipt
-> Grimoire verification
-> final status
```

## 8. Functional requirements

### FR-001 Manifest validation

Malformed input must return controlled errors and exit code 2.

### FR-002 No uncaught fuzz failures

At least 10,000 generated manifest mutations must produce zero unhandled exceptions.

### FR-003 Actual standard resolution

Every compiled control must reference a valid standard ID and standard version.

### FR-004 Traceable selection

Every selected and excluded control must record a predicate result and reason.

### FR-005 No false assurance

A project with unverified acceptance items must not receive project readiness `PASS`.

### FR-006 Safe output

The compiler must reject symlinks, dirty directories, path escapes, duplicate IDs, and unexpected artifacts.

### FR-007 Deterministic mode

Given identical inputs, pinned sources, and deterministic timestamp mode, artifact bytes and hashes must be identical.

### FR-008 Source authenticity

Online verification must confirm repository commit existence. Offline mode must state `SOURCE_AUTHENTICITY_NOT_VERIFIED`.

### FR-009 Freshness correctness

Future generation timestamps and future source review dates must fail.

### FR-010 Policy schema conformance

Every machine policy must validate against its declared schema in CI.

### FR-011 Self-conforming standards

One hundred percent of enforced standards must follow the normative authoring contract.

### FR-012 Security control mapping

Applicable web controls must support versioned OWASP ASVS mappings. Applicable mobile controls must support MASVS mappings. AI systems must support AISVS mappings. Software lifecycle controls must support NIST SSDF mappings.

### FR-013 Accessibility mapping

Applicable web controls must map to WCAG 2.2 success criteria and conformance levels.

### FR-014 Supply-chain evidence

Release mode must support SBOM, provenance, pinned dependencies, workflow hardening, and artifact attestations.

### FR-015 Benchmark evidence

No benchmark score may be published without fixtures, expected results, tool versions, commit SHA, repeated runs where relevant, and raw outputs.

### FR-016 Compatibility

Existing 0.5.x packs and CLI aliases must remain verifiable through one documented migration window.

### FR-017 Zeref plan binding

Zeref execution must fail verification if the returned receipt is not bound to the same plan ID, revision, pack hash, and project commit.

### FR-018 Cost evidence

Grimoire must report compiler time, pack size, selected control count, source count, model-token budget where applicable, and Zeref execution cost where provided.

## 9. Non-functional requirements

### Reliability

- zero uncaught exceptions in the approved fuzz suite;
- atomic writes;
- idempotent compilation;
- deterministic mode;
- stable exit codes;
- rollback documentation.

### Performance

Initial 1.0 targets:

- median compile time under 100 ms for 1,000 registered controls;
- 95th percentile under 250 ms for 10,000 controls;
- one-read context under the configured token budget;
- verifier under 500 ms for local packs excluding external network checks.

### Security

- no symlink traversal;
- no path escape;
- no prompt injection from manifest content;
- no unpinned executable CI dependencies;
- least-privilege workflow permissions;
- no silent trust of external commits;
- secure temporary files;
- sanitized error output;
- no credentials in generated packs.

### Portability

- runtime core supports Python 3.11, 3.12, and 3.13;
- Linux and macOS are required;
- Windows support is either verified or explicitly marked unsupported;
- runtime core remains Python standard-library only unless an ADR changes the contract;
- CI may use pinned development tools.

### Maintainability

- typed internal models;
- stable schema versions;
- migration utilities;
- domain ownership;
- no duplicate source registries;
- no hidden command registry;
- architecture decisions for material changes.

### Observability

- structured logs;
- stable event IDs;
- execution duration;
- control counts;
- failure class;
- source freshness;
- verifier outcomes;
- benchmark regressions.

## 10. User stories

### US-001 Product team

As a product team, I can declare my product facts once and receive only the standards, documents, and gates applicable to my product.

### US-002 Coding agent

As a coding agent, I receive a bounded context pack with clear scope, stop conditions, and acceptance criteria.

### US-003 Reviewer

As a reviewer, I can trace every enforced control back to an authoritative source and forward to implementation evidence.

### US-004 Maintainer

As a maintainer, I can update a standard version without silently changing existing project packs.

### US-005 Zeref

As Zeref, I can execute a plan-bound profile and return a receipt that Grimoire can verify.

### US-006 Legal reviewer

As a legal reviewer, I can see potentially applicable obligations, missing facts, source versions, and questions requiring qualified judgment.

### US-007 Accessibility reviewer

As an accessibility reviewer, I can see exact WCAG criteria, required manual tests, automated evidence, and unresolved barriers.

### US-008 Security reviewer

As a security reviewer, I can see ASVS, MASVS, AISVS, SSDF, and supply-chain mappings appropriate to the project.

## 11. Success metrics

### Hard gates

- false project `PASS`: 0
- uncaught manifest fuzz exceptions: 0
- enforced standards without valid IDs: 0
- enforced standards without source provenance: 0
- critical control selection recall: 100%
- critical false non-applicability: 0
- unresolved critical conflicts silently resolved: 0
- unverified release marked ready: 0
- future timestamps accepted: 0
- symlink overwrite success: 0
- prompt instructions sourced from untrusted manifest fields: 0

### Quality targets

- all category scores at or above 9.5/10;
- overall weighted score at or above 9.7/10;
- 100% normative self-conformance;
- 90% or greater meaningful line and branch coverage in compiler, verifier, applicability, status, and policy validation modules;
- mutation score at or above 85% for critical modules;
- no critical or high security findings;
- benchmark variance documented and within approved thresholds;
- zero undocumented compatibility breaks.

## 12. Dependencies

- current Grimoire repository and history;
- official source records;
- approved JSON schemas;
- benchmark fixtures;
- Zeref execution receipt contract;
- GitHub Actions;
- optional pinned CI tools;
- qualified legal review for jurisdiction-specific mappings.

## 13. Open decisions requiring ADRs

1. Runtime schema validation strategy while preserving a dependency-free core.
2. Internal rule expression language for applicability predicates.
3. Signature and attestation format.
4. Storage format for benchmark history.
5. Zeref receipt transport and trust model.
6. Online source verification policy.
7. Compatibility duration for 0.5.x packs.
8. Whether Windows is a 1.0 release requirement.
9. Whether legal source records include full text, extracts, or metadata and links only.
10. Whether `scripts/standards.py` is removed in 1.0 or retained as an alias.

## 14. Final product acceptance

Grimoire 1.0 is accepted only when all requirements in `12_ACCEPTANCE_CRITERIA_AND_RELEASE_GATES.md` pass on the release commit and the result is independently reproduced from a clean environment.
