# Governance

## Canonical authority

This repository is the canonical internal source for Engineering Standards and cross-surface activation policy used by Yash Kanadhia.

Zeref Memory Engine remains the canonical owner of its own runtime, memory, agents, skills, permissions, and boot contract. This repository may detect, activate, simulate, or defer to Zeref but must not silently modify or duplicate Zeref internals.

Consuming repositories and browser source packs pin a released version or exact reviewed commit. They must not silently follow an unversioned branch.

## Change classes

### Patch

Clarifications, typo corrections, non-behavioral documentation changes, and compatible validator fixes.

### Minor

New optional standards, adapters, checks, source-pack formats, activation states, or backward-compatible requirements.

### Major

Breaking policy changes, removed rules, changed instruction precedence, changed command semantics, changed memory lifecycle, or requirements that invalidate existing project manifests or source packs.

## Required process for material changes

1. Create a dedicated branch.
2. Explain the problem and intended outcome.
3. Record affected standards, policies, profiles, adapters, templates, and surfaces.
4. Update tests before or with implementation.
5. Include migration guidance where compatibility changes.
6. Open a draft pull request.
7. Run all required checks.
8. Verify that protected external repositories remain unchanged.
9. Update `CHANGELOG.md` and `VERSION` only when releasing.

## Cross-surface requirements

A new or changed surface adapter must:

- preserve the AI operations command meanings;
- preserve the autonomy and approval model;
- classify runtime versus simulation truthfully;
- emit an activation receipt;
- pin canonical sources;
- preserve source-pack integrity and freshness metadata;
- stage browser memory instead of claiming canonical promotion;
- document unsupported capabilities;
- pass adversarial conformance tests.

An adapter must not:

- create a second command registry;
- claim Zeref runtime execution without evidence;
- modify the Zeref repository;
- silently refresh policy to a new revision;
- weaken security, privacy, accessibility, approval, or verification controls.

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
