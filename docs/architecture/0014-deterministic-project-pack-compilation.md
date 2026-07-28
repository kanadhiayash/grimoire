# ADR 0014: Deterministic Project Pack Compilation

## Status

Accepted.

## Context

Project packs must be reviewable as evidence. Repeated compilation from the
same validated manifest should be able to produce byte-identical artifacts when
the operator requests deterministic mode.

## Decision

The project compiler supports deterministic mode. When enabled, it uses a fixed
default generation timestamp unless the caller pins `--generated-at`
explicitly. The generated file set is still validated by the safe filesystem
promotion layer before final output replacement.

The default non-deterministic path keeps current timestamp behavior for normal
operator use.

## Boundaries

- Deterministic generation proves repeatability for local pack artifacts only.
- It does not verify source authenticity, runtime execution, legal status, or
  release readiness.
- Runtime dependencies remain limited to the Python standard library.

## Testing

Focused tests compare every generated file byte-for-byte across repeated
deterministic compiles and verify explicit timestamp pinning.
