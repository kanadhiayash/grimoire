# ADR 0016: Normative Standard Registry

## Status

Accepted.

## Context

Grimoire has human-readable standards, but real standards resolution needs a
machine-first registry that can be validated, deduplicated, and linked back to
the Markdown source without treating document count as compliance evidence.

## Decision

Grimoire standard records live under `registry/standards/`. Each accepted record
has a stable ID, semantic version, normative status, domain, requirement level,
owner, review date, provenance, applicability predicate data, and a repository
local human-document link.

Only records with `status: "normative"` are accepted by the registry loader.
Guidance, draft, example, and superseded records are rejected for compilation.

## Boundaries

- Markdown remains the human-readable source.
- Registry records do not duplicate normative prose.
- Runtime validation remains Python standard-library only.
- This registry does not create a second command registry or source registry.
- Offensive security workflows are not introduced by this decision.

## Testing

Focused registry tests cover duplicate IDs, missing required fields, missing
provenance, non-normative statuses, path escape, and repository registry
validation. The doctor check validates the registry during full conformance.
