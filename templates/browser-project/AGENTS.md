# Project Agent Contract

This project is governed by Grimoire and uses Zeref Memory Engine as the referenced continuity system.

Canonical sources:
- Grimoire: https://github.com/kanadhiayash/grimoire
- Zeref Memory Engine: https://github.com/kanadhiayash/zeref-memory-engine

Use the pinned revisions and hashes in `SOURCES_MANIFEST.json`.

## Required behavior

- Read before acting.
- Separate facts, assumptions, unknowns, risks, and conflicts when material.
- Make the smallest complete change.
- Preserve security, privacy, accessibility, tests, and quality gates.
- Bind approval to one named plan and revision.
- Verify current or unstable claims.
- Report exact evidence and one completion status: `PASS`, `PARTIAL`, `BLOCKED`, or `NOT_VERIFIED`.
- Never claim tools, agents, runtime execution, persistence, or independent review that did not occur.

## Browser boundary

When this pack is loaded in a browser project or chat, operate in the simulation state selected by `SURFACE_BOOT.md`. Do not claim local Zeref runtime execution or canonical memory promotion.
