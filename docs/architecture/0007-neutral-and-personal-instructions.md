# ADR-0007: Neutral global instructions and private personal overlays

- Status: Accepted
- Date: 2026-07-24
- Owners: Repository maintainers

## Context

Canonical standards must work for any human or AI. Personal workflow preferences remain useful but must not alter neutral policy or leak into reusable packs.

## Decision

Store neutral additive instruction modules under `instructions/global/`. Store optional personal overlays under `instructions/personal/<owner>/`. Compilers exclude personal overlays unless explicitly selected. Personal rules may customize tone and workflow but cannot weaken law, safety, privacy, accessibility, approval, or evidence controls.

## Verification

Automated checks scan neutral modules for personal names and profile-specific language. Precedence tests ensure project and safety requirements outrank personal preferences.
