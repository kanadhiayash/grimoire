# Backend and Data Engineering

## Purpose

Protect domain integrity, personal data, reliability, and operational control across services and persistence.

## Expected outcome

Domain rules, persistence, authorization, migrations, retention, deletion, jobs, events, backups, and recovery are explicit and tested.

## Applicability

Server-side applications, functions, workers, databases, queues, caches, search, analytics stores, and data pipelines.

## Non-applicability

A static client without server-side processing still follows local storage and privacy controls.

## Required inputs

Domain model, data classification, volume, consistency, retention, recovery objectives, authorization, and legal controls.

## Unknowns to resolve

Source of truth, transaction boundaries, deletion propagation, backup retention, migration strategy, and operational ownership.

## Required actions

Enforce authorization at trusted boundaries. Validate inputs. Define transactions, concurrency, idempotency, migrations, retention, deletion, backup, restore, audit, jobs, queues, cache invalidation, and data-quality controls.

## Required decisions

Storage technology, schema, consistency, indexing, partitioning, encryption, access, residency, archival, deletion, and recovery.

## Required details

Data owner, purpose, sensitivity, source, transformations, consumers, retention, access, lineage, quality, and deletion behavior.

## Expected documents and artifacts

Data model, data inventory, migration plan, retention schedule, access matrix, backup and restore plan, runbook, and data-quality checks.

## Document structure

Each dataset records purpose, fields, classification, source, authority, access, retention, transfer, deletion, quality, and owner.

## Acceptance criteria

- Trusted boundaries enforce authorization and validation.
- Migrations are reversible or have tested recovery.
- Retention and deletion are executable, not only documented.
- Backup restore is tested where required.
- Jobs and messages handle duplication and failure safely.
- Sensitive data is not logged without approved need and controls.

## Verification method

Unit, integration, migration, authorization, concurrency, restore, retention, deletion, and data-quality tests.

## Evidence required

Schemas, migration output, test results, restore evidence, access review, and operational dashboards.

## Failure conditions

Unbounded retention, orphaned personal data, untested restore, missing authorization, destructive migration without rollback, or silent job loss.

## Risks and abuse cases

Privilege escalation, data exfiltration, mass assignment, injection, replay, race conditions, poison messages, and vendor lock-in.

## Guards and limits

Do not add storage, queues, caches, or services without ownership, failure, cost, and exit analysis.

## Exceptions

Document data affected, risk, temporary control, owner, approval, and expiry.

## Cost considerations

Track storage, reads, writes, compute, transfer, backup, restore, vendor minimums, and operational labor.

## Dependencies

Architecture, API, security, privacy, cloud, observability, and legal standards.

## Related standards

System Layering, Cloud Reliability and Cost, and Minimum Correct Change.

## Source provenance

Use official database, framework, security, and jurisdiction sources.

## Owner and review cycle

Backend and data owners. Review on schema, vendor, residency, scale, or retention changes.

## Zeref execution behavior

Require data and migration context before changes. Block destructive operations without approval and verified backup or recovery path.

## Examples

Account deletion queues idempotent deletion across primary data, derived data, and allowed backup lifecycle.

## Anti-patterns

A soft-delete flag presented as full deletion with no retention or downstream handling.
