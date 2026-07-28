# ADR 0015: Independent Project Pack Verification

## Status

Accepted.

## Context

Compiler success is not verification evidence. A generated project pack needs an
independent check that can be run later against pack contents without trusting
the compile operation that produced it.

## Decision

Grimoire provides a project-pack verifier that checks the required file set,
receipt JSON, recorded artifact hashes, source manifest timestamp, future
timestamps, and unexpected files. The unified CLI exposes this as
`python3 scripts/grimoire.py project verify --directory <pack>`.

Offline mode can verify local artifact integrity but must report remote source
authenticity as `NOT_VERIFIED`.

## Boundaries

- Verification does not reuse compiler success as assurance evidence.
- Offline verification does not claim connected source authenticity.
- Connected and release verification remain conservative until their source
  checks are implemented.
- Runtime dependencies remain limited to the Python standard library.

## Testing

Focused verifier tests cover valid packs, tampered artifacts, unexpected files,
future timestamps, offline authenticity status, and machine-readable CLI output.
