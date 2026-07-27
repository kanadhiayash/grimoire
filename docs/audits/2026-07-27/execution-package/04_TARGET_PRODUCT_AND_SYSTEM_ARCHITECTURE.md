# Target Product and System Architecture

## 1. Architecture outcome

Grimoire 1.0 must be a deterministic standards compiler and verifier, not a checklist generator.

## 2. System context

```text
Authoritative sources
    |
    v
Source registry and freshness service
    |
    v
Normalized standards registry
    |
    +----------------------+
    |                      |
    v                      v
Profiles and overlays   Document schemas
    |                      |
    +----------+-----------+
               |
               v
Project manifest and project records
               |
               v
Strict validation and normalization
               |
               v
Applicability and conflict engine
               |
               v
Bounded pack compiler
               |
               v
Pack verifier
               |
               +----------------------+
               |                      |
               v                      v
Human and AI read              Zeref execution profile
                                      |
                                      v
                              Zeref execution receipt
                                      |
                                      v
                            Evidence and assurance verifier
```

## 3. Required modules

### 3.1 Domain models

Proposed path:

```text
src/grimoire/models/
```

Models:

- ProjectManifest
- ProjectRecordSet
- StandardRecord
- SourceRecord
- ApplicabilityPredicate
- ApplicabilityDecision
- ControlRecord
- EvidenceRecord
- ExceptionRecord
- ConflictRecord
- DocumentRequirement
- GateRecord
- PlanBinding
- ZerefExecutionProfile
- ZerefExecutionReceipt
- AssuranceStatus
- PackReceipt

The runtime may remain standard-library only by using dataclasses, enums, typed dictionaries, and custom validators.

### 3.2 Schema registry

```text
schemas/
  project/
  standards/
  sources/
  controls/
  evidence/
  receipts/
  benchmarks/
  zeref/
```

Requirements:

- schema ID;
- schema version;
- compatibility rules;
- migration path;
- test fixtures;
- invalid fixtures;
- no unresolved references;
- CI validation.

### 3.3 Standard registry

```text
registry/
  standards/
  sources/
  profiles/
  overlays/
  crosswalks/
```

Each standard record should be data-first. Markdown is generated or linked as the human representation.

Example control identity:

```text
STD-SEC-ASVS-V5-0-0-1-2-5
```

### 3.4 Predicate engine

Use a constrained declarative expression model. Do not execute arbitrary Python from standards records.

Recommended operations:

- `equals`
- `not_equals`
- `contains`
- `contains_any`
- `contains_all`
- `exists`
- `is_true`
- `is_false`
- `in`
- `not_in`
- `greater_than_or_equal`
- `stage_at_or_after`
- `risk_at_or_above`
- `all`
- `any`
- `not`

Every evaluation must produce:

- predicate;
- inputs;
- normalized values;
- result;
- reason;
- source standard.

### 3.5 Applicability engine

Inputs:

- validated manifest;
- project decisions;
- active profiles;
- standard registry;
- approved exceptions;
- source freshness;
- target task or lifecycle gate.

Outputs:

- selected controls;
- excluded controls;
- uncertain controls;
- conflicts;
- missing facts;
- counsel questions;
- source status.

### 3.6 Status engine

Status dimensions must be independent.

Recommended model:

```text
Pack generation
Manifest validation
Source freshness
Applicability
Conflict resolution
Document readiness
Control verification
Project readiness
Release assurance
Legal review
Zeref execution
```

Aggregate status is the most severe blocking state, not a majority score.

### 3.7 Safe filesystem layer

Functions:

- resolve path inside allowed root;
- reject path escape;
- reject symlink components;
- create secure temporary directory;
- fsync generated files where supported;
- verify content;
- atomic directory promotion;
- remove temporary output on failure;
- reject unexpected output files;
- never follow user-controlled symlinks.

### 3.8 Context renderer

Manifest content is data.

Requirements:

- length limits;
- control-character filtering;
- quoted blocks;
- explicit `UNTRUSTED PROJECT DATA` labels;
- no raw data in instruction hierarchy;
- safe Markdown rendering;
- no HTML execution;
- deterministic ordering.

### 3.9 Evidence engine

Control evidence states:

- `MISSING`
- `SUBMITTED`
- `INVALID`
- `EXPIRED`
- `PARTIAL`
- `VERIFIED`
- `WAIVED`
- `NOT_APPLICABLE`

A waiver must include:

- approver;
- reason;
- risk;
- expiry;
- affected control;
- compensating control.

### 3.10 Pack verifier

Modes:

- offline;
- connected;
- release.

Offline:

- local schemas;
- hashes;
- source metadata;
- pack consistency.

Connected:

- commit existence;
- source URL reachability;
- freshness;
- revocation or supersession where available.

Release:

- all offline and connected checks;
- plan and approval binding;
- evidence completeness;
- signature;
- attestation;
- no critical unknowns;
- no unresolved release-blocking controls.

## 4. CLI target

```text
grimoire status
grimoire catalog
grimoire doctor
grimoire check
grimoire project validate
grimoire project explain
grimoire project compile
grimoire project verify
grimoire project diff
grimoire controls trace
grimoire controls explain
grimoire sources check
grimoire sources stale
grimoire sources diff
grimoire benchmark run
grimoire benchmark compare
grimoire zeref profile
grimoire zeref verify-receipt
grimoire migrate
```

## 5. File output target

```text
.standards/compiled/
  AI_CONTEXT.md
  CONTROL_PACK.json
  CONTROL_TRACE.json
  EXCLUSIONS.json
  CONFLICT_REPORT.json
  PROJECT_STATUS.json
  EXPECTED_OUTCOMES.md
  REQUIRED_DOCUMENTS.md
  DOCUMENT_SCHEMAS.json
  REQUIRED_GATES.md
  ACCEPTANCE_MATRIX.md
  VERIFICATION_PLAN.md
  SOURCE_MANIFEST.json
  ZEREF_EXECUTION_PROFILE.json
  EXECUTION_RECEIPT.json
```

## 6. Versioning model

### Repository version

Semantic version of Grimoire.

### Schema version

Independent version for each machine contract.

### Standard version

Version per standard or standard family.

### Source version

Official publication or effective version.

### Pack version

Generated artifact format version.

### Project pin

A project must pin:

- Grimoire release or commit;
- schema versions;
- profile versions;
- source review cutoff;
- approved plan revision.

## 7. Runtime dependency decision

Recommended:

- runtime compiler and verifier remain Python standard-library only;
- CI uses pinned development tools for independent verification;
- no dependency is added without an ADR and measured need;
- JSON Schema conformance in CI may use a pinned verifier;
- runtime uses generated typed validators or a deliberately supported subset until a dependency ADR is approved.

## 8. Failure behavior

- invalid manifest: exit 2;
- source conflict: exit 3;
- compiler failure: exit 4;
- verification failure: exit 5;
- security boundary failure: exit 6;
- benchmark regression: exit 7;
- unsupported operation: exit 8;
- unexpected internal exception: exit 70 with sanitized diagnostic and crash receipt.

No failure may leave a partially promoted output directory.
