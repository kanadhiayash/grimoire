# ADR 0022: CI Assurance Boundary

- Status: Accepted
- Date: 2026-07-30

## Context

The original Phase 8 plan included secret scanners, static-analysis scanners,
repository scorecards, and related cybersecurity tooling. The current owner
boundary explicitly excludes cybersecurity actions and asks for a clean
operational upgrade without bypassing policy.

## Decision

Phase 8.2 implements a non-cyber CI governance gate. It verifies:

- every external GitHub Action reference uses a full immutable commit SHA;
- workflow permissions remain read-only;
- workflow failure suppression is not enabled;
- approved CI-only dependencies are versioned and hashed;
- the Grimoire runtime core has no external imports;
- exact policy evidence is retained as a CI artifact.

The existing CI-only Draft 2020-12 validator remains approved. No new runtime or
development dependency is introduced.

The original cybersecurity-specific toolchain is deferred:

- secret-scanner expansion: `NOT_VERIFIED`;
- static-analysis scanner: `NOT_VERIFIED`;
- repository Scorecard: `NOT_VERIFIED`;
- scanner-derived security assurance: `NOT_VERIFIED`.

No deferred item may be converted to `PASS` through documentation, a skipped
job, or self-scoring.

## Consequences

This gate improves CI integrity and reviewability without performing
cybersecurity testing. It does not certify repository security, dependency
safety, or release assurance. A future owner-approved mission must separately
define any cybersecurity tools, permissions, pins, false-positive process, and
data-handling boundary.

## Rollback

Revert the policy checker, workflow job, tests, index entry, and this ADR
together. Existing conformance and runtime matrix jobs remain unchanged.
