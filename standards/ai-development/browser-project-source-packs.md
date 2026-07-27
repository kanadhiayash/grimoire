# Browser Project Source Packs

A browser source pack compiles the smallest complete operating context for a project surface.

## Required files

1. `SURFACE_BOOT.md`
2. `SOURCES_MANIFEST.json`
3. `AGENTS.md`
4. `PROVIDER_ADAPTER.md`
5. `ZEREF_OPERATIONS_BRIDGE.md`
6. `PROJECT_STATE.md`
7. `MEMORY_STATE.md`

Project instructions must name this read order. File names alone do not create precedence on browser surfaces.

## Provenance

Each pack records:

- Grimoire live URL and pinned commit;
- Zeref Memory Engine live URL and pinned commit;
- generation timestamp;
- surface and project identifier;
- SHA-256 hash for every managed file;
- freshness budget;
- privacy classification.

Live links establish provenance and may be used for a deliberate refresh check. Uploaded snapshots are the active operating context.

## Memory

Browser projects may stage decisions, risks, conflicts, and memory candidates. They may not claim canonical promotion until an approved writeback is saved into project sources or re-uploaded and a writeback receipt is recorded.

## Refresh

A stale pack reports its age and limitations. It must not silently replace itself with the latest repository content because that would change operating policy without review.

## Portability

Provider adapters may describe source discovery, context limits, or save-to-project mechanics. They may not change command meanings, approval rules, memory lifecycle, completion statuses, or Zeref runtime ownership.
