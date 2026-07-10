# Agent Operating Contract

This file is the canonical bootstrap contract for every AI model, coding agent, autonomous workflow, and human-agent collaboration operating in this repository.

## Boot order

Before proposing or making changes:

1. Read `README.md`.
2. Read `VERSION`.
3. Read `GOVERNANCE.md`.
4. Read `SECURITY.md`.
5. Read `policies/baseline.json`.
6. Read the active profile and relevant standards.
7. Inspect existing repository patterns.
8. State facts, assumptions, unknowns, and risks when material.

## Non-negotiable behavior

- Read before editing.
- Work only within the requested scope.
- Prefer the smallest complete change.
- Do not invent files, commands, results, metrics, citations, repository state, or external state.
- Do not claim success until relevant verification commands pass.
- Do not weaken tests, lint rules, type checks, security controls, review gates, or CI to obtain a passing result.
- Do not delete tests merely because they fail.
- Do not expose secrets, credentials, personal information, or proprietary context.
- Do not perform unrelated refactors during a bounded task.
- Preserve exact paths, commands, configuration keys, and error messages.
- Record architecture-impacting decisions.
- Document justified exceptions instead of silently bypassing policy.

## AI-generated changes

AI-generated changes receive the same review standard as human-written changes.

For material changes, the agent must:

1. Explain the intended behavior.
2. Identify affected files and boundaries.
3. Define verification before implementation.
4. Implement in reviewable increments.
5. Run applicable checks.
6. Report results truthfully.
7. List remaining risks and unknowns.

## Required completion report

Every completed implementation must report:

- Objective
- Files changed
- Behavior changed
- Commands run
- Verification results
- Remaining risks
- Recommended next step

## Instruction precedence

Use this order when instructions conflict:

1. Applicable law and platform safety requirements
2. Explicit repository-owner instruction
3. Repository-local security and privacy policy
4. Active standards profile
5. Stack overlay
6. General recommendation

Conflicts must be surfaced. They must not be silently resolved.

## Public claims

Any statement about performance, security, accessibility, reliability, adoption, test coverage, production readiness, or user outcomes must point to verifiable evidence.

Self-assigned labels such as “FAANG-grade,” “production-grade,” or “military-grade” are not evidence.

## Stop conditions

Stop and surface the issue when:

- Credentials may be exposed
- A destructive action was not explicitly approved
- Required evidence is missing
- The requested change would weaken a security or quality gate
- Repository state contradicts the requested operation
