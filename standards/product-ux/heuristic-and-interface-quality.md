# Heuristic and Interface Quality Standard

## Purpose

Convert vague interface-quality requests into testable product and UX requirements.

## Expected outcome

Every interface has clear hierarchy, predictable behavior, complete states, accessible interaction, platform-appropriate patterns, specific content, and reviewable evidence.

## Applicability

Applies to user-facing web, mobile, desktop, conversational, voice, embedded, and administrative interfaces.

## Non-applicability

Pure machine-to-machine services still require operator and error surfaces where humans administer or troubleshoot them.

## Required inputs

- User goals and task criticality
- Platform and device context
- Design-system inventory
- Content and localization constraints
- Accessibility profile
- Performance and network assumptions

## Unknowns to resolve

Primary action, user expertise, recovery expectations, destructive actions, empty-data behavior, and degraded-service behavior.

## Required actions

Review visibility of system status, match with user language, user control, consistency, error prevention, recognition over recall, efficiency, focus, recovery, and help. Define default, hover, focus, pressed, selected, disabled, loading, empty, partial, offline, permission, error, success, and destructive-confirmation states where applicable.

## Required decisions

Information order, primary and secondary actions, navigation model, disclosure depth, content priority, responsive behavior, and state ownership.

## Required details

Typography roles, spacing rhythm, alignment, contrast, target size, focus order, keyboard behavior, motion, truncation, validation timing, confirmation, undo, and analytics boundaries.

## Expected documents and artifacts

User flow, state matrix, content specification, accessibility requirements, design QA report, and implementation handoff.

## Document structure

Each artifact identifies actors, task, entry, paths, states, content, accessibility, data, analytics, evidence, risks, and owner.

## Acceptance criteria

- The primary task is discoverable.
- Every material state has intended behavior.
- The interface works with keyboard and assistive technologies where applicable.
- Destructive actions provide prevention or recovery.
- Content is specific and not placeholder evidence.
- Platform and design-system conventions are followed or exceptions are recorded.

## Verification method

Heuristic review, accessibility review, representative-device review, content review, visual comparison, and usability testing when risk warrants it.

## Evidence required

Annotated design, state matrix, screenshots or recordings, accessibility results, test notes, and unresolved findings.

## Failure conditions

Missing recovery paths, inaccessible interaction, contradictory actions, invented validation, incomplete states, or presentation treated as proof of usability.

## Risks and abuse cases

Manipulative choice architecture, accidental purchase or deletion, inaccessible controls, deceptive urgency, hidden costs, and silent data collection.

## Guards and limits

Do not equate visual polish with product quality. Do not hide required information or make refusal materially harder than acceptance.

## Exceptions

Record the unmet criterion, user impact, compensating control, owner, approval, and review date.

## Cost considerations

Balance state completeness and testing depth against task risk. Do not reduce critical-state coverage to save design or token cost.

## Dependencies

Accessibility, content, design-system, privacy, performance, and platform overlays.

## Related standards

Product Design Operations, Global Legal Control Plane, and Design Development Handoff.

## Source provenance

Use reviewed usability, platform, accessibility, and regulator sources through the source registry.

## Owner and review cycle

Product UX owner. Review when platform guidance, user evidence, or design-system behavior changes.

## Zeref execution behavior

Route design review to a product-design lead with accessibility support when risk warrants it. Stop at missing user need or unsupported validation claims.

## Examples

A payment flow defines review, validation, failure, retry, cancellation, receipt, and support paths.

## Anti-patterns

A polished happy path with no errors, recovery, keyboard behavior, or evidence.
