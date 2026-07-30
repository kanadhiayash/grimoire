# ADR 0017: Deterministic applicability resolution

## Status

Accepted.

## Decision

The applicability resolver evaluates every validated normative registry record
against a validated project manifest. It returns exactly one of `SELECTED`,
`EXCLUDED`, `UNCERTAIN`, or `CONFLICTED` for each record, with the record ID,
version, source provenance, predicate trace, and stable reason codes.

Project facts are the base source. Explicitly activated profiles are resolved
parent-first. Explicitly ordered overlays are then considered. A new fact may
be added, and an identical fact may be repeated. A different value for the
same fact is a conflict: it is recorded and every control whose predicate uses
that fact is `CONFLICTED`. No source silently overrides another source.

A predicate that references a missing fact is `UNCERTAIN`, not `EXCLUDED`.
This prevents a missing material fact from becoming a false non-applicability
claim. An approved exception returns an explicit `EXCLUDED` decision with
`approved_exception` and `review_required`; it retains the original control
ID, version, provenance, and predicate trace. Malformed exceptions conflict
instead of bypassing a control.

The resolver is dependency-free and does not modify Zeref. It does not emit
the pack-level trace, exclusion, conflict artifacts, or explain CLI: those are
owned by Phase 3.4.

## Consequences

- Resolution is reproducible for identical inputs.
- Missing or conflicting facts remain visible for human review.
- Existing 0.5.x pack and CLI behavior remains unchanged until Phase 3.4
  integrates the resolver into the compiler artifacts.
