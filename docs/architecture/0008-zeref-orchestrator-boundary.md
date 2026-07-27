# ADR-0008: Standards Orchestrator and Zeref execution boundary

- Status: Accepted
- Date: 2026-07-24
- Owners: Repository maintainers

## Context

The standards system and the execution runtime must work together without duplicating command registries, skills, memory internals, permissions, or model routing.

## Decision

The Standards Orchestrator defines applicable requirements, outcomes, documents, gates, evidence, limits, and completion criteria. Zeref detects the execution environment, selects roles, models, tools, and skills, manages approvals and retries, performs bounded execution, and emits receipts. Project repositories remain authoritative for facts, decisions, plans, code, and evidence.

## Guards

- This repository does not rewrite Zeref internals.
- Browser simulation is never labeled local runtime execution.
- Zeref cannot override locked standards or approved plan revisions.
- The Orchestrator cannot claim actions Zeref did not verify.

## Verification

Compiled packs include a `ZEREF_EXECUTION_PROFILE.json` with explicit mode, cost ceiling, approval actions, stop conditions, and completion statuses.
