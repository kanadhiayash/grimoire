# Minimum Correct Change

## Purpose

Produce the smallest complete, maintainable, and verified implementation that satisfies the locked product, design, architecture, security, privacy, accessibility, legal, operational, and cost contract.

## Required sequence

1. Confirm the active approved plan and revision.
2. Read the actual code path and local standards before editing.
3. Determine whether the behavior already exists.
4. Reuse existing architecture, components, utilities, and approved dependencies.
5. Prefer standard-library, framework-native, and platform-native capabilities.
6. Identify the correct ownership layer.
7. Make the smallest complete change at that layer.
8. Add the smallest runnable verification proving the behavior.
9. Remove avoidable duplication or configuration only when within scope.
10. Stop when acceptance criteria pass.

## Guards

Minimalism must not remove authentication, authorization, trust-boundary validation, data protections, accessibility, auditability, observability, transaction integrity, concurrency correctness, resilience, legal obligations, user requirements, or required tests.

## Modes

- `advisory`: recommend the simpler path without blocking.
- `standard`: enforce reuse, native-first behavior, bounded diffs, and verification.
- `strict`: require justification for new abstractions, dependencies, files, or complexity.
- `off`: disable this discipline only; safety and approval rules remain active.

## Evidence

Record files changed, lines added and removed, dependencies added or avoided, components reused, tests added and run, token and API use when available, execution time when measured, and remaining risk. Do not invent measurements.
