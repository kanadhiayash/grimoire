# Contributing

## Before changing policy

1. Read `AGENTS.md`.
2. Run `make check`.
3. Identify the exact rule or gap being changed.
4. Determine whether the change is patch, minor, or major.
5. Create a focused branch.

## Branch naming

```text
feat/<scope>__<description>
fix/<scope>__<description>
docs/<scope>__<description>
refactor/<scope>__<description>
ci/<scope>__<description>
```

## Commit format

Use Conventional Commits:

```text
<type>(<scope>): <description>
```

## Pull request requirements

A material policy pull request must include:

- Problem and scope
- Policy behavior before and after
- Compatibility impact
- Evidence and sources
- Tests and commands run
- Migration notes when required
- Remaining risks

## Verification

Run:

```bash
make check
```

Do not merge while required checks fail.
