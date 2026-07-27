# Governance

## Canonical authority

This repository is the canonical private source for neutral product engineering standards, machine policy, project compilation, cross-surface adapters, and verification. It is not a source of project facts, legal advice, or Zeref runtime internals.

Consuming projects pin a released version or exact reviewed commit. They must not silently follow an unversioned branch or refresh compiled packs without review.

## Ownership boundaries

- Standards Orchestrator: requirements, profiles, overlays, expected outcomes, document contracts, gates, evidence, and limits.
- Zeref: activation, roles, models, tools, skills, approvals, retries, memory, and execution receipts.
- Project repository: facts, decisions, plans, code, designs, exceptions, and evidence.
- Qualified legal reviewers: final jurisdiction-specific legal interpretation and compliance conclusions.

## Change classes

### Patch

Clarifications, source metadata corrections, non-behavioral documentation, and compatible validator fixes.

### Minor

Backward-compatible standards, profiles, schemas, templates, commands, adapters, skills, source records, or checks.

### Major

Breaking policy, precedence, lifecycle, command semantics, schema, completion vocabulary, legal-status vocabulary, or manifest compatibility changes.

## Required process for material changes

1. Create a focused branch.
2. Explain the problem, expected outcome, scope, and non-goals.
3. Identify affected standards, policies, schemas, profiles, adapters, templates, instructions, sources, checks, and tests.
4. Write or update tests before or with behavior changes.
5. Record architecture decisions.
6. Include compatibility, migration, privacy, accessibility, security, legal, cost, and Zeref-boundary analysis.
7. Open a reviewable pull request.
8. Run all required checks.
9. Verify protected external repositories remain unchanged.
10. Update `VERSION`, release notes, and changelog when releasing.

## Standards changes

Every normative standard follows the standard-authoring contract. External material is not copied into canonical policy without source classification, adoption rationale, license review where needed, version, effective date, review date, and local interpretation.

## Legal source governance

Official sources are canonical. Guidance, standards, best practices, trends, proposals, and drafts remain separate authority classes. The registry must record freshness and supersession. Automated systems cannot issue final legal-compliance certification.

## Instruction governance

Neutral global instructions contain no personal identity or project-specific claims. Personal overlays are optional, explicitly selected, and excluded from neutral packs. Personal overlays cannot weaken law, safety, privacy, accessibility, approval, or evidence controls.

## Exceptions

Projects record exceptions only in `docs/standards-exceptions.md` or another path explicitly named by the project manifest. Each exception includes rule, scope, reason, risk, compensating control, owner, approver, review date, and expiry or removal condition. Undocumented exceptions are violations.

## External actions

Merge, deploy, publish, external send, destructive changes, credentials, canonical memory, and legal publication remain approval-gated.

## Legacy repositories

`project-practices`, `github-velocity-practices`, `development-architecture-practices`, and `design-system-practices` remain migration sources until inventoried, reconciled, imported, and verified.
