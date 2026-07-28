# ADR 0013: Inert Project Context Rendering

## Status

Accepted.

## Context

Project manifests are operator-supplied data. Their text can describe a product,
but it must not become executable AI guidance, approval, evidence, or a status
claim inside generated packs.

## Decision

Generated `AI_CONTEXT.md` separates trusted Orchestrator instructions from
project-supplied manifest values. Manifest values are rendered in an indented,
JSON-shaped block labeled `UNTRUSTED_PROJECT_DATA`.

Trusted sections may summarize derived counts and required outcomes, documents,
and gates, but they must not directly interpolate project-supplied strings.

## Boundaries

- Manifest values remain observable.
- Markdown inside project values cannot escape the inert data block.
- Control and format characters are rejected by the renderer.
- This does not certify project truth, legal status, release readiness, or Zeref
  execution.

## Testing

Focused context rendering tests cover instruction-like text, Markdown escape
attempts, renderer limits, and project compiler compatibility.
