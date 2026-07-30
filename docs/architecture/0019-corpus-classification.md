# ADR 0019: Explicit corpus classification

## Status

Accepted.

## Decision

`inventory/standards-classification.json` assigns one explicit classification,
domain, owner, review status, and migration target to every Markdown document
under `standards/`. The inventory is checked against the filesystem and the
machine registry on every conformance run.

Only a document classified `NORMATIVE` and linked to a current registry record
is eligible for automatic compilation. `LEGACY_NORMATIVE` preserves prior
enforceable content for migration but is not a second compilation source.

The inventory keeps the existing five registry-backed standards available while
the remaining legacy documents migrate in their dedicated domain issues. The
four stack overlay documents remain explicitly non-compilable with an
`ADR_REQUIRED_STACK_OVERLAYS` target because the approved Phase 4 map has no
stack-overlay migration lane. `security-red-team.md` is classified as
defensive-only legacy content; this does not authorize offensive activity.
