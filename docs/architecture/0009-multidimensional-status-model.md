# ADR 0009: Multidimensional Status Model

- Status: Accepted
- Date: 2026-07-27
- Plan: `GRM-1.0-P0P1-2026-07-27`, revision 1

## Context

Grimoire 0.5.x used one compiler `status` value for several different claims. A
successfully generated pack could therefore be reported as `PASS` even when no
project-readiness, release, legal-review, control, applicability, or Zeref
execution evidence had been supplied.

## Decision

Grimoire records eight independent status dimensions:

1. `PACK_GENERATION_STATUS`
2. `MANIFEST_VALIDATION_STATUS`
3. `APPLICABILITY_STATUS`
4. `CONTROL_VERIFICATION_STATUS`
5. `PROJECT_READINESS_STATUS`
6. `RELEASE_ASSURANCE_STATUS`
7. `LEGAL_REVIEW_STATUS`
8. `ZEREF_EXECUTION_STATUS`

Each dimension uses only `PASS`, `PARTIAL`, `BLOCKED`, or `NOT_VERIFIED` and
includes stable machine-readable reason codes. The aggregate is conservative:

```text
BLOCKED > NOT_VERIFIED > PARTIAL > PASS
```

Pack generation can be `PASS` while the aggregate remains `NOT_VERIFIED`.
Automated `COMPLIANT` is not part of the completion vocabulary and is rejected.

## Boundaries and state ownership

The project compiler owns pack-generation and current manifest-check results. It
does not infer project, release, legal, control, applicability, or Zeref
assurance from pack creation. Those dimensions remain `NOT_VERIFIED` until their
respective engines consume explicit evidence.

The status model is an immutable standard-library value layer under
`src/grimoire/status.py`. `PROJECT_STATUS.json` and `EXECUTION_RECEIPT.json`
serialize the same report, with schemas under `policies/schemas/`.

Additional source, conflict, and document-readiness dimensions are deferred
until engines exist that can establish those claims.

## Data flow

```text
manifest and supplied evidence
  -> dimension-specific StatusResult values
  -> complete StatusReport
  -> conservative aggregate
  -> project status and execution receipt
```

## Compatibility

The 0.5.x CLI entrypoints and twelve generated filenames remain available.
Existing scalar `status` fields remain present but now contain the conservative
aggregate. `pack_generation_status` preserves the narrower generation outcome.

Dimensionless legacy values are migrated conservatively: `BLOCKED` remains
`BLOCKED`; `PASS`, `PARTIAL`, and `NOT_VERIFIED` become `NOT_VERIFIED`.

## Testing strategy

Tests require the exact eight dimensions, precedence ordering, conservative
legacy mapping, rejection of `COMPLIANT`, schema closure, and the audited
false-readiness fixture changing from `PASS` to `NOT_VERIFIED`.

## Tradeoffs

Consumers that treated scalar `PASS` as pack-generation success must migrate to
`pack_generation_status`. This intentional conservatism prevents one successful
operation from becoming an unsupported broader assurance claim.
