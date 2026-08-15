# Source Discipline

## Required

- Separate facts, assumptions, unknowns, and risks when they affect decisions.
- Preserve exact paths, commands, configuration keys, error messages, and values.
- Verify present-day or external claims before using them as authority.
- Do not promote a claim into public documentation without evidence.

## Evidence grades

Canonical machine vocabulary: `policies/canonical-vocabularies.json`.

- `VERIFIED`: directly observed in code, tests, logs, source documents, trusted external documentation, or reproducible execution evidence.
- `SUPPORTED`: consistent with available evidence but not independently reproduced.
- `ASSUMPTION`: a necessary working assumption that remains unverified.
- `UNKNOWN`: material information is not available.
- `CONFLICTED`: relevant evidence or same-authority sources conflict and require explicit arbitration before the claim can be promoted.

Risk is tracked separately from evidence confidence. A risk may exist at any evidence-confidence level and must not be substituted for `CONFLICTED`.
