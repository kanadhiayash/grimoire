# Decision Log and Locked Constraints

## Locked decisions

### DEC-001 One canonical repository

Grimoire remains the canonical standards repository.

### DEC-002 Grimoire identity

The repository name is Grimoire.

`Standards Orchestrator` is the functional control-plane capability, not a future repository rename.

### DEC-003 Zeref boundary

Grimoire defines requirements and verifies evidence.

Zeref routes and records execution.

Project repositories own product facts, code, decisions, and evidence.

### DEC-004 Runtime truth

A generated pack does not prove project readiness.

### DEC-005 Status separation

Pack generation, project readiness, release assurance, legal review, and Zeref execution have separate statuses.

### DEC-006 Legal boundary

No automated final legal compliance certification.

### DEC-007 Detailed at rest

Canonical standards can be extensive. Runtime packs are bounded.

### DEC-008 Human and AI parity

Human and AI work receives the same standards and evidence requirements.

### DEC-009 Minimum Correct Change

Implementation uses the smallest complete change without weakening safeguards.

### DEC-010 One mission per PR

No giant rewrite.

### DEC-011 Evidence before merge

Exact-head CI and benchmark evidence are required.

### DEC-012 No self-awarded 10/10

The score is calculated only from the versioned benchmark suite and hard gates.

### DEC-013 Runtime dependency boundary

Default recommendation:

- runtime core remains Python standard-library only;
- CI may use pinned development tools;
- any runtime dependency requires ADR approval.

### DEC-014 Normative classification

Only schema-valid `NORMATIVE` standards can be automatically enforced.

### DEC-015 Hostile input

Manifest, standard imports, source metadata, and receipts are untrusted.

### DEC-016 Compatibility

0.5.x aliases and packs receive one documented migration window.

## Decisions requiring ADR

- schema validation implementation;
- predicate language;
- signing and attestation;
- benchmark storage;
- Zeref receipt trust;
- source verification;
- Windows requirement;
- legal source storage;
- removal date for old CLI aliases.

## Constraints

- private repository;
- no external publication without redaction;
- no Zeref modification without separate approval;
- no legal advice claim;
- no hidden telemetry;
- no secret-bearing artifacts;
- no arbitrary code in applicability predicates;
- no destructive migration without backup and rollback;
- no benchmark fixture changes that hide failures.
