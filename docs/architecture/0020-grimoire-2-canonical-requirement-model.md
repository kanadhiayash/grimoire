# ADR 0020: Grimoire 2.0 canonical requirement model

## Status

Accepted.

## Context

Grimoire 1.0 contains both machine normative records and human Markdown standards. The repository currently verifies that normative Markdown is classified and linked to a machine registry record, but it does not universally prove semantic parity between the two surfaces.

Phase 10.2 reproduced this gap with `GRIM-STD-0012` and `standards/engineering/testing.md`. The registry record is accepted as normative and contains a machine contract, while the linked human document does not render the complete current standard-authoring contract. Existing checks can therefore accept a state in which human and machine normative surfaces differ in structure or semantics.

Grimoire 2.0 needs one authoritative local representation of requirements so compilers, humans, AI systems, reviewers, and runtime adapters cannot choose between competing sources of truth.

This decision applies to normative requirements compiled or evaluated by Grimoire. Repository bootstrap and governance authorities such as `AGENTS.md`, `GOVERNANCE.md`, `SECURITY.md`, and accepted architecture decisions retain their declared precedence and constrain the machine model. Phase 11 must make machine policy conform to those authorities rather than silently replacing them.

## Decision

Grimoire 2.0 uses an authored-once, rendered-many requirement model.

Machine registry and policy records are the canonical local normative authority.

Human-readable standards are generated views or parity-enforced views of those canonical records. External official sources remain separate authority records until a governed local adoption maps them into Grimoire requirements. Runtime adapters translate applicable requirements for an execution surface but do not own or alter normative meaning.

The repository MUST fail closed when canonical machine requirements and a required human rendering cannot be proven to agree.

## Machine normative authority

Machine registry and policy records are the canonical local normative authority.

For every active normative requirement, the canonical machine layer MUST own or reference the information required to determine at least:

- stable requirement identity;
- record kind and version;
- requirement modality;
- domain and applicability;
- expected outcomes;
- required actions and decisions;
- expected documents or artifacts;
- acceptance criteria;
- verification method;
- evidence requirements;
- failure conditions;
- exceptions and limits;
- provenance and adopted source mappings;
- owner, review state, and supersession state.

The exact closed schema by record kind is a Phase 11 implementation decision constrained by this ADR. Phase 10.2 does not authorize an incomplete universal schema merely to make the current corpus conform.

A requirement MUST have one canonical machine owner. Other machine surfaces MAY reference or project the requirement by stable ID, but MUST NOT redefine its normative semantics independently.

`AGENTS.md`, governance, security, privacy, legal authority, and accepted architecture decisions continue to constrain the canonical machine layer through the repository source-of-truth order. If a machine record conflicts with a higher authority, the machine record does not override that authority.

## Human rendering and parity

Human Markdown MUST NOT introduce, weaken, remove, or override normative semantics independently.

Grimoire 2.0 permits two human-rendering modes for active normative requirements:

1. `GENERATED`: the human document or normative section is deterministically rendered from the canonical machine record.
2. `PARITY_ENFORCED`: human-authored explanatory Markdown is permitted, but every normative statement is traceable to canonical requirement IDs and automated checks prove the required parity properties.

Human documents MAY add rationale, examples, navigation, diagrams, explanatory prose, or implementation guidance when those additions are clearly non-normative and do not contradict canonical requirements.

Human documents MUST NOT silently change requirement modality, applicability, acceptance, evidence, gate effect, exception conditions, or ownership. A hand-authored human requirement without a canonical machine owner is invalid for the active v2 normative corpus.

If semantic parity cannot be established for an active normative requirement, that requirement MUST NOT be treated as fully verified for v2 compilation or release eligibility.

The current 25-section authoring contract must be reconciled with the Phase 11 record-kind model. This ADR does not require every future record kind to carry identical human boilerplate. It requires each active normative record kind to have a complete closed machine contract and an explicit human-rendering contract.

## Official-source authority

Official external sources are authority records, not local controls until adopted through governed mapping.

An official-source record represents an external authority such as law, regulator guidance, an official platform specification, or a standards body publication. Its existence in the source registry does not by itself create a local Grimoire requirement.

A local normative requirement derived from an external source MUST use a governed adoption mapping that preserves source identity, authority class, version or revision, applicability, effective state where relevant, local interpretation, and review responsibility.

Local policy MUST NOT impersonate external authority. A local Grimoire standard may be a canonical local requirement, but it is not an `official_source` merely because it was reviewed internally.

Source freshness, supersession, effective dates, and risk-sensitive review cadence are implemented in later phases. This ADR fixes the authority boundary those systems must preserve.

## Runtime adapters

Runtime adapters are non-authoritative translations and MUST NOT alter requirement modality, scope, gates, or evidence.

Adapters MAY transform canonical requirements into bounded execution instructions, context packs, surface-specific formats, or runtime handoff contracts. They MAY omit requirements that are proven non-applicable by the canonical applicability process. They MUST preserve the stable identity and normative meaning of every requirement they carry.

Adapters MUST NOT create new normative requirements, weaken approval or evidence gates, silently resolve conflicts, or claim runtime capabilities that were not independently verified.

Shiroe remains a separate execution and continuity runtime. Grimoire owns requirements, applicability, expected outcomes, gates, evidence contracts, and limits. Shiroe owns activation, roles, models, tools, skills, approvals, retries, memory, and execution receipts.

No Shiroe repository or runtime implementation change is authorized by this ADR.

## Compatibility and historical material

Compatibility and historical documents are non-normative by default.

Historical audits, prior release records, legacy execution artifacts, migration evidence, and superseded standards remain evidence of prior states. They MUST NOT become active v2 normative authority merely because they remain present in the repository.

Compatibility behavior MUST be explicitly typed, bounded, and selected. A compatibility document or legacy record MUST NOT compile into a v2 active normative pack unless a governed compatibility rule explicitly permits that projection.

Promotion of historical or compatibility content into active v2 policy requires a current canonical machine record, provenance, applicability, owner, review, and migration rationale. Historical evidence itself remains unchanged.

The exact Grimoire 1.x compatibility and runtime-boundary rules are decided by ADR 0021 in Phase 10.3.

## Conflict handling

Same-level conflicts produce CONFLICTED and halt automatic resolution.

Grimoire MUST NOT use last-write-wins, document order, confidence, convenience, or unreviewed recency to resolve two same-authority normative requirements that disagree.

Conflicts with different authority levels follow the canonical repository source-of-truth order. The resolution outcome MUST retain enough evidence to show the conflicting requirement IDs or sources, the authority relationship, and the human or policy decision that resolved the conflict.

A runtime adapter, renderer, compiler, or AI surface MUST NOT resolve a canonical conflict independently.

## Phase 11 executable parity gate contract

Phase 11 MUST implement a dependency-free repository gate at:

`checks/human_machine_parity_check.py`

and deterministic fixtures under:

`tests/fixtures/parity/`

For every active normative machine record, the gate MUST verify the parity rules required by the record kind and rendering mode. At minimum it MUST detect and report the following stable reason classes:

- `PARITY_MISMATCH`: a required human rendering disagrees with the canonical machine requirement on a protected semantic dimension such as modality, scope, gate effect, evidence, acceptance, or exception behavior.
- `MISSING_HUMAN_RENDERING`: an active record that requires a human view has no resolvable rendering.
- `UNDECLARED_HUMAN_NORMATIVE_CONTENT`: a human document contains normative content that has no canonical machine owner or allowed projection.
- `MACHINE_CONTRACT_INCOMPLETE`: an active normative machine record lacks fields required by its declared record kind.

The fixture set MUST include at least:

- a valid deterministic `GENERATED` rendering;
- a valid `PARITY_ENFORCED` rendering;
- one fixture for each failure reason above;
- a same-level conflict case that cannot pass through rendering;
- a non-normative explanatory addition that is accepted without becoming a requirement.

The parity gate MUST be part of `python3 scripts/grimoire.py check` before Grimoire 2.0 can claim the human-machine-parity release dimension as `PASS`.

A parity checker MAY use deterministic structural normalization and stable requirement IDs. It MUST NOT claim proof of semantic equivalence that it cannot actually compute. Any semantic relation that cannot be deterministically established MUST surface for human review rather than being silently treated as equal.

Phase 11 implements this contract; Phase 10.2 does not.

## Compatibility impact

This is a breaking architectural direction for Grimoire 2.0 because the v1 corpus permits human and machine normative representations to coexist without universal parity enforcement.

This ADR does not change current v1 compiler behavior, schemas, registry records, standard documents, project packs, runtime adapters, or compatibility artifacts. Existing v1 packs remain subject to their current versioned contracts until the explicit compatibility model in ADR 0021 and later implementation phases define the v2 migration path.

Consumers that rely on hand-authored Markdown as an independent normative override will need to migrate that requirement into the canonical machine model or classify the prose as non-normative explanation.

## Consequences

Positive consequences:

- one stable local normative owner per requirement;
- deterministic compiler and audit inputs;
- machine-readable traceability from requirement to human explanation, source, applicability, verification, and evidence;
- reduced drift between AI-facing and human-facing standards;
- adapters can remain small projections instead of secondary policy engines;
- future contradiction and source-currentness checks can operate on stable requirement identities.

Costs and tradeoffs:

- Phase 11 must introduce record kinds, complete closed contracts, and parity metadata;
- current human standards require migration or generated rendering;
- authoring becomes machine-first for normative semantics;
- deterministic parity checks cannot prove every semantic equivalence, so some changes will require explicit human review;
- migration must preserve v1 compatibility without letting compatibility become a second v2 authority source.

## Non-goals

This ADR does not:

- implement the Phase 11 schema or record-kind taxonomy;
- rewrite the current standards corpus;
- migrate Zeref or Shiroe runtime behavior;
- define the final 1.x compatibility path;
- refresh external official sources;
- implement source-currentness or temporal legal routing;
- add work-type coverage;
- change `VERSION`;
- create a tag or release;
- publish or deploy anything.
