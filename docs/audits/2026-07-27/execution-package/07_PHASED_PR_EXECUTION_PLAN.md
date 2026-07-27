# Phased Pull-Request Execution Plan

## Program rule

Do not attempt a giant 1.0 rewrite.

Each PR must be independently testable and preserve compatibility unless its approved purpose is a versioned migration.

## Phase 0: Baseline and truth freeze

### PR 0.1: Audit evidence import

Objective:

- add the audit findings, failing fixtures, scorecard, and benchmark baseline to the repository.

Required outputs:

- `docs/audits/2026-07-27/`;
- current scores;
- exact failing fixtures;
- baseline benchmark result;
- no behavior change.

Gate:

- audit findings reproducible.

## Phase 1: Status truth and strict validation

### PR 1.1: Multidimensional status model

Fix:

- project `PASS` with unverified acceptance.

Add:

- separate status enums;
- aggregate severity rules;
- regression tests;
- migration notes.

Hard acceptance:

- no evidence means project readiness `NOT_VERIFIED`.

### PR 1.2: Correct AI Operations schema

Fix:

- command and autonomy schema contradictions.

Add:

- independent schema validation in CI;
- valid and invalid fixtures.

### PR 1.3: Strict manifest models

Add:

- typed manifest model;
- complete nested validation;
- structured error output;
- unknown-property policy;
- supported version checks.

Gate:

- current 500-case fuzz failures converted into controlled results.

### PR 1.4: 10,000-case fuzz suite

Add:

- deterministic seed;
- property tests;
- crash corpus;
- CI fast subset;
- scheduled full run.

Gate:

- zero unhandled exceptions.

## Phase 2: Safe compiler and verifier

### PR 2.1: Safe filesystem layer

Fix:

- symlink overwrite;
- path escape;
- dirty output;
- partial writes.

Gate:

- adversarial filesystem suite passes.

### PR 2.2: Untrusted-data context rendering

Fix:

- manifest prompt injection.

Add:

- trust labels;
- length limits;
- safe quoting;
- control-character policy.

Gate:

- injected instructions remain inert data.

### PR 2.3: Atomic deterministic compiler

Add:

- temporary build directory;
- deterministic mode;
- atomic promotion;
- unexpected-file checks;
- stable ordering.

Gate:

- repeated deterministic compiles are byte-identical.

### PR 2.4: Project pack verifier

Add:

- schema, hash, timestamp, file-set, and receipt checks;
- offline, connected, and release modes.

Gate:

- future timestamp and fake commit cases fail correctly.

## Phase 3: Real standards resolution

### PR 3.1: Standard record schema and registry

Add:

- machine-first normative record;
- unique IDs;
- versions;
- source links;
- applicability predicates;
- human Markdown link.

Gate:

- registry validates and duplicate IDs fail.

### PR 3.2: Declarative predicate engine

Add:

- constrained operations;
- evaluation trace;
- no arbitrary code execution.

Gate:

- property and mutation tests.

### PR 3.3: Applicability resolver

Add:

- profile and overlay resolution;
- selected, excluded, uncertain, and conflicted controls;
- reasons.

Gate:

- first five gold scenarios pass.

### PR 3.4: Control trace and exclusions

Add:

- `CONTROL_TRACE.json`;
- `EXCLUSIONS.json`;
- `CONFLICT_REPORT.json`;
- CLI explain commands.

Gate:

- every compiled control is traceable.

## Phase 4: Normalize the standards corpus

### PR 4.1: Content classification

Classify all documents:

- normative;
- legacy normative;
- guidance;
- template;
- example;
- draft;
- superseded.

Gate:

- only valid normative records can compile.

### PR 4.2 through 4.N: Domain migration

Migrate in separate PRs:

1. universal governance;
2. product and UX;
3. accessibility;
4. design systems;
5. architecture;
6. frontend;
7. APIs;
8. backend and data;
9. security;
10. AI and agents;
11. cloud and cost;
12. Git and release;
13. legal and privacy.

Gate for each domain:

- 100% authoring-schema compliance;
- source provenance;
- tests;
- benchmark fixture updates.

## Phase 5: Authoritative crosswalks

### PR 5.1: NIST SSDF crosswalk

Add versioned practice and task mappings.

### PR 5.2: OWASP ASVS 5.0.0 crosswalk

Use versioned requirement IDs.

### PR 5.3: OWASP MASVS crosswalk

Activate for mobile product profiles.

### PR 5.4: OWASP AISVS 1.0 crosswalk

Activate for AI-enabled systems.

### PR 5.5: WCAG 2.2 crosswalk

Include criterion IDs, levels, automated/manual evidence classes.

### PR 5.6: SLSA and OpenSSF controls

Add release and supply-chain evidence requirements.

Gate:

- official source records;
- source version;
- license review;
- mapping tests.

## Phase 6: Benchmark system

### PR 6.1: Benchmark runner

Add:

- run;
- compare;
- historical result format;
- regression thresholds.

### PR 6.2: Gold scenarios

Implement at least 15 product scenarios.

### PR 6.3: Security adversarial suite

Implement trust-boundary and source-substitution cases.

### PR 6.4: Performance and scale

Implement 100, 1,000, 10,000, and 50,000-control datasets.

Gate:

- no self-awarded target score;
- raw outputs retained.

## Phase 7: Zeref round trip

### PR 7.1: Zeref profile v2

Include:

- pack hash;
- plan ID;
- revision;
- project commit;
- required controls;
- tool and approval limits;
- cost ceiling;
- expected receipt schema.

### PR 7.2: Zeref receipt verifier

Reject:

- mismatched plan;
- mismatched pack;
- missing evidence;
- unauthorized external action;
- invalid memory promotion;
- expired receipt.

### PR 7.3: End-to-end pilot

Run one real project:

```text
project manifest
-> Grimoire pack
-> Zeref execution
-> evidence
-> receipt
-> Grimoire verification
```

Gate:

- independent reviewer reproduces the result.

## Phase 8: CI, security, and release hardening

### PR 8.1: CI matrix

Python:

- 3.11;
- 3.12;
- 3.13.

Platforms:

- Ubuntu;
- macOS;
- Windows or explicit deferral ADR.

### PR 8.2: Security toolchain

Add pinned:

- schema validation;
- actionlint;
- secret scan;
- static analysis;
- SBOM;
- OpenSSF Scorecard where applicable.

### PR 8.3: Provenance and release evidence

Add:

- artifact attestations;
- SLSA-aligned provenance;
- signed release manifest;
- rollback.

## Phase 9: 1.0 release candidate

### PR 9.1: Documentation and migration

Update:

- README;
- AGENTS;
- quickstart;
- adoption;
- API and CLI docs;
- migration from 0.5.x;
- deprecations.

### PR 9.2: Release candidate benchmark

Run full suite three times from clean environments.

### PR 9.3: Independent audit fixes

No new features.

### PR 9.4: 1.0.0 release

Requires explicit approval after all hard gates pass.
