# ADR 0020: Zeref Profile and Receipt Trust

## Status

Accepted for the Grimoire 1.0 contract boundary.

## Context

Grimoire must bind a generated standards pack to one project commit, approved
plan, revision, scope, tool boundary, approval boundary, and expected receipt.
The profile itself is part of the final pack, so hashing the entire directory
from inside the profile would create a recursive and unstable value.

Zeref is a separate continuity and execution-routing layer. Grimoire must not
copy its routing, memory, skill, or model-selection implementation.

## Decision

Profile v2 uses `sha256-framed-pack-v1`. It hashes an explicit, sorted domain of
thirteen pre-profile artifacts. Each filename and content value is
length-prefixed before hashing. The profile and the pack-generation receipt are
excluded from this domain, preventing recursive self-binding. The final
pack-generation receipt separately hashes the profile.

Plan binding is supplied as an explicit compiler input. It is not inferred from
project prose or fabricated for legacy manifests. A compiler call without this
input continues to emit the compatible profile v1 and leaves Zeref execution
`NOT_VERIFIED`.

Profile v2 defines constraints and evidence requirements only. Zeref or the
active harness owns actual role, model, tool, retry, and memory operations.

## Integrity and trust

- SHA-256 proves content integrity, not author identity.
- A future signed release envelope may add identity and provenance without
  changing the profile hash domain.
- Missing or ambiguous plan, project, scope, tool, or approval data fails
  profile construction.
- The receipt expiry is bounded between 60 seconds and 24 hours.
- A receipt may prove Zeref execution only. It cannot raise project readiness,
  release assurance, accessibility, security, or legal status without their
  own evidence.

## Compatibility

The existing profile v1 schema and compiler output remain available when no
explicit plan binding is supplied. Consumers opt into v2 by supplying the
versioned contract input.

## Testing

Tests cover missing bindings, weakened approval limits, conflicting tools,
stable pack hashing, deterministic profile bytes, and compiler integration.
