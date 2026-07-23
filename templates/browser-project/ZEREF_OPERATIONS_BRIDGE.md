# Zeref Operations Bridge

This bridge maps Engineering Standards operations onto a source-backed browser session. It does not reproduce Zeref internals.

- `ACTIVATE`: load state, sources, conflicts, open work, and first safe action.
- `INGEST`: inventory sources, provenance, freshness, conflicts, and missing files.
- `RESUME`: reconstruct the latest verified state from project sources.
- `AUDIT`: perform read-only evidence, contradiction, risk, and gap analysis.
- `PLAN`: produce plan ID, revision, scope, non-goals, checks, risks, and approval boundary.
- `FAIRYTALE`: approve only the latest unchanged identified plan revision.
- `EXECUTE`: perform only the approved bounded action supported by the active surface.
- `VERIFY`: report checks, results, coverage, limitations, and completion status.
- `ETHERIOUS`: produce a cross-surface handoff.
- `PARK`: record scope, reason, and revisit trigger without planning or execution.
- `PROMOTE MEMORY`: prepare a candidate; persistence requires approved writeback and a receipt.
- `HALT`: stop affected mutations and report the smallest recovery path.

The actual Zeref runtime command set remains owned by Zeref Memory Engine.
