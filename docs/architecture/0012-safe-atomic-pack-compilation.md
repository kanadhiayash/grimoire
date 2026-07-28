# ADR 0012: Safe Atomic Pack Compilation

## Status

Accepted.

## Context

Generated Grimoire packs are assurance artifacts. A compiler that writes directly
into the final output directory can leave stale files, partial files, or a
modified prior pack when compilation fails. Output paths are also untrusted
operator input and must not redirect writes through a symlinked final directory.

## Decision

Pack compilers must write into a temporary directory owned by the compiler,
validate the complete declared file set, then promote the temporary directory to
the requested output path. Existing packs are replaced as a complete directory
only after the new pack validates.

The runtime implementation remains Python standard library only.

## Boundaries

- Symlinked final output paths are rejected before writing.
- Child paths must resolve inside the declared output root.
- Unexpected or missing generated files fail compilation.
- Failed builds leave the prior output directory unchanged.
- This layer does not certify remote source authenticity or release readiness.

## Testing

The acceptance surface is covered by focused filesystem tests and existing
project compiler compatibility tests. Verification requires the full Grimoire
check before merge.
