# ADR 0024: Release and Standards Policy Versioning

- Status: Accepted
- Date: 2026-07-30

## Context

Grimoire has more than one versioned contract. The repository release version
describes the complete product. The standards policy version describes the
manifest-to-policy compatibility boundary. Treating them as one value would
silently reject valid 0.5.x manifests or accept an invented standards pin.

## Decision

The repository release version and standards policy version remain independent:

- `VERSION`, `REPOSITORY_INDEX.standard_version`, and release notes carry the
  repository release version.
- `policies/standards-orchestrator.json.module_version`,
  `policies/baseline.json.standards_orchestrator.policy_version`, the project
  manifest schema, and the runtime validator carry the standards policy
  version.

The 1.0.0 repository release continues to accept the reviewed `0.4.0` standards
policy pin. A future standards policy version requires its own migration,
schema, validator, fixtures, and compatibility decision. Repository release
number changes cannot alter that pin implicitly.

`schema_version` remains an integer structural schema revision. It is not a
semantic repository release version or standards policy version.

## Consequences

Existing 0.5.x manifests remain compatible when structurally valid and pinned
to standards policy `0.4.0`. Unsupported pins such as `99.0.0` remain rejected.
Documentation must name which version it means.
