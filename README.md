# Engineering Standards

Private, versioned engineering policy for human and AI-assisted product development.

This repository is the canonical source for project structure, architecture, GitHub operations, security, testing, release readiness, product and UX quality, and AI-agent execution rules used by Yash Kanadhia and Zeref OS.

## Why this exists

Written principles are useful, but they are not enforcement. This repository converts reusable engineering guidance into a system with four layers:

1. Human-readable standards
2. Machine-readable policies and profiles
3. Harness-specific instruction adapters
4. Local and CI conformance checks

```text
Standards -> Policies -> Adapters -> Project manifests -> Verification
```

## Core guarantees

A conforming project must:

- Read project context before editing
- Separate facts, assumptions, unknowns, and risks when material
- Make the smallest complete change
- Preserve tests, security controls, and existing quality gates
- Never invent repository state, metrics, citations, or verification results
- Verify behavior before claiming success
- Record architecture-impacting decisions
- Tie public claims to reproducible evidence
- Apply the same review standard to human and AI-generated changes

## Repository map

| Path | Purpose |
|---|---|
| `standards/` | Human-readable rules and rationale |
| `policies/` | Machine-readable baseline and schema |
| `profiles/` | Risk-based enforcement profiles |
| `adapters/` | Compact instructions for AI harnesses |
| `templates/` | Reusable governance and delivery templates |
| `checks/` | Dependency-free conformance checker |
| `scripts/` | Local doctor and test commands |
| `tests/` | Conformance checker tests |
| `docs/` | Architecture decisions, exceptions, and migration records |

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
Tests: PASS
```

## Adoption contract

A consuming project should pin a released version and add:

```text
AGENTS.md
.standards/manifest.json
docs/standards-exceptions.md
```

The manifest selects the standards version, profile, stack overlays, and required checks. Projects must not silently consume an unversioned branch.

## Status

Version `0.1.0` establishes the canonical repository scaffold and initial hardened policy contract.

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
