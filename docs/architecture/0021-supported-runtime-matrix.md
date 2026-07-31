# ADR 0021: Supported Runtime Matrix

- Status: Accepted
- Date: 2026-07-30

## Context

Grimoire 1.0 needs evidence for the dependency-free runtime across actively
supported Python versions and operating systems. The CI-only Draft 2020-12
schema validator has a Linux and CPython 3.12 wheel lock and is not part of the
runtime.

## Decision

The required runtime matrix is:

- Ubuntu latest with Python 3.11, 3.12, and 3.13.
- macOS latest with Python 3.11, 3.12, and 3.13.
- Windows: `NOT_VERIFIED`.

Each required job runs the strict 500-case manifest acceptance, a deterministic
fuzz subset, and the complete dependency-free Grimoire check. It records the
exact Git commit, Python implementation and version, operating system,
architecture, runner metadata, and UTC timestamp as an uploaded artifact.

The Linux CPython 3.12 conformance job remains the independent JSON Schema
validation gate. Runtime matrix jobs do not install third-party packages.

## Windows deferral

Windows is not declared unsupported. It remains `NOT_VERIFIED` because the
current test and evidence surfaces contain POSIX-specific symlink and temporary
path behavior that has not been designed and tested on Windows. Silent skips
or an informational green job would create false support evidence.

Windows can move to `PASS` only through a focused compatibility mission that
defines equivalent filesystem controls, removes platform assumptions, and
passes the complete required matrix without weakening a test.

## Consequences

- Failures on any Ubuntu or macOS matrix combination block the pull request.
- Python 3.14 and later are outside the declared 1.0 support window until added
  by a future compatibility decision.
- Schema-tool portability does not affect the zero-dependency runtime contract.
- This ADR records compatibility evidence, not release assurance.

## Rollback

Revert the matrix workflow, environment writer, tests, and this ADR together.
The prior Linux CPython 3.12 conformance job remains independently functional.
