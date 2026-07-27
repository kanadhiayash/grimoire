# ADR-0006: Structured standards and document contracts

- Status: Accepted
- Date: 2026-07-24
- Owners: Repository maintainers

## Context

Human prose alone cannot reliably tell an AI when a standard applies, what artifact to create, which headings are mandatory, or what evidence proves completion.

## Decision

Every normative standard uses a shared record model covering purpose, expected outcome, applicability, inputs, unknowns, required actions and decisions, document requirements, acceptance, verification, evidence, failure conditions, risks, guards, exceptions, costs, dependencies, sources, ownership, Zeref behavior, examples, and anti-patterns.

Every required document has a machine record defining trigger, type, owner, headings, acceptance, evidence, approvers, retention, and sensitivity.

## Consequences

The repository gains more structure and validation work, but standards become testable and compilation becomes deterministic.

## Verification

Schemas validate representative standard and document records. Authoring checks reject missing mandatory sections.
