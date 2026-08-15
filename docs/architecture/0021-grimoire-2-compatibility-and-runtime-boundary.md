# ADR 0021: Grimoire 2.0 compatibility and runtime boundary

## Status

Accepted.

## Context

Grimoire 1.0 has already moved its intended active runtime relationship toward Shiroe, but its universal project-pack and status contracts still contain Zeref-era names and runtime ownership. The current executable compiler emits `ZEREF_EXECUTION_PROFILE.json`, the canonical status model contains `ZEREF_EXECUTION_STATUS`, the project manifest carries `zeref.mode` and `zeref.cost_ceiling`, and the generated AI context states that Zeref routes execution.

Phase 10.3 reproduced those facts directly from the current compiler and status model. Those contracts are valid evidence of the v1 product state, but they cannot remain active universal semantics in Grimoire 2.0 without contradicting ADR 0020 and the current Grimoire/Shiroe ownership boundary.

Grimoire 2.0 therefore needs a breaking compatibility boundary. The migration must preserve the ability to verify old packs without carrying old runtime ownership into new universal output.

## Decision

The target major release is 2.0.0.

Grimoire 2.0 universal outputs use runtime-neutral execution contracts.

Shiroe integration is an adapter and does not make Shiroe behavior part of Grimoire's universal standard model.

Grimoire 1.x packs remain verifiable only through explicit compatibility mode.

The Grimoire 2.0 compiler MUST NOT emit active Zeref filenames, Zeref status dimensions, or Zeref runtime ownership.

Compatibility MUST NOT become the default v2 execution path.

No migration may weaken a Grimoire control.

## Grimoire 2.0 universal execution contract

The v2 universal project pack describes what execution must preserve, prove, stop on, and return without naming or owning a particular runtime.

The universal execution surface MUST represent at least:

- applicable requirement IDs;
- required outcomes;
- required documents and artifacts;
- required gates;
- approval boundaries;
- allowed and forbidden action classes where Grimoire owns that policy;
- evidence requirements;
- verification requirements;
- stop conditions;
- cost or resource limits when they are policy constraints;
- execution status as a runtime-neutral assurance dimension;
- receipt expectations sufficient for independent verification.

The v2 universal profile filename is `EXECUTION_PROFILE.json`. The v2 runtime-neutral execution status dimension is `EXECUTION_STATUS`.

These names describe Grimoire-owned contracts. They do not assert that Grimoire executes work itself.

Grimoire MUST NOT own runtime-specific model selection, tool implementation, skill activation, retry strategy, memory mechanics, or orchestration internals merely to populate the universal profile.

## Shiroe adapter boundary

Shiroe is the preferred current execution and continuity runtime integration for this repository, but it remains external to Grimoire's universal standard model.

The Shiroe adapter MAY translate the runtime-neutral `EXECUTION_PROFILE.json` into Shiroe-readable activation, role, tool, approval, retry, memory, handoff, and receipt inputs. It MAY translate a verified Shiroe receipt back into Grimoire's runtime-neutral evidence model.

The adapter MUST preserve requirement IDs, gates, approval boundaries, evidence requirements, limits, and stop conditions. It MUST NOT weaken a Grimoire control or claim that a Shiroe capability was exercised without evidence.

A project that does not use Shiroe remains able to compile and verify the universal Grimoire contract. Runtime choice is therefore an adapter decision, not a universal standards dependency.

No Shiroe repository modification is required or authorized by this ADR.

## Grimoire 1.x compatibility mode

Grimoire 1.x verification is retained for migration and evidence preservation through an explicit compatibility mode.

The canonical compatibility selector is `compatibility_mode`. A v1/Zeref compatibility request uses the explicit value `v1_zeref`.

A v2 invocation MUST NOT infer compatibility mode from the presence of legacy fields, filenames, directories, prior receipts, or runtime terminology. The caller must select compatibility intentionally or use a versioned v1 verification entrypoint whose behavior is explicitly documented as compatibility behavior.

Compatibility mode MAY read and verify the versioned legacy contracts required to validate an old pack, including:

- `ZEREF_EXECUTION_PROFILE.json`;
- `ZEREF_EXECUTION_STATUS`;
- `zeref.mode`;
- `zeref.cost_ceiling`;
- versioned Zeref execution-receipt fields required by the v1 verifier.

Compatibility mode MUST preserve v1 verification semantics closely enough to detect tampering and invalid legacy evidence. It MUST NOT upgrade a legacy runtime claim into a v2 runtime-neutral claim without a governed mapping and fresh evidence.

## Zeref isolation

Zeref is a legacy compatibility concern in Grimoire 2.0, not active universal runtime ownership.

Active v2 compiler code, active v2 schemas, v2 status dimensions, v2 pack filenames, current runtime instructions, and v2 human guidance MUST NOT use Zeref naming as the universal execution model.

Zeref-specific implementation that remains necessary for v1 verification MUST be isolated behind explicit compatibility boundaries. Compatibility code SHOULD be discoverable as legacy/versioned behavior rather than imported by the default v2 compilation path.

Historical source, audits, benchmark evidence, and release records that contain Zeref terminology remain unchanged unless a separate correction is required for factual integrity. Historical terminology is evidence of the state that existed at the time.

## Breaking changes

Grimoire 2.0 intentionally makes the following breaking changes to the universal contract:

| Grimoire 1.x active contract | Grimoire 2.0 contract | Migration rule |
|---|---|---|
| `ZEREF_EXECUTION_PROFILE.json` | `EXECUTION_PROFILE.json` | Rebuild from canonical Grimoire controls. Do not rename bytes and assume equivalence. |
| `ZEREF_EXECUTION_STATUS` | `EXECUTION_STATUS` | Map only when the evidence semantics are equivalent and independently verifiable. |
| `zeref.mode` | runtime adapter selection or compatibility input | Do not carry into the universal manifest as runtime ownership. |
| `zeref.cost_ceiling` | runtime-neutral policy/resource limit where applicable | Preserve or strengthen the effective limit; never silently drop it. |
| Zeref routes execution in universal context | runtime-neutral execution handoff | Runtime identity belongs to the selected adapter. |
| default imports of Zeref profile behavior | explicit v1 compatibility implementation | Default v2 compilation does not depend on legacy runtime code. |

Aliases are not sufficient migration for these changes. The v2 contract must make the new ownership boundary observable in schemas, compiler output, status reports, documentation, and tests.

## Fail-closed migration rules

Phase 12 MUST implement deterministic compatibility validation in:

`checks/grimoire_2_compatibility_check.py`

with representative fixtures under:

`tests/fixtures/compatibility/`

At minimum, migration and compatibility validation MUST expose stable reason classes for:

- `UNMAPPABLE_LEGACY_CONTROL`: a legacy control or field has no safe v2 equivalent and therefore requires explicit human disposition.
- `AMBIGUOUS_RUNTIME_OWNERSHIP`: a mapping would leave it unclear whether Grimoire or a runtime owns execution behavior.
- `COMPATIBILITY_NOT_EXPLICIT`: legacy behavior is being requested, inferred, or consumed without an explicit allowed compatibility selection.
- `CONTROL_WEAKENING_DETECTED`: the proposed mapping removes, loosens, bypasses, or silently fails to preserve an existing Grimoire gate, limit, approval boundary, evidence requirement, or stop condition.

A failed or ambiguous mapping MUST block migration. It MUST NOT be converted to a warning merely to preserve backward compatibility.

A v1 value that no longer belongs in the universal contract MAY be moved to an adapter-specific input only when its meaning and ownership are explicit. If the migration cannot determine that safely, it returns `UNMAPPABLE_LEGACY_CONTROL` or `AMBIGUOUS_RUNTIME_OWNERSHIP` rather than guessing.

Phase 12 implements this migration contract; Phase 10.3 does not.

## Compatibility sunset

The `v1_zeref` path exists to verify and migrate versioned 1.x evidence, not to provide a permanent alternate architecture for new work.

Compatibility MUST NOT become the default v2 execution path.

New v2 project packs MUST use the runtime-neutral universal contract. A newly created project MUST NOT choose `v1_zeref` merely to avoid v2 migration requirements.

The compatibility path may be removed only after all of the following are true:

1. the supported v1 maintenance window is formally ended through a versioned governance decision;
2. migration tooling and documentation have existed for at least one supported release cycle;
3. retained historical packs remain independently readable or verifiable through an archived versioned verifier or equivalent evidence-preservation mechanism;
4. removal does not destroy required audit, legal, security, or release evidence;
5. the removal is recorded as a breaking change with explicit owner approval.

Until that sunset gate is satisfied, compatibility remains supported but non-default.

## Historical evidence

Historical audits, releases, checksums, receipts, benchmark outputs, and prior packs are immutable evidence of earlier states unless a separately governed integrity correction is required.

Grimoire 2.0 MUST NOT rewrite historical evidence simply to remove Zeref terminology. Doing so would damage provenance and make prior claims harder to reproduce.

A historical artifact MAY be referenced by v2 migration evidence, but it does not become active v2 runtime policy through that reference.

## Compatibility impact

This ADR defines a major-version break. Consumers that parse v1 pack filenames, status dimensions, `zeref` manifest fields, or Zeref-specific execution receipts will need either explicit v1 compatibility verification or migration to the v2 runtime-neutral contract.

Current Grimoire 1.0 behavior remains unchanged by this ADR. The compiler still emits its versioned v1 pack until Phase 12 implements the migration under RED-first verification. Existing 1.x artifacts therefore remain verifiable under their current contracts.

The Shiroe adapter contract can evolve independently as long as it continues to preserve the Grimoire v2 universal execution contract and does not claim unsupported runtime evidence.

## Consequences

Positive consequences:

- Grimoire stops encoding a legacy runtime as a universal standards concept;
- Shiroe can remain the current runtime without coupling all projects to Shiroe internals;
- old packs remain verifiable through an explicit compatibility boundary;
- breaking changes become visible instead of hidden behind aliases;
- future runtimes can integrate without changing universal Grimoire semantics;
- migration can fail closed when a legacy behavior has no safe mapping.

Costs and tradeoffs:

- Phase 12 must separate legacy compatibility code from default v2 compilation;
- schemas, manifest models, status models, compiler output, verifier behavior, documentation, and tests require coordinated versioned migration;
- downstream tooling that expects Zeref-era names must update or select compatibility explicitly;
- compatibility support adds temporary maintenance cost until the sunset gate is satisfied.

## Non-goals

This ADR does not:

- implement the v2 compiler or `EXECUTION_PROFILE.json`;
- remove `ZEREF_EXECUTION_PROFILE.json` from the current v1 compiler;
- remove `ZEREF_EXECUTION_STATUS` from the current v1 status model;
- change current manifest validation;
- delete Zeref compatibility code or historical artifacts;
- modify Shiroe;
- implement Phase 12 compatibility fixtures or checks;
- change `VERSION`;
- create a tag or release;
- publish or deploy anything.
