# Design Token and Figma Conventions

## Purpose

Keep design decisions consistent, semantic, accessible, and portable from Figma to implementation.

## Expected outcome

Tokens and components have stable semantic names, explicit modes and states, traceable code outputs, and no duplicate source of truth.

## Applicability

Applies to shared visual foundations, component libraries, themes, responsive modes, and design-to-code handoff.

## Non-applicability

One-off exploratory artifacts may use temporary local styles but cannot be represented as the canonical design system.

## Required inputs

Brand foundations, accessibility constraints, platform outputs, supported modes, component inventory, and naming overlays.

## Unknowns to resolve

Canonical token source, supported themes, platform transformations, ownership, release process, and deprecation policy.

## Required actions

Use Primitive, Semantic, Component, and Platform Output layers. Use nested names such as `color/semantic/text/primary`. Alias semantic and component tokens to primitives. Define state, size, density, theme, and platform dimensions explicitly. Map every published Figma token or component to implementation output or mark it design-only.

## Required decisions

Canonical source, collection and mode boundaries, alias strategy, code generation, fallback, versioning, contribution, and deprecation.

## Required details

Color, typography, spacing, sizing, radius, border, elevation, icon, motion, breakpoint, content, and accessibility behavior.

## Expected documents and artifacts

Token taxonomy, Figma library map, component anatomy, variant matrix, code mapping, release notes, migration guide, and parity report.

## Document structure

Each component records purpose, anatomy, properties, states, content, responsive behavior, accessibility, tokens, code mapping, tests, and owner.

## Acceptance criteria

- No dotted token names are used as canonical DTCG names.
- Semantic tokens are not named only by appearance.
- Modes and variants are bounded and non-duplicative.
- Contrast and motion requirements are verifiable.
- Published design and code mappings are versioned.

## Verification method

Token linting, alias-resolution check, unused and duplicate-token review, Figma-to-code parity review, visual regression, and accessibility testing.

## Evidence required

Export, generated output, parity report, screenshots, test results, and release record.

## Failure conditions

Circular aliases, inaccessible values, hidden local styles, duplicate canonical sources, ambiguous variants, or code and design drift.

## Risks and abuse cases

Token explosion, brand overrides that break accessibility, generated-code drift, and component variants used to hide inconsistent patterns.

## Guards and limits

Do not combine app icon and app logo when the product contract calls for one. Do not create a token for every raw value without a reuse or semantic need.

## Exceptions

Record temporary value, scope, reason, replacement plan, owner, and expiry.

## Cost considerations

Prefer reusable semantic systems over large generated token sets that increase review, build, and context cost.

## Dependencies

Accessibility, brand, platform, component, and release standards.

## Related standards

Naming and Placement, Product Design Operations, and Design Development Handoff.

## Source provenance

Pin the adopted Design Tokens Community Group format and platform guidance in the source registry.

## Owner and review cycle

Design-system owner with engineering counterpart. Review at every library release.

## Zeref execution behavior

Use design-system and platform overlays, validate names before generation, and emit a parity report. Stop on conflicting canonical sources.

## Examples

`color/component/button/primary/background/default` aliases `color/semantic/action/primary`.

## Anti-patterns

`blueButton`, `component.button.primary`, or multiple unversioned token exports.
