# Engineering Standards

Private, versioned engineering policy for human and AI-assisted product development.

This repository is the canonical source for project structure, architecture, GitHub operations, security, testing, release readiness, product and UX quality, AI-agent execution rules, and cross-surface Zeref activation used by Yash Kanadhia.

## Why this exists

Written principles are useful, but they are not enforcement. This repository converts reusable engineering guidance into a system with five layers:

1. Human-readable standards
2. Machine-readable policies and profiles
3. Harness and browser-surface adapters
4. Compiled project contracts and source packs
5. Local and CI conformance checks

```text
Standards -> Policies -> Adapters -> Project manifests or source packs -> Verification
```

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

| Path | Purpose |
|---|---|
| `standards/` | Human-readable rules and rationale |
| `policies/` | Machine-readable baseline, AI operations, surface activation, and schemas |
| `profiles/` | Risk-based enforcement profiles |
| `adapters/` | Compact instructions for coding harnesses and browser project surfaces |
| `templates/` | Reusable governance, AI operations, browser source-pack, and delivery templates |
| `checks/` | Dependency-free conformance checkers |
| `scripts/` | Doctor, tests, pack compiler, verifier, and installer |
| `tests/` | Conformance and adversarial behavior tests |
| `docs/` | Architecture decisions, capability matrices, adapter contracts, exceptions, and migration records |

## AI operations control plane

Version `0.2.0` established the provider-neutral control plane for AI-assisted execution:

- command grammar
- autonomy levels
- approval scope and revision binding
- session lifecycle
- assurance modes
- verification statuses
- staged memory promotion
- external-action gates
- stop and escalation behavior
- cross-harness handoffs

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
- generated provider adapters;
- safe install, verify, and uninstall workflows.

Canonical files:

- [`policies/surface-activation.json`](policies/surface-activation.json)
- [`standards/ai-development/cross-surface-activation.md`](standards/ai-development/cross-surface-activation.md)
- [`standards/ai-development/browser-project-source-packs.md`](standards/ai-development/browser-project-source-packs.md)
- [`docs/adapters/surface-capability-matrix.md`](docs/adapters/surface-capability-matrix.md)
- [`templates/browser-project/`](templates/browser-project/)

Engineering Standards owns activation portability. Zeref Memory Engine remains unchanged and owns its runtime internals.

## Compile a browser pack

```bash
python3 scripts/compile_surface_pack.py \
  --surface chatgpt-project \
  --project-name "Example Project" \
  --output ./dist/example-project \
  --engineering-standards-commit <40-character-sha> \
  --zeref-commit <40-character-sha>
```

Verify:

```bash
python3 scripts/verify_surface_pack.py ./dist/example-project
```

## Install local harness activation

Dry-run:

```bash
python3 scripts/install_ai_harness_standards.py plan
```

Apply managed blocks:

```bash
python3 scripts/install_ai_harness_standards.py apply
```

Verify:

```bash
python3 scripts/install_ai_harness_standards.py verify
```

The installer backs up existing files and manages only marked blocks.

## Local verification

Requirements:

- Git
- Python 3.11 or newer
- Bash or Zsh
- Make

Run:

```bash
make check
```

Expected result:

```text
Engineering Standards Doctor: PASS
Surface activation policy: PASS
Tests: PASS
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

Version `0.2.0` is the current released baseline. Cross-surface Zeref activation is under review for the next minor release.

The following public repositories remain migration sources until their content is inventoried, reconciled, imported, and verified:

- `project-practices`
- `github-velocity-practices`
- `development-architecture-practices`
- `design-system-practices`

## Governance and security

- [Agent contract](AGENTS.md)
- [Governance](GOVERNANCE.md)
- [Security policy](SECURITY.md)
- [Contributing](CONTRIBUTING.md)
- [Changelog](CHANGELOG.md)

## Visibility

Private internal policy. Do not publish repository content without an explicit review and redaction pass.
