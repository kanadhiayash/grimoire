# Governance

## Canonical authority

This repository is the canonical internal source for engineering standards used by Zeref OS projects.

Consuming repositories pin a released version. They must not silently follow an unversioned branch.

## Change classes

### Patch

Clarifications, typo corrections, non-behavioral documentation changes, and compatible validator fixes.

### Minor

New optional standards, adapters, checks, or backward-compatible requirements.

### Major

Breaking policy changes, removed rules, changed instruction precedence, or requirements that invalidate existing project manifests.

## Required process for material changes

1. Create a dedicated branch.
2. Explain the problem and intended outcome.
3. Record affected standards, policies, profiles, and adapters.
4. Update tests before or with implementation.
5. Include migration guidance where compatibility changes.
6. Open a pull request.
7. Run all required checks.
8. Update `CHANGELOG.md` and `VERSION` when releasing.

## Exceptions

Projects may define exceptions only in:

```text
docs/standards-exceptions.md
```

Each exception must include:

- Rule being excepted
- Scope
- Reason
- Risk
- Compensating control
- Owner
- Review date
- Expiry or removal condition

Undocumented exceptions are violations.

## Legacy repositories

The following repositories are migration sources, not canonical authority:

- `project-practices`
- `github-velocity-practices`
- `development-architecture-practices`
- `design-system-practices`

Keep them unchanged until migration verification is complete.
