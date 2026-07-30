# ADR 0018: Complete control trace evidence

## Status

Accepted.

## Decision

Every project pack now contains one `CONTROL_TRACE.json` entry for every
loaded normative registry record. Each entry includes the record ID, version,
state, reason codes, predicate trace, source provenance, missing-fact paths,
and review requirement. The pack also emits `EXCLUSIONS.json` and
`CONFLICT_REPORT.json`.

`APPLICABILITY_STATUS` is `PASS` only when every loaded record is resolved and
no source conflict remains. It is `NOT_VERIFIED` for unresolved material facts
and `BLOCKED` for a conflicting source or control. This status does not imply
control verification, legal review, release assurance, or project readiness.

`python3 scripts/grimoire.py project explain --directory PACK --standard-id
GRIM-STD-0001 --json` reads the stored trace. Its error contract uses only
machine codes and does not echo untrusted CLI values or raw manifest data.

The independent pack verifier checks the complete file set, receipt hashes,
and trace structure. The runtime remains dependency-free and no Zeref internals
are changed.
