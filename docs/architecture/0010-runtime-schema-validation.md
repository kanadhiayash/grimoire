# ADR 0010: Runtime and CI Schema Validation Boundary

- Status: Accepted
- Date: 2026-07-27
- Plan: `GRM-1.0-P0P1-2026-07-27`, revision 1

## Context

Grimoire's runtime is portable Python 3.11+ standard-library code. JSON Schema
Draft 2020-12 provides an independent machine-contract check, but adding a
validator to runtime would change that portability contract.

The 0.5.0 AI Operations schema also contained a contradiction: required command
and autonomy keys were forbidden because their parent objects had
`additionalProperties: false` without corresponding `properties`.

## Decision

Runtime remains dependency-free. CI installs `jsonschema==4.26.0` and its five
transitive packages from `requirements/ci-schema.txt` using exact versions,
wheel-only installation, `--no-deps`, `--require-hashes`, and one reviewed hash
per CPython 3.12 Linux x86_64 distribution.

CI then runs `checks/json_schema_check.py` before the dependency-free Grimoire
check. The independent checker:

1. requires exactly `jsonschema==4.26.0`;
2. checks every repository schema against the Draft 2020-12 metaschema;
3. validates the current AI Operations policy;
4. proves valid fixtures pass; and
5. proves invalid mutation fixtures fail for their intended validator and path.

No runtime module or command imports `jsonschema`.

## Contract boundaries

Finite objects have explicit properties and reject unknown fields. Commands and
autonomy levels have exact named records. Command and approval alias maps remain
extensible maps because their keys are user-facing aliases; their values remain
constrained.

Open string vocabularies are not converted to enums in this change. Doing so
would be a separate policy-version decision.

## Data flow

```text
hashed CI-only lock
  -> external Draft 2020-12 validator
  -> schema metaschema checks
  -> policy and fixture validation
  -> dependency-free Grimoire check
```

## Compatibility

The policy document and runtime command surface are unchanged. The corrected
schema accepts the current policy and rejects missing, extra, or malformed
command and autonomy records.

## Tradeoffs

The lock is intentionally specific to the current GitHub Actions environment.
A Python or runner-platform change requires a separately generated and reviewed
lock update. Hashes prove downloaded bytes match the reviewed distributions;
they do not replace package-source review.

The dependency update owner is the Grimoire maintainer. Review is required when
the Python CI version, runner OS, validator version, or any transitive version
changes.
