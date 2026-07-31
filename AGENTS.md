# Grimoire Agent Contract

This file is the canonical bootstrap contract for every human, AI model, coding agent, and autonomous workflow operating in this repository.

## Repository identity

Grimoire is the neutral, versioned Global Product Engineering Standards Orchestrator. It defines reusable product, design, engineering, legal, accessibility, AI, security, privacy, cloud, cost, Git, delivery, and operational standards.

Zeref Memory Engine is a separate execution and continuity runtime. This repository may compile execution profiles for Zeref but does not own or rewrite Zeref internals.

## Core operating model

Detailed at rest, selective during execution:

```text
Canonical standards + project manifest + approved project records
    -> applicability and context compiler
    -> one bounded AI context pack
    -> Zeref-routed execution
    -> fresh verification evidence
```

## Boot order

Before material work:

1. Read `README.md`.
2. Read `VERSION`.
3. Read `REPOSITORY_INDEX.json`.
4. Read `GOVERNANCE.md` and `SECURITY.md`.
5. Read `policies/baseline.json`, `policies/standards-orchestrator.json`, and only the relevant policy modules.
6. Read the active project manifest and compiled pack when working in a consuming project.
7. Read only the standards, overlays, templates, skills, sources, checks, and tests relevant to the task.
8. Inspect existing patterns before editing.
9. State facts, assumptions, unknowns, risks, and conflicts when material.

Do not scan or inject the full repository when the index and compiler identify a smaller sufficient set.

## Fast commands

```bash
python3 scripts/grimoire.py status --json
python3 scripts/grimoire.py catalog --json
python3 scripts/grimoire.py project boot \
  --manifest templates/project/project.json \
  --output artifacts/example-standards-pack
python3 scripts/verify_documented_commands.py --json
python3 scripts/grimoire.py check
```

## Source-of-truth order

1. Applicable law, platform safety, and system requirements
2. Current explicit user instruction
3. Exact approved plan and revision
4. Repository contract, governance, security, privacy, active profile, and applicable architecture decisions
5. Verified project facts, decisions, exceptions, and configuration
6. Compiled Standards Orchestrator pack
7. Neutral global instructions
8. Explicit personal overlay
9. Verified canonical memory
10. Historical handoffs, external references, examples, and general knowledge

Same-level conflicts must be surfaced. Never choose silently by confidence, recency, or convenience.

## Human and AI equality

Human-written and AI-generated changes receive the same requirements for scope, evidence, review, security, accessibility, testing, and verification.

## Required behavior

- Read before editing.
- Work only within approved scope.
- Prefer the smallest complete change.
- Use official language and framework conventions through overlays.
- Separate priority, severity, risk, evidence confidence, and gate effect.
- Do not invent files, research, users, quotes, metrics, citations, legal applicability, repository state, runtime capability, or test results.
- Do not claim success until relevant checks pass.
- Do not weaken tests, security, privacy, accessibility, legal, data, review, or CI controls.
- Record architecture-impacting decisions.
- Record justified exceptions with owner and expiry.
- Do not create a second command registry, lifecycle, completion vocabulary, or canonical policy source.

## Standard authoring

Normative standards must follow `standards/universal/standard-authoring.md` and `templates/standards/STANDARD.md`. Every standard defines expected outcomes, applicability, inputs, unknowns, actions, decisions, details, documents, document structure, acceptance, verification, evidence, failure conditions, risks, guards, exceptions, costs, dependencies, sources, ownership, Zeref behavior, examples, and anti-patterns.

## Product and design work

Do not begin with unsupported personas or screens. Establish need, evidence, actors, user groups, flows, interaction states, accessibility, content, risks, metrics, design-system mappings, validation status, and handoff requirements. Translate subjective terms such as “professional” into measurable criteria.

## Engineering work

During coding, apply `standards/engineering/minimum-correct-change.md`:

1. Confirm approved plan and revision.
2. Understand the actual code path.
3. Reuse before creating.
4. Prefer standard-library, framework-native, and platform-native capabilities.
5. Change the correct ownership layer.
6. Avoid unnecessary dependencies, files, abstractions, and configuration.
7. Preserve safeguards.
8. Add runnable verification.
9. Stop when acceptance criteria pass.

## Legal and compliance behavior

Do not assume jurisdiction, law, industry, user age, data category, or compliance status. Distinguish binding authority from guidance, standards, best practices, trends, proposals, drafts, and superseded sources. Use official sources. Automated systems may report applicability and evidence status but must not issue a final legal-compliance certification.

## Zeref boundary

The Orchestrator defines requirements, outcomes, documents, gates, evidence, and limits. Zeref owns activation, roles, model and tool routing, skills, approvals, retries, memory, and execution receipts.

- Do not modify `kanadhiayash/zeref-memory-engine` without separate approval.
- Do not duplicate Zeref internals.
- Do not call browser simulation verified local runtime execution.
- Do not let personal overlays weaken neutral standards.

## External actions

Explicit approval is required for merge, deploy, publish, external send, destructive changes, credentials, and canonical memory promotion.

## Completion report

Every material implementation reports:

- Objective
- Context used
- Files changed
- Behavior changed
- Commands run
- Verification results
- Intentionally untouched scope
- Facts, assumptions, unknowns, risks, and conflicts
- Recommended next action

Completion statuses are `PASS`, `PARTIAL`, `BLOCKED`, and `NOT_VERIFIED`.

## Stop conditions

Stop and surface the smallest recovery path when credentials or private data may be exposed, destructive or external action lacks approval, canonical sources conflict, required evidence is missing, a safeguard would be weakened, repository state contradicts the operation, retries are exhausted without new evidence, or the available tool cannot perform the claimed action.
