# Product Engineering Standards & Operations

Private, neutral, versioned standards and an executable control plane for human and AI product work. The repository will later be renamed **Standards Orchestrator**.

It covers product strategy, research, UX, UI, accessibility, design systems, architecture, frontend, APIs, backend, data, AI and agents, security, privacy, legal applicability, cloud, cost, Git, delivery, release, and operations.

## Core idea

**Detailed at rest, selective during execution.**

The repository may be extensive. A human or AI does not load the full corpus for every task. One project manifest is compiled into one bounded context pack containing only the applicable standards, expected outcomes, documents, gates, evidence, limits, and Zeref execution metadata.

```text
Standards -> policies and profiles -> project manifest -> compiled pack -> Zeref execution -> verification
```

## Start here

### Human operator

```bash
python3 scripts/standards.py status
python3 scripts/standards.py check
```

### AI agent

1. Read `AGENTS.md`.
2. Read `REPOSITORY_INDEX.json`.
3. Read the project manifest and compiled `AI_CONTEXT.md` when operating in a consuming project.
4. Use the smallest relevant source set.

### Compile a project pack

```bash
python3 scripts/standards.py project boot   --manifest templates/project/project.json   --output /tmp/example-standards-pack
```

The compiler emits:

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
EXECUTION_RECEIPT.json
```

`AI_CONTEXT.md` is the one-read human and AI contract. Structured files support Zeref, checks, automation, and evidence.

## Ownership model

### Standards Orchestrator

Defines applicable requirements, expected outcomes, required documents and headings, gates, acceptance criteria, verification, evidence, limits, profiles, and overlays.

### Zeref

Routes execution through roles, models, tools, skills, approvals, retries, memory, cost limits, and receipts. Zeref remains a separate runtime.

### Project repository

Owns actual product facts, local instructions, project manifest, assumptions, decisions, risks, plan revisions, designs, code, tests, exceptions, deployment state, and evidence.

## Implementation stack

| Concern | Technology | Reason |
|---|---|---|
| Orchestration | Python 3.11+ standard library | Portable and dependency-free |
| Machine contracts | JSON and JSON Schema draft 2020-12 | Deterministic and language-neutral |
| Human and AI guidance | Markdown | Reviewable and portable |
| Shell | Bash or Zsh | Thin launchers only |
| CI | GitHub Actions YAML | Native verification |

The project manifest is JSON. YAML is not used because adding a parser dependency would violate the current portability contract.

## Repository map

| Path | Purpose |
|---|---|
| `standards/` | Human-readable product, design, engineering, legal, AI, and operational rules |
| `policies/` | Machine-readable policy and schemas |
| `profiles/` | Risk and applicability profiles |
| `adapters/` | Harness and browser-surface adapters |
| `templates/` | Standards, product, design, engineering, governance, and evidence templates |
| `instructions/global/` | Neutral additive instruction modules for any user or team |
| `instructions/personal/` | Optional private overlays excluded from neutral packs |
| `sources/` | Source authority and freshness records |
| `checks/` | Dependency-free conformance checks |
| `scripts/` | Unified CLI, compilers, verifiers, and installers |
| `tests/` | Unit, boundary, adversarial, and compatibility tests |
| `benchmarks/` | Scenario and efficiency benchmark specifications |
| `docs/` | Architecture decisions, operations, releases, and migrations |

## Core guarantees

A conforming operation must:

- Read context before editing
- Separate facts, assumptions, unknowns, risks, and conflicts
- Load only applicable standards
- Define expected outcomes and required documents
- Bind execution to an approved plan revision
- Use Minimum Correct Change during implementation
- Preserve tests, security, privacy, accessibility, legal, data, and review controls
- Never invent evidence or runtime capability
- Verify before claiming completion
- Require explicit approval for external or destructive actions
- Keep neutral standards separate from personal overlays
- Report legal applicability without issuing automated compliance certification

## Standard structure

Every normative standard defines purpose, expected outcome, applicability, non-applicability, inputs, unknowns, actions, decisions, details, documents, document structure, acceptance, verification, evidence, failure conditions, risks, guards, exceptions, costs, dependencies, related standards, sources, ownership, Zeref behavior, examples, and anti-patterns.

## Naming and placement

Stable records use `ADR`, `DEC`, `ASM`, `RSK`, `RES`, `EXP`, `INC`, and `PM-INC` identifiers. Mutable priority, status, and owner values do not belong in filenames. Source code follows official language and framework overlays. Figma token names use nested semantic groups such as `color/semantic/text/primary`, not dotted names.

## Neutral and personal instructions

`instructions/global/` is reusable by any human, team, or AI. `instructions/personal/yash/` is a private optional overlay and is excluded from neutral packs. Personal preferences may customize tone and workflow but cannot weaken neutral safeguards.

## Legal and compliance boundary

The system classifies source authority, identifies potentially applicable controls, detects missing facts, prepares evidence and documents, and escalates to qualified review. It never claims universal legal compliance. The legal source registry is explicitly versioned and not represented as exhaustive.

## Existing capabilities retained

Version 0.4.0 retains the 0.3.0 AI Operations control plane, cross-surface Zeref activation, browser source packs, harness adapters, repository index, and unified CLI. It adds the Standards Orchestrator without modifying Zeref Memory Engine.

## Verification

```bash
make check
```

Expected top-level checks include repository health, surface activation, repository index, Standards Orchestrator, unit tests, and Python compilation.

## Adoption

A consuming repository pins a released version and adds:

```text
AGENTS.md
.standards/project.json
docs/standards-exceptions.md
```

Generated packs are artifacts, not alternate canonical standards. They must record version, source status, integrity, and freshness.

## Status

Version `0.4.0` establishes the Standards Orchestrator foundation, one-call project compiler, structured standard and document contracts, neutral instructions, private Yash overlay, legal source governance, Minimum Correct Change, Zeref execution profiles, checks, templates, and benchmarks.

Private internal policy. Do not publish repository content without explicit review and redaction.
