# Grimoire 2.0 Operational Baseline

## Objective

Freeze the exact Grimoire 1.0 repository state used to begin the Grimoire 2.0 hardening program and record accepted operational debt without rewriting historical audits or prematurely implementing later phases.

## Baseline identity

- Audit date: `2026-08-15`
- Baseline branch: `main`
- Baseline commit: `dcc1017757d53615b29921967e6a9afd08fee38a`
- Repository release at baseline: `1.0.0`
- Repository: `kanadhiayash/grimoire`
- GitHub-observed repository visibility on audit date: `public`
- Historical audit records: preserved unchanged

## Evidence method

The baseline uses repository files at the exact baseline commit plus read-only GitHub repository metadata. Findings are recorded in `FINDINGS.json` with stable IDs, severity, affected release gate, evidence, owner, remediation phase, and close condition.

The Phase 10.1 RED test was committed separately before the implementation artifacts existed. Exact RED commit:

`ce7e0ae679dbadc61f9a74d063f1126850a49c3d`

GitHub Actions Grimoire CI run `31874732832` reproduced the expected failures. The runtime-matrix jobs failed at `python scripts/grimoire.py check` because the finding register/schema were absent and repository visibility still read `private` instead of the observed `public` state. The RED test also confirmed that active Zeref-era references remain, normative authoring completeness is not enforced corpus-wide, four stack overlays remain migration-required, and no `official_source` record exists under `registry/sources/` at the baseline commit.

## Finding register summary

`FINDINGS.json` contains 20 accepted baseline findings:

- P1: 13
- P2: 6
- P3: 1
- P0: 0

Status after the Phase 10.1 metadata correction:

- CLOSED: 1
- OPEN: 19
- ACCEPTED_RISK: 0
- NOT_APPLICABLE: 0

`GRM2-P10-001` is the only finding closed in Phase 10.1. It covers the factual repository visibility mismatch. All structural findings remain OPEN for their assigned later phases.

## Current facts

- Grimoire 1.0 already has an executable dependency-free Python control plane, registry, applicability resolver, compiler, verifier, benchmark/evidence system, and GitHub Actions conformance workflow.
- The intended current runtime boundary names Shiroe, but active universal and compatibility-era surfaces still contain Zeref naming that must be isolated in the 2.0 migration.
- `standards/universal/standard-authoring.md` requires 25 sections for every normative standard, while multiple current normative Markdown documents do not contain those sections and current repository checks still pass.
- Four stack documents are classified `LEGACY_NORMATIVE` with `MIGRATION_REQUIRED`.
- The current foundation source registry is made of local-policy source records. It does not yet provide the planned adopted official-source authority layer.
- Windows is not part of the required baseline CI matrix.

## Assumptions

- Grimoire 2.0 preserves the dependency-free runtime contract unless a separately approved ADR changes it.
- Historical audits remain evidence and are not rewritten to match later architecture.
- Shiroe remains a separate execution runtime. Grimoire 2.0 will define requirements and a runtime-neutral execution contract rather than duplicate Shiroe internals.
- The 2.0 program executes through ordered child issues, one focused branch and pull request per child mission.

## Unknowns

The following are intentionally not claimed by Phase 10.1:

- final Grimoire 2.0 schema design;
- current official-source adoption completeness;
- Windows compatibility;
- Python 3.14 compatibility;
- real current Shiroe v2 round-trip evidence;
- final 2.0 benchmark thresholds or results;
- final source freshness state;
- final work-type coverage state.

These require later implementation and fresh verification.

## Risks

- Treating this baseline register as remediation would create a false completion claim. Nineteen findings remain OPEN after Phase 10.1.
- Updating standards before the canonical requirement model is locked could create more human/machine drift.
- Updating Zeref names before the compatibility/runtime-boundary ADR is approved could break 1.x verification semantics.
- Adding official-source records before the v2 source/currentness contract is defined could preserve the same provenance ambiguity under a new format.

## Intentionally untouched scope

Phase 10.1 does not:

- change `VERSION`;
- rewrite standards or work-type coverage;
- change the project pack contract;
- change Zeref/Shiroe runtime behavior;
- migrate compatibility code;
- add official external sources;
- change source review cadence;
- add Windows or Python 3.14 CI;
- modify Shiroe;
- create a tag, release, deployment, or publication.

## Phase 10.1 completion contract

This mission is complete only when:

1. the finding register validates through a dependency-free repository check;
2. repository visibility metadata matches observed GitHub state;
3. all structural findings remain explicitly OPEN;
4. focused and full exact-head CI pass on the implementation commit;
5. the pull request diff contains only the approved Phase 10.1 scope;
6. the pull request is reviewed and merged through the repository approval boundary;
7. merge-commit CI is verified before Phase 10.2 begins.

The Grimoire 2.0 release remains ineligible at this stage.
