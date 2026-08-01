# Grimoire

Grimoire is a versioned, dependency-free Global Product Engineering Standards Orchestrator
for human and AI product work.

It turns one validated project manifest into a bounded, evidence-aware context
pack. The pack identifies applicable standards, required outcomes, documents,
gates, conflicts, exclusions, verification steps, and Zeref routing metadata.
Grimoire is the product name. “Standards Orchestrator” describes the capability.

## What is operational

Grimoire is an executable control plane, not only a standards directory. Its
Python standard-library runtime can:

- validate untrusted project manifests with deterministic diagnostics;
- resolve standards applicability from versioned registries and predicates;
- compile reproducible 15-file project packs;
- verify pack integrity independently from compiler success;
- explain control decisions without echoing hostile manifest values;
- run evidence-bound benchmark suites and deterministic fuzz gates;
- validate Zeref profiles and receipts while preserving the runtime boundary;
- produce exact-commit release evidence and rehearse rollback without mutation;
- run the dependency-free conformance surface locally and across a supported
  CI matrix.

## Quick start

Requirements:

- Python 3.11, 3.12, or 3.13 for the supported CI contract
- Git
- no runtime package installation

Clone the repository and enter it:

```bash
git clone https://github.com/kanadhiayash/grimoire.git
cd grimoire
```

Inspect the repository:

```bash
python3 scripts/grimoire.py status --json
python3 scripts/grimoire.py catalog --json
```

Run all local checks:

```bash
python3 scripts/grimoire.py check
```

Compile and verify the example project:

```bash
python3 scripts/grimoire.py project boot \
  --manifest templates/project/project.json \
  --output artifacts/example-pack \
  --deterministic \
  --generated-at 2026-01-01T00:00:00+00:00

python3 scripts/grimoire.py project verify \
  --directory artifacts/example-pack \
  --mode offline
```

Run the documented-command smoke:

```bash
python3 scripts/verify_documented_commands.py --json
```

See [Grimoire Quickstart](docs/operations/quickstart.md) for browser packs,
harness adapters, benchmarks, release evidence, and conservative status rules.

## Project manifest

The manifest is JSON so the runtime remains portable and dependency-free. Start
from [templates/project/project.json](templates/project/project.json).

The manifest’s `standards.version` is a standards policy version, not the
repository release version. The current supported policy pin is `0.4.0`.
Unsupported or malformed inputs fail with exit code `2` and safe structured
diagnostics.

## Compiled project pack

`project boot` emits exactly these files:

```text
AI_CONTEXT.md
CONTROL_PACK.json
PROJECT_STATUS.json
EXPECTED_OUTCOMES.md
REQUIRED_DOCUMENTS.md
DOCUMENT_SCHEMAS.json
REQUIRED_GATES.md
ACCEPTANCE_MATRIX.md
VERIFICATION_PLAN.md
SOURCE_MANIFEST.json
ZEREF_EXECUTION_PROFILE.json
CONTROL_TRACE.json
CONFLICT_REPORT.json
EXCLUSIONS.json
EXECUTION_RECEIPT.json
```

`AI_CONTEXT.md` is the bounded one-read contract. The structured files support
verification, traceability, automation, and Zeref routing. Generated packs are
evidence artifacts, not alternate canonical standards.

## Truthful status model

Grimoire keeps generation separate from assurance. The aggregate is
conservative: `BLOCKED` dominates `NOT_VERIFIED`, which dominates `PARTIAL`,
which dominates `PASS`.

Required dimensions:

- `PACK_GENERATION_STATUS`
- `MANIFEST_VALIDATION_STATUS`
- `APPLICABILITY_STATUS`
- `CONTROL_VERIFICATION_STATUS`
- `PROJECT_READINESS_STATUS`
- `RELEASE_ASSURANCE_STATUS`
- `LEGAL_REVIEW_STATUS`
- `ZEREF_EXECUTION_STATUS`

A generated pack may report `pack_generation_status=PASS` while the aggregate
remains `NOT_VERIFIED`. Grimoire never converts missing evidence into readiness,
legal compliance, accessibility compliance, or verified Zeref execution.

## Architecture

```text
Versioned standards and sources
        + project manifest
        + approved project records
                    |
                    v
      validation and applicability
                    |
                    v
        bounded 15-file context pack
                    |
                    v
       Zeref-routed execution boundary
                    |
                    v
         fresh independent evidence
```

Ownership is explicit:

- Grimoire owns standards, applicability, outcomes, documents, gates,
  evidence contracts, and limits.
- Zeref owns activation, model and tool routing, roles, approvals, retries,
  memory, and execution receipts.
- A consuming project owns its facts, decisions, implementation, exceptions,
  deployment state, and evidence.
- Qualified reviewers own final jurisdiction-specific legal conclusions.

## Repository map

| Path | Purpose |
|---|---|
| `src/grimoire/` | Dependency-free validation, registry, compiler, verifier, benchmark, evidence, and Zeref contracts |
| `scripts/` | Unified CLI and operator entrypoints |
| `standards/` | Human-readable normative standards |
| `registry/` | Versioned standard, source, and crosswalk records |
| `policies/` | Machine policy and Draft 2020-12 schemas |
| `profiles/` | Risk and applicability profiles |
| `templates/` | Project, standard, record, evidence, and adapter templates |
| `checks/` | Repository conformance and CI policy checks |
| `tests/` | Unit, compatibility, boundary, and regression tests |
| `benchmarks/` | Executable suites, gold scenarios, scale checks, fuzzing, and pilot evidence |
| `docs/` | Architecture, operations, audits, migrations, and releases |

## Verification surfaces

Local:

```bash
python3 scripts/grimoire.py doctor
python3 scripts/grimoire.py test
python3 scripts/grimoire.py check
git diff --check
```

CI repeats the dependency-free checks and additionally verifies:

- Draft 2020-12 schemas with a fully hashed CI-only dependency lock;
- dependency-free runtime behavior;
- strict manifest acceptance and a deterministic 10,000-case fuzz gate;
- Ubuntu and macOS on Python 3.11, 3.12, and 3.13;
- pinned workflow actions and read-only workflow permissions;
- exact-commit benchmark and release-evidence generation.

Windows remains `NOT_VERIFIED`.

## Zeref boundary

Grimoire can compile and verify Zeref profile and receipt contracts. Zeref
Memory Engine remains a separate continuity and routing runtime. A
self-authenticated receipt or browser simulation is not proof that Zeref
executed. Current repository evidence keeps `ZEREF_EXECUTION_STATUS` at
`NOT_VERIFIED` unless an approved external trust anchor is supplied.

Grimoire does not modify Zeref internals.

## Release evidence

The release-evidence command binds a clean source commit to regular-file
artifacts, a complete benchmark package, environment metadata, approval
records, and a canonical SHA-256 integrity digest. SHA-256 integrity is not an
identity signature. Signing, publication, deployment, and GitHub release
creation remain separate approval-gated actions.

See [Release Evidence and Rollback](docs/operations/release-evidence-and-rollback.md).

## Adoption

A consuming repository should pin a released Grimoire version or reviewed
commit and add:

```text
AGENTS.md
.standards/project.json
docs/standards-exceptions.md
```

Then compile, review, and verify the generated pack before using it as an
execution contract. Do not follow an unversioned branch automatically.

## Compatibility and migration

- Existing 0.5.x CLI entrypoints remain available.
- The deprecated `--engineering-standards-commit` browser-pack alias remains
  tested through the 0.5.x migration window.
- Existing 0.5.x manifests remain supported when they use the active `0.4.0`
  standards policy pin.
- Status consumers must migrate from a single completion field to the
  multidimensional model.

See [Migrating 0.5.x to 1.0](docs/migrations/0.5.x-to-1.0.md).

## Current release state

The checked-in repository version remains `0.5.0` until the approval-gated
1.0.0 release operation is completed. The 1.0 contracts and migration
documentation are release-candidate material. The repository content is written
with public-safe wording, which means external-facing copy was reviewed for
sensitive details. Source use is granted under the MIT License. Repository
visibility and release publication remain separate owner-controlled actions.

## License and contribution

Grimoire is available under the [MIT License](LICENSE). Use the governance and
security files as the source of truth for contributions and responsible use.
Material changes require focused branches, tests, exact-head CI, review, and
evidence-backed completion claims.
