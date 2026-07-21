# AI Operations Governance

This standard defines how AI-assisted work moves from a request to a verified result without relying on vague autonomy, decorative role language, or unreviewed memory writes.

## Execution spine

Material work follows:

```text
ACTIVATE
→ INGEST or RESUME
→ CLASSIFY
→ VERIFY
→ PLAN
→ APPROVE when required
→ EXECUTE bounded scope
→ TEST
→ REVIEW
→ PACKAGE
→ HANDOFF
→ PROMOTE MEMORY when eligible
```

A phase may be skipped only when it is not relevant and the omission does not weaken a quality or security gate.

## Command grammar

The canonical commands are:

| Command | Purpose | Default mutation level |
|---|---|---|
| `ACTIVATE` | Load project state, rules, open work, and the smallest useful role stack | Read-only |
| `INGEST` | Inventory supplied sources, provenance, freshness, and conflicts | Read-only |
| `RESUME` | Reconstruct state from canonical sources and verify current external state | Read-only |
| `AUDIT` | Assess evidence, gaps, risks, contradictions, and corrective priority | Read-only |
| `COUNCIL` | Use independent evaluators only when the assurance mode requires them | Read-only unless separately approved |
| `PLAN` | Define scope, non-goals, dependencies, files, checks, rollback, and gates | Draft only |
| `LOCK` | Record an approved decision, rationale, affected surfaces, and unlock condition | Decision write |
| `APPROVE` | Authorize one named plan revision and no broader scope | Scoped authorization |
| `EXECUTE` | Apply the approved bounded plan | Limited by autonomy level |
| `VERIFY` | Run defined checks and report exact evidence | Non-destructive |
| `SHIP` | Evaluate release readiness and prepare a candidate | No merge or deployment by default |
| `HANDOFF` | Package verified state for another surface or session | Draft or approved local write |
| `PARK` | Record an idea and revisit trigger without planning or implementation | Capture only |
| `PROMOTE_MEMORY` | Move validated, approved information into canonical memory | Canonical writer only |
| `HALT` | Stop mutations, preserve evidence, and report recovery | No further mutation |

Commands must not silently escalate into a more permissive mode.

## Source and conflict discipline

Use the repository-local precedence defined by `AGENTS.md`, security policy, active profile, and stack overlays. An approved plan is specific execution authority, not permission to override higher-priority controls.

When sources conflict:

1. Preserve both claims.
2. Record provenance and freshness.
3. Stop only the affected action.
4. Request or locate human arbitration.
5. Record the resolution.
6. Never choose silently by recency, confidence, or convenience.

## Autonomy levels

| Level | Name | Allowed behavior |
|---:|---|---|
| 0 | Advisory | Explain, compare, and recommend |
| 1 | Read-only | Inspect, research, verify, and summarize |
| 2 | Local reversible | Draft files, edit approved local scope, and run checks |
| 3 | Reviewed external | Prepare an external action and request approval |
| 4 | Pre-approved automation | Execute a narrow recurring action under a stored contract |
| 5 | Prohibited unattended | Sensitive, destructive, irreversible, or authority-bearing action |

Default autonomy is Level 1. A clearly approved local implementation plan may permit Level 2. External actions remain Level 3 unless a stored Level 4 contract names the exact action.

Ambitious language such as “full access,” “autopilot,” or “do everything” does not raise autonomy.

## Approval binding

An approval must resolve to:

- plan identifier
- revision
- approved scope
- excluded scope
- allowed actions
- actions still requiring separate approval
- approver
- timestamp or effective session

Human-friendly aliases such as `FAIRYTALE` are valid only when they resolve unambiguously to the latest unchanged plan revision.

Material plan changes invalidate prior approval.

Approval never implicitly includes merge, deploy, publish, send, delete, credential change, destructive migration, or canonical memory promotion.

## Smallest useful stack

Use one lead role, zero to three support roles, and one quality gate only when risk justifies it.

Assurance modes:

- `lean`: one capable lead and direct verification
- `balanced`: lead plus one specialist or reviewer
- `assured`: independent candidates, dissent, evidence review, and human gate
- `experimental-council`: measured multi-agent or multi-model deliberation

A response may claim a council ran only when independent first-pass work actually ran and disagreement was preserved. One model applying multiple lenses must say so directly.

## Session lifecycle

Material sessions use:

```text
BOOT → ORIENT → CLASSIFY → PLAN → EXECUTE → VERIFY → CLOSE
```

Boot reports:

- project
- last verified decision
- open work
- blockers and conflicts
- current autonomy
- selected stack
- first safe action

Close reports:

- objective
- files or surfaces changed
- behavior changed
- commands and checks run
- exact results
- untouched scope
- remaining risks and unknowns
- memory candidates
- next action
- cross-harness handoff when needed

## Verification and completion

Define verification before implementation when behavior changes.

Allowed completion statuses:

- `PASS`
- `PARTIAL`
- `BLOCKED`
- `NOT_VERIFIED`

Do not use “done,” “production-ready,” “fully fixed,” or equivalent claims without the evidence required by the active profile.

Never weaken, delete, bypass, or rewrite a gate to obtain a pass.

## Memory promotion

Canonical memory uses one designated writer.

Lifecycle:

```text
raw → candidate → validated → approved → canonical
```

Additional states:

```text
contested
superseded
expired
do_not_store
```

Promotion requires source, provenance, evidence grade, privacy class, ownership, contradiction status, and approval when policy requires it.

Do not store secrets, unverified inference, casual conversation, copied external system prompts as canonical truth, or one-time preferences.

Use the Two-Strikes Rule before turning repeated behavior into permanent policy.

## Currentness policy

Verify externally before using facts that may have changed, including:

- software, model, and API versions
- platform behavior
- laws, prices, schedules, roles, and job postings
- repository branches, pull requests, checks, releases, and deployment state
- security advisories
- store submission rules

Prefer connected internal sources, then official primary sources, original documentation, research or standards, strong secondary sources, and clearly labeled community evidence.

## External action gate

Explicit approval is required for:

- commit or push
- issue or pull-request creation or mutation
- merge
- deploy or release
- publication or message send
- calendar or task creation
- deletion, archive, rename, overwrite, or migration
- credential or infrastructure changes
- canonical memory promotion
- public claims or metrics

A stored Level 4 automation contract may pre-approve only narrow, reversible, auditable actions.

## Stop conditions

Stop and surface the smallest recovery path when:

- secrets or private data may be exposed
- a destructive or external action lacks approval
- canonical sources conflict
- required evidence is unavailable
- a requested change weakens a quality or security gate
- repository state contradicts the requested operation
- retries are exhausted without new evidence
- the evaluation rubric would need to change to obtain a pass
- the available tool cannot perform the claimed action
