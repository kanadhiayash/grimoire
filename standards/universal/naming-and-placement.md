# Naming and Placement Conventions

## Purpose

Provide stable, searchable names without forcing one language or platform to violate its native conventions.

## Repository directories

Use lowercase kebab-case for policy and documentation directories. Place content by responsibility, not by author or temporary status.

## Stable record identifiers

- Architecture decision: `ADR-0001-short-title.md`
- Product or operational decision: `DEC-YYYYMMDD-short-title.md`
- Assumption: `ASM-YYYYMMDD-short-title.md`
- Risk: `RSK-YYYYMMDD-short-title.md`
- Research: `RES-YYYYMMDD-short-title.md`
- Experiment: `EXP-YYYYMMDD-short-title.md`
- Incident: `INC-YYYYMMDD-short-title.md`
- Postmortem: `PM-INC-YYYYMMDD-short-title.md`

Do not place mutable priority, status, or owner values in filenames.

## Exported artifacts

Use `[scope]_[subject]_[type]_[state]_[owner]_[yyyy-mm-dd]_v[major.minor].ext` when governance metadata must travel with an exported file.

## Source code

Use universal semantic rules plus the official language or framework overlay plus a documented repository-local exception. Do not impose one identifier style across Swift, Kotlin, Python, Go, TypeScript, Figma, or other environments.

## Git

Branches:

```text
feat/<scope>__<description>
fix/<scope>__<description>
docs/<scope>__<description>
refactor/<scope>__<description>
ci/<scope>__<description>
```

Commits use Conventional Commits: `<type>(<scope>): <description>`.

## Figma and design tokens

Use nested semantic groups rather than dotted token names:

```text
color/primitive/blue/600
color/semantic/text/primary
color/component/button/primary/background/default
space/scale/200
type/body/md/font-size
motion/duration/fast
```

Token layers are Primitive, Semantic, Component, and Platform Output. Component and variant names use clear nouns and explicit state or size properties. Avoid names based on temporary visual appearance when a semantic purpose exists.
