# ADR 0025: Fail-Closed Final Release Blocker Report

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
`BLOCKER_REPORT_V1` mode. This mode cannot authorize a release or return
eligibility `PASS`. It reports whether these facts agree:

- the checked-out source is clean and matches the expected commit;
- `VERSION`, the baseline, the repository index, README release declaration,
  dated changelog entry, and final release document all name the intended
  version;
- exactly three independently valid candidate runs match the checked-in
  canonical suite ID, sources, source hashes, source tree, ordered gate vector,
  gate types, and declared reason codes;
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
`BLOCKED` with stable reason codes. Malformed CLI inputs return exit code `2`
without echoing their contents.

Repository-local timestamps and the canonical integrity digest are
self-attested. The report therefore always includes
`release_freshness_not_independently_verified` and
`external_signature_contract_unavailable`. A future eligibility decision needs
a separate approved ADR and trust contract for external identity signature,
trusted time, and approval ingestion. These reasons cannot be waived by CLI
input.

## Boundaries

The preflight reads Git and evidence only. It cannot create a commit, tag,
GitHub release, signature, deployment, publication, visibility change, or Zeref
trust anchor. The tag check verifies an existing local tag; it does not create
one. External identity-signature and trusted-time verification are not inputs
to v1.

## Consequences

Release blockers become one independently reproducible report instead of an
operator inference across multiple artifacts. The 1.0.0 source version must not
be advanced while the report is blocked. The current repository may therefore
contain the preflight while truthfully remaining at version 0.5.0 and keeping
the release issue open.
