# Agent Operating Contract

This file is the canonical bootstrap contract for every AI model, coding agent, autonomous workflow, and human-agent collaboration operating in this repository.

## Repository identity

Engineering Standards is the canonical private control plane for reusable engineering policy, AI operations, cross-surface adapters, compiled project contracts, and verification used by Yash Kanadhia projects.

Zeref Memory Engine is a separate runtime. This repository may define how supported surfaces detect, activate, or simulate Zeref operations. It does not own or rewrite Zeref internals.

## Boot order

Before proposing or making material changes:

1. Read `README.md` for the human overview.
2. Read `VERSION`.
3. Read `REPOSITORY_INDEX.json` for the machine route map.
4. Read `GOVERNANCE.md` and `SECURITY.md`.
5. Read `policies/baseline.json`.
6. Read the active profile and only the standards, policies, adapters, templates, checks, and tests relevant to the task.
7. Inspect existing repository patterns.
8. State facts, assumptions, unknowns, risks, and conflicts when material.

Do not scan the full repository when the index and task router identify a smaller sufficient source set.

## Fast operational commands

```bash
python3 scripts/standards.py status --json
python3 scripts/standards.py catalog --json
python3 scripts/standards.py check
```

The machine-readable command and surface catalog is `REPOSITORY_INDEX.json`.

## Task routing

| Task | Start with |
|---|---|
| Universal engineering rule | Baseline policy, relevant standard, active profile, tests |
| AI operations behavior | `policies/ai-operations.json`, schema, governance standard, adapter contract |
| Cross-surface activation | `policies/surface-activation.json`, schema, activation standard, capability matrix |
| Harness or browser adapter | Canonical policy, adapter contract, target adapter, tests |
| Browser source pack | Source-pack standard, templates, compiler, verifier, tests |
| Installer | Installer, activation policy, installer tests, safety boundaries |
| Repository navigation or CLI | Repository index, schema, checker, CLI, operator guides |
| Release | Governance, changelog, version, compatibility and migration evidence |

See `docs/operations/agent-entrypoint.md` for the expanded route map.

## Implementation stack

Use the smallest portable stack that satisfies repository requirements:

- Python 3.11+ standard library for executable control-plane logic
- JSON and JSON Schema for machine contracts
- Markdown for human and agent instructions
- Bash or Zsh only for thin launchers
- GitHub Actions YAML for CI

Do not add a framework, database, service, or second implementation language without measured evidence that the existing stack cannot satisfy the requirement.

## Non-negotiable behavior

- Read before editing.
- Work only within the requested scope.
- Prefer the smallest complete change.
- Do not invent files, commands, results, metrics, citations, repository state, runtime capability, or external state.
- Do not claim success until relevant verification commands pass.
- Do not weaken tests, lint rules, type checks, security controls, accessibility requirements, review gates, or CI to obtain a passing result.
- Do not delete tests merely because they fail.
- Do not expose secrets, credentials, personal information, or proprietary context.
- Do not perform unrelated refactors during a bounded task.
- Preserve exact paths, commands, configuration keys, and error messages.
- Record architecture-impacting decisions.
- Document justified exceptions instead of silently bypassing policy.
- Do not create a second command registry, autonomy scale, memory lifecycle, or canonical policy source.

## AI-generated changes

AI-generated changes receive the same review standard as human-written changes.

For material changes, the agent must:

1. Explain intended behavior and non-goals.
2. Identify affected files and boundaries.
3. Define verification before implementation.
4. Write or update tests before or with behavior changes.
5. Implement in reviewable increments.
6. Run applicable checks.
7. Report exact results and remaining risk.

## Instruction precedence

Use the canonical order from `policies/ai-operations.json`:

1. Applicable law, platform safety, and system requirements
2. The current explicit user instruction
3. The exact approved plan and revision
4. The repository contract: `AGENTS.md`, security, privacy, governance, active profile, and applicable architecture decisions
5. Project instructions and configuration
6. Stable global instructions
7. Verified canonical memory
8. Historical handoffs
9. External references
10. General knowledge

Same-level conflicts must be surfaced and arbitrated. Never choose silently by recency, confidence, or convenience.

## Zeref boundary

- Do not modify `kanadhiayash/zeref-memory-engine` under this repository’s task scope.
- Do not duplicate Zeref agents, skills, memory internals, model routing, permissions, or boot contract.
- Browser source-backed simulation must never be described as verified local runtime execution.
- Activation adapters must detect, classify, defer, and report truthfully.

## Public claims

Any statement about performance, security, accessibility, reliability, adoption, test coverage, production readiness, runtime activation, or user outcomes must point to verifiable evidence.

Self-assigned labels are not evidence.

## Required completion report

Every completed implementation must report:

- Objective
- Files changed
- Behavior changed
- Commands run
- Verification results
- Files or scope intentionally untouched
- Remaining risks and unknowns
- Recommended next step

Machine completion states are `PASS`, `PARTIAL`, `BLOCKED`, and `NOT_VERIFIED`.

## Stop conditions

Stop and surface the smallest recovery path when:

- credentials or private data may be exposed;
- a destructive or external action lacks explicit approval;
- canonical sources conflict;
- required evidence is missing;
- a requested change weakens a security, accessibility, or quality gate;
- repository state contradicts the requested operation;
- retries are exhausted without new evidence;
- the available tool cannot perform the claimed action.
