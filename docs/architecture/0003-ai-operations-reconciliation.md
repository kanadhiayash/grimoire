# ADR-0003: Reconcile parallel AI operations implementations

- Status: Accepted
- Date: 2026-07-21
- Owner: Yash Kanadhia

## Context

Two branches implemented the locked AI operations plan from the same original `main` commit.

Pull request #2 merged first and established the canonical repository layout:

```text
policies/ai-operations.json
policies/schemas/ai-operations.schema.json
standards/ai-development/ai-operations-governance.md
templates/ai-operations/
```

Pull request #3 used a parallel `zeref-workflow-registry` layout and therefore conflicted after pull request #2 merged.

Merging both layouts would create duplicate policy sources, duplicate templates, and unclear authority.

## Decision

Keep the pull request #2 file layout as canonical.

Reset the pull request #3 branch onto current `main`, discard duplicate files, and carry forward only semantics that strengthen the existing control plane:

- explicit global, project, and repository boundaries;
- ten-level source precedence;
- same-level conflict arbitration;
- exact command aliases, including `FAIRYTALE` and `ETHERIOUS`;
- required output and stop-condition contracts for every command;
- approval invalidation rules;
- protection against autonomy inferred from ambitious wording;
- memory review and approval fields;
- explicit currentness categories;
- behavioral validation cases;
- a human-facing `NOT VERIFIED` label while retaining the stable `NOT_VERIFIED` machine key.

## Verification requirement

The reconciled branch must be based on current `main`, contain no duplicate policy tree, pass all repository unit tests, and pass the GitHub Actions `make check` workflow before merge.

## Consequences

- One policy remains canonical.
- Existing adapters and consuming projects keep their current paths.
- The conflict is resolved without adding a second registry or template tree.
- Conformance tests cover the reconciled semantics.
- No version bump beyond `0.2.0` is required because this reconciliation completes the same unreleased control-plane change.
