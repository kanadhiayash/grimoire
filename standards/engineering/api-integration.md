# API and Integration Engineering

## Purpose

Create secure, evolvable, observable contracts between clients, services, vendors, and event consumers.

## Expected outcome

Every public or cross-boundary interface has explicit semantics, validation, compatibility, failure behavior, ownership, and evidence.

## Applicability

HTTP APIs, GraphQL, RPC, webhooks, events, SDKs, file exchanges, and external-service integrations.

## Non-applicability

In-process private interfaces still follow language and architecture conventions but may not require an external contract artifact.

## Required inputs

Domain model, consumers, trust boundaries, data classification, latency and availability needs, and compatibility policy.

## Unknowns to resolve

Consumer count, ownership, versioning, idempotency, rate limits, delivery guarantees, and vendor failure behavior.

## Required actions

Define resource or operation semantics, schemas, authentication, authorization, validation, error model, pagination, idempotency, timeouts, retries, rate limits, observability, deprecation, and compatibility.

## Required decisions

Protocol, versioning, synchronous or asynchronous behavior, consistency, delivery guarantee, webhook verification, SDK generation, and fallback.

## Required details

Request, response, event, error, status, identity, permissions, correlation, timestamps, retries, and sensitive-field handling.

## Expected documents and artifacts

OpenAPI or equivalent contract, event schema, integration ADR, data classification, consumer list, compatibility plan, and contract tests.

## Document structure

Each operation records purpose, actor, authorization, request, response, errors, idempotency, limits, observability, compatibility, and tests.

## Acceptance criteria

- Server-side authorization exists for protected operations.
- Inputs and outputs are validated.
- Errors are stable and do not leak secrets.
- Retried mutations are safe where required.
- Compatibility and deprecation are explicit.
- External failures have bounded handling.

## Verification method

Schema validation, contract tests, authorization tests, replay tests, failure injection, and consumer review.

## Evidence required

Published contract, test output, example payloads without sensitive data, and compatibility record.

## Failure conditions

Undocumented behavior, breaking change without migration, infinite retry, missing authorization, unverified webhook, or vendor secrets in clients.

## Risks and abuse cases

Enumeration, injection, replay, confused deputy, excessive data exposure, denial of service, and supply-chain failure.

## Guards and limits

Do not expose internal persistence models as accidental public contracts. Do not add a gateway or BFF without client-specific needs.

## Exceptions

Record consumer, duration, compatibility risk, owner, and removal date.

## Cost considerations

Track request volume, egress, vendor pricing, retries, latency, SDK maintenance, and observability cost.

## Dependencies

Security, privacy, architecture, data, cloud, and stack overlays.

## Related standards

System Layering, Backend and Data, and Global Legal Control Plane.

## Source provenance

Use official protocol, platform, and API design guidance.

## Owner and review cycle

Interface owner with consumer reviewers. Review on contract or vendor changes.

## Zeref execution behavior

Require contract-first context and run contract and security tests before PASS.

## Examples

A create operation accepts an idempotency key and returns a stable domain error schema.

## Anti-patterns

Client-specific secrets embedded in an app or undocumented 200 responses containing errors.
