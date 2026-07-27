# ADR-0002: Add a provider-neutral AI operations control plane

- Status: Accepted
- Date: 2026-07-21
- Owner: Yash Kanadhia
- Tracks: Issue #1

## Context

Grimoire already centralizes human-readable standards, machine policy, harness adapters, and verification. It does not yet define the operational lifecycle used across Zeref-assisted work: command semantics, bounded autonomy, approval scope, memory promotion, session lifecycle, assurance modes, or cross-harness handoffs.

Duplicating these rules inside every global or project instruction would create drift. Treating ambitious phrases as permission would create unsafe autonomy. Treating a single model as a multi-model council would create false assurance.

## Decision

Add one provider-neutral AI operations control plane with four parts:

1. `standards/ai-development/ai-operations-governance.md` defines human-readable behavior.
2. `policies/ai-operations.json` defines machine-readable commands, autonomy, approvals, memory, lifecycle, and stop conditions.
3. `templates/ai-operations/` defines reviewable mission, approval, run-report, escalation, and handoff records.
4. Dependency-free checks validate required semantics and prevent policy drift.

Personal global and project instructions remain adapters. They must reference or preserve this contract rather than become alternate sources of authority.

## Consequences

- AI operations become versioned engineering policy rather than prompt folklore.
- Approval words cannot authorize undefined scope.
- Councils must match actual independent execution.
- Memory promotion becomes staged and reviewable.
- Existing consumers remain compatible until they opt into this policy.
- Adapter generation and project-manifest integration remain future work.
