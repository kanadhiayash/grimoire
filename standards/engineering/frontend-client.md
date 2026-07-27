# Frontend and Client Engineering

## Purpose

Build accessible, performant, resilient clients that implement the approved product and design contract.

## Expected outcome

Client behavior, state, rendering, data access, accessibility, performance, telemetry, and recovery are explicit and tested.

## Applicability

Web, native mobile, desktop, embedded, and cross-platform clients.

## Non-applicability

Machine-only services use API and backend standards instead.

## Required inputs

Approved flows and states, component and token contracts, API contracts, device and browser support, accessibility profile, and performance budgets.

## Unknowns to resolve

Offline behavior, cache authority, data freshness, navigation ownership, telemetry, and supported device ceilings.

## Required actions

Separate local UI state from server state. Use semantic platform controls where possible. Implement complete states, cancellation, retries, permissions, accessibility, localization, error boundaries, telemetry, and feature-flag behavior where applicable.

## Required decisions

Rendering strategy, state ownership, navigation, data fetching, cache and invalidation, forms and validation, offline strategy, error handling, analytics, and component boundaries.

## Required details

Loading, partial, empty, offline, stale, permission, error, success, focus, keyboard, motion, scaling, and responsive behavior.

## Expected documents and artifacts

Client architecture note, component map, state matrix, performance budget, accessibility plan, analytics specification, and test plan.

## Document structure

Record route or screen, purpose, state, data, actions, accessibility, telemetry, failure, tests, and owner.

## Acceptance criteria

- Client does not enforce server-authoritative security alone.
- States match the approved design contract.
- Accessibility and performance budgets pass.
- Data fetching and cache behavior are deterministic.
- Errors provide recovery without exposing sensitive details.

## Verification method

Unit, component, integration, accessibility, visual, performance, device, and end-to-end tests according to risk.

## Evidence required

Test output, performance measurements, accessibility results, screenshots or recordings, and known limitations.

## Failure conditions

Business rules duplicated inconsistently, inaccessible custom controls, unbounded requests, silent errors, stale data represented as current, or missing degraded states.

## Risks and abuse cases

Client tampering, sensitive logging, insecure storage, tracking without disclosure, and misleading UI state.

## Guards and limits

Do not add a state library, router, analytics SDK, or custom component system without a demonstrated need and approval.

## Exceptions

Document unsupported platform, user impact, compensating behavior, owner, and removal plan.

## Cost considerations

Track bundle, startup, rendering, network, battery, SDK, testing, and maintenance cost.

## Dependencies

Product design, accessibility, API, security, privacy, performance, and stack overlays.

## Related standards

Minimum Correct Change, Design Token Conventions, and System Layering.

## Source provenance

Use official framework and platform guidance pinned through overlays.

## Owner and review cycle

Client engineering owner. Review on platform, framework, or major flow changes.

## Zeref execution behavior

Load the exact client overlay and approved screen contract. Prefer existing components and native APIs. Stop on absent API or state contract.

## Examples

An offline transaction draft is clearly local, recoverable, and synchronized through an idempotent contract.

## Anti-patterns

A custom button, modal, state manager, and fetch wrapper added for a single screen without evidence.
