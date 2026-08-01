# ADR 0025: Non-Mutating Final Release Decision

- Status: Accepted
- Date: 2026-08-01

## Context

The release-candidate runner produces exact-commit evidence, and the release
evidence module verifies artifact integrity. Neither surface alone proves that
all final release boundaries passed. A generic benchmark smoke can be valid
while a release-candidate hard gate remains `NOT_VERIFIED`; an integrity digest
is not an identity signature; and standing merge authority is not the fresh
exact-commit release approval required by the locked release contract.

## Decision

Grimoire provides a dependency-free, non-mutating final preflight in
`FINAL_RELEASE_DECISION_V1` mode. It reports whether these facts agree:

- the checked-out source is clean and matches the expected commit;
- `VERSION`, the baseline, the repository index, README release declaration,
  dated changelog entry, and final release document all name the intended
  version;
- exactly three independently valid candidate runs match the checked-in
  canonical suite ID, sources, source hashes, source tree, ordered gate vector,
  and gate command contract;
- those runs reproduce the supplied comparison with zero status variance and a
  `PASS` verdict;
- every candidate hard gate is `PASS`;
- release evidence is bound to the same commit and has `PASS` verification,
  package, and release-assurance status;
- candidate command evidence and the release-evidence package report timestamps
  no more than 24 hours old and do not claim a future timestamp;
- release approval is scoped to that exact commit and is no more than 24 hours
  old;
- the intended tag matches the version and, when requested, resolves to the
  exact commit.

Any missing, invalid, `FAIL`, `PARTIAL`, or `NOT_VERIFIED` boundary returns
`BLOCKED` with stable reason codes. When no blockers remain, the decision
returns `PASS` and `eligible=true`. Malformed CLI inputs return exit code `2`
without echoing their contents.

Repository-local timestamps and the canonical integrity digest are
self-attested. Private release approval is recorded as
`APPROVED_NOT_CRYPTOGRAPHIC`, which is release assurance for this private source
release and is not a cryptographic identity signature.

## Boundaries

The preflight reads Git and evidence only. It cannot create a commit, tag,
GitHub release, signature, deployment, publication, visibility change, or Shiroe
repository change. The tag check verifies an existing local tag; it does not
create one. Cryptographic identity signing remains outside this contract.

## Consequences

Release eligibility becomes one independently reproducible report instead of an
operator inference across multiple artifacts. The 1.0.0 source version may be
advanced only in the same reviewed branch that supplies executable hard gates,
fresh exact-commit evidence, and exact-commit approval.
