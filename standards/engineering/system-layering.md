# System Layering and Ownership

## Purpose

Place behavior, state, data, security, and failure handling in explicit ownership layers.

## Expected outcome

A reviewer can identify system boundaries, client responsibilities, public contracts, application and domain logic, persistence, integrations, infrastructure, and operational ownership.

## Applicability

Applies to any product with more than one component, external dependency, persistent state, or trust boundary.

## Non-applicability

A small static artifact may use a simpler documented structure.

## Required inputs

Product flows, architecture context, data flows, trust boundaries, platform constraints, scale assumptions, and failure requirements.

## Unknowns to resolve

State authority, consistency, data ownership, external-service behavior, offline expectations, and recovery objectives.

## Required actions

Separate client, API contract, optional backend-for-frontend, application services, domain services, persistence, events, integrations, platform infrastructure, and observability where those responsibilities exist. Do not create a layer without a problem it solves.

## Required decisions

Boundaries, state ownership, public interfaces, transactions, consistency, synchronization, authentication, authorization, failure isolation, migration, rollback, and observability.

## Required details

Inputs, outputs, dependencies, trust level, data handled, failure modes, retry and idempotency behavior, owner, and tests for each material boundary.

## Expected documents and artifacts

System context, container view, data-flow map, ADRs, API contracts, failure-mode table, and operational ownership map.

## Document structure

Each boundary records responsibility, inputs, outputs, state, trust, dependencies, failures, controls, observability, tests, and owner.

## Acceptance criteria

- Every material responsibility has one authoritative owner.
- Public contracts are explicit and versioned.
- Trust boundaries and data flows are documented.
- Failure and rollback behavior are testable.
- No “middle-end” layer exists without a precise responsibility.

## Verification method

Architecture review, contract tests, threat model, failure testing, and operational review.

## Evidence required

Diagrams, ADRs, contracts, test results, and owner acknowledgements.

## Failure conditions

Duplicated state authority, hidden coupling, circular dependencies, unspecified failures, or security decisions left to UI code.

## Risks and abuse cases

Privilege escalation, stale data, replay, cascading failure, vendor outage, and inconsistent enforcement across clients.

## Guards and limits

Do not split services solely for fashion or combine unrelated trust boundaries solely to reduce files.

## Exceptions

Record the boundary debt, ceiling, trigger for change, owner, and review date.

## Cost considerations

Evaluate build, operational, cloud, observability, migration, and human cognitive cost.

## Dependencies

Architecture, security, API, backend, data, cloud, and observability standards.

## Related standards

Minimum Correct Change and Global Legal Control Plane.

## Source provenance

Use reviewed architecture patterns and official platform guidance.

## Owner and review cycle

Architecture owner. Review on material boundary, vendor, scale, or data changes.

## Zeref execution behavior

Route material boundary choices to architecture review and require an ADR before coding.

## Examples

Location permission UX belongs in the client, authorization belongs at the service boundary, and durable transaction rules belong in domain and persistence layers.

## Anti-patterns

A “middle-end” folder containing unrelated validation, API calls, state, and business rules.
