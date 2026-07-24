# Engineering Standards

Private, versioned engineering policy and an executable control plane for human and AI-assisted product development.

This repository is the canonical source for project structure, architecture, GitHub operations, security, testing, release readiness, product and UX quality, AI-agent execution rules, and cross-surface Zeref activation used by Yash Kanadhia.

## Start here

### Human operator

```bash
python3 scripts/standards.py status
python3 scripts/standards.py check
```

Then read the [Quickstart](docs/operations/quickstart.md).

### AI agent

1. Read [`AGENTS.md`](AGENTS.md).
2. Read [`REPOSITORY_INDEX.json`](REPOSITORY_INDEX.json).
3. Run:

```bash
python3 scripts/standards.py status --json
```

4. Route the task using the [AI Agent Entrypoint](docs/operations/agent-entrypoint.md).

The index is navigation metadata, not an alternate policy source. Canonical policy remains in the files named by the index.

## Why this exists

Written principles are useful, but they are not enforcement. This repository converts reusable engineering guidance into five layers:

1. Human-readable standards
2. Machine-readable policies and profiles
3. Harness and browser-surface adapters
4. Compiled project contracts and source packs
5. Local and CI conformance checks

```text
Standards -> Policies -> Adapters -> Project contracts or source packs -> Verification
```

## Implementation stack

The control plane uses a deliberately small stack:

| Concern | Technology | Reason |
|---|---|---|
| Executable orchestration | Python 3.11+ standard library | Portable, readable, testable, no runtime dependency graph |
| Machine contracts | JSON and JSON Schema | Deterministic, language-neutral, easy for agents and CI to inspect |
| Human and agent guidance | Markdown | Reviewable, portable, diff-friendly |
| Shell automation | Bash or Zsh | Thin launchers only |
| CI | GitHub Actions YAML | Native repository verification |

TypeScript, Go, Rust, databases, and web frameworks are not default choices. Add them only when measured requirements exceed this stack.

## Core guarantees

A conforming project must:

- Read project context before editing
- Separate facts, assumptions, unknowns, risks, and conflicts when material
- Make the smallest complete change
- Preserve tests, security controls, accessibility, and existing quality gates
- Never invent repository state, metrics, citations, runtime capability, or verification results
- Verify behavior before claiming success
- Record architecture-impacting decisions
- Tie public claims to reproducible evidence
- Apply the same review standard to human and AI-generated changes
- Bind approval to a named plan and revision
- Keep external actions and canonical memory writes human-gated unless narrowly pre-approved
- Report assurance and activation methods honestly
- Label browser Zeref simulation separately from verified local runtime

## Repository map

The authoritative machine map is [`REPOSITORY_INDEX.json`](REPOSITORY_INDEX.json).

| Path | Purpose |
|---|---|
| `standards/` | Human-readable rules and rationale |
| `policies/` | Machine-readable baseline, AI operations, surface activation, and schemas |
| `profiles/` | Risk-based enforcement profiles |
| `adapters/` | Compact instructions for coding harnesses and browser project surfaces |
| `templates/` | Governance, operations, browser source-pack, and delivery templates |
| `checks/` | Dependency-free conformance checkers |
| `scripts/` | Unified CLI, doctor, tests, compiler, verifier, and installer |
| `tests/` | Conformance and adversarial behavior tests |
| `docs/` | Architecture decisions, capability matrices, contracts, guides, and migration records |

## Unified CLI

Repository health:

```bash
python3 scripts/standards.py status --json
```

Machine catalog:

```bash
python3 scripts/standards.py catalog --json
```

Full verification:

```bash
python3 scripts/standards.py check
```

Write a machine report:

```bash
python3 scripts/standards.py check \
  --json-output artifacts/standards-check.json
```

Browser pack compilation:

```bash
python3 scripts/standards.py pack compile \
  --surface chatgpt-project \
  --project-name "Example Project" \
  --output ./dist/example-project \
  --engineering-standards-commit <40-character-sha> \
  --zeref-commit <40-character-sha>
```

Browser pack verification:

```bash
python3 scripts/standards.py pack verify ./dist/example-project
```

Local harness adapter management:

```bash
python3 scripts/standards.py harness detect
python3 scripts/standards.py harness plan
python3 scripts/standards.py harness apply
python3 scripts/standards.py harness verify
python3 scripts/standards.py harness uninstall
```

## AI operations control plane

Version `0.2.0` established the provider-neutral control plane for:

- command grammar;
- autonomy levels;
- approval scope and revision binding;
- session lifecycle;
- assurance modes;
- verification statuses;
- staged memory promotion;
- external-action gates;
- stop and escalation behavior;
- cross-harness handoffs.

Canonical files:

- [`standards/ai-development/ai-operations-governance.md`](standards/ai-development/ai-operations-governance.md)
- [`policies/ai-operations.json`](policies/ai-operations.json)
- [`docs/adapters/ai-operations-adapter-contract.md`](docs/adapters/ai-operations-adapter-contract.md)
- [`templates/ai-operations/`](templates/ai-operations/)

## Cross-surface Zeref activation

The unreleased cross-surface layer supports:

- verified local Zeref activation on coding harnesses;
- source-backed simulation on ChatGPT Projects, Claude Projects, Gemini Gems, and ordinary browser chats;
- explicit activation states and receipts;
- pinned source provenance and SHA-256 pack integrity;
- freshness budgets;
- staged browser memory and writeback receipts;
- provider adapters;
- safe install, verify, and uninstall workflows.

Canonical files:

- [`policies/surface-activation.json`](policies/surface-activation.json)
- [`standards/ai-development/cross-surface-activation.md`](standards/ai-development/cross-surface-activation.md)
- [`standards/ai-development/browser-project-source-packs.md`](standards/ai-development/browser-project-source-packs.md)
- [`docs/adapters/surface-capability-matrix.md`](docs/adapters/surface-capability-matrix.md)
- [`templates/browser-project/`](templates/browser-project/)

Engineering Standards owns activation portability. Zeref Memory Engine remains unchanged and owns its runtime internals.

## Verification

Requirements:

- Git
- Python 3.11 or newer
- Bash or Zsh for legacy convenience scripts
- Make for convenience targets

Run:

```bash
make check
```

Expected high-level result:

```text
PASS  standards doctor
PASS  surface activation
PASS  repository index
PASS  unit tests
PASS  compile
```

## Adoption contract

A consuming repository should pin a released version and add:

```text
AGENTS.md
.standards/manifest.json
docs/standards-exceptions.md
```

A browser project should upload a compiled source pack and copy the generated provider instructions into the project instruction field.

Projects must not silently consume an unversioned branch or silently refresh an uploaded policy snapshot.

## Status

Version `0.2.0` is the current released baseline. Cross-surface Zeref activation and the operational repository interface are under review for the next minor release.

The following public repositories remain migration sources until their content is inventoried, reconciled, imported, and verified:

- `project-practices`
- `github-velocity-practices`
- `development-architecture-practices`
- `design-system-practices`

## Governance and security

- [Agent contract](AGENTS.md)
- [Machine repository index](REPOSITORY_INDEX.json)
- [Quickstart](docs/operations/quickstart.md)
- [AI agent entrypoint](docs/operations/agent-entrypoint.md)
- [Governance](GOVERNANCE.md)
- [Security policy](SECURITY.md)
- [Contributing](CONTRIBUTING.md)
- [Changelog](CHANGELOG.md)

## Visibility

Private internal policy. Do not publish repository content without an explicit review and redaction pass.
