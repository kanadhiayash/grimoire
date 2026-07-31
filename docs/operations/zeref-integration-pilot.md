# Zeref Integration Pilot

Grimoire treats Zeref as a separate continuity and execution-routing layer used
through an active harness. Zeref is not represented as a standalone code
execution engine.

The pilot uses this private Grimoire repository as the approved project. Its
plan is bound to one base commit, a closed file scope, zero external cost,
read/write and test tools, explicit prohibited tools, and approval-required
external actions.

## Status rule

- Pack compilation can pass independently.
- Receipt structure and content binding can pass independently.
- A self-authenticated receipt cannot prove execution.
- A separate clean reproduction with a detached attestation is required for
  the scoped pilot status.
- The detached attestation records declared reviewer identity but does not
  provide cryptographic identity verification.
- Project readiness and release assurance remain separate evidence dimensions.

## Rollback

Delete generated `artifacts/zeref-pilot/` outputs. Reverting the pilot PR removes
the runner and fixtures. No Zeref repository, memory, credential, deployment,
publication, or external project state is changed.
