# ADR 0023: Release Provenance and Rollback

- Status: Accepted
- Date: 2026-07-30

## Numbering note

The program issue called this ADR 0018, but ADR 0018 already records the control
trace evidence architecture. Reusing that identifier would make both decisions
ambiguous, so the next available identifier, 0023, is used.

## Decision

Release evidence is a closed, dependency-free record bound to:

- the exact checked-out source commit;
- the build environment and tracked-tree state;
- artifact paths, byte sizes, and SHA-256 hashes;
- complete benchmark packages, suite identities, hashes, controlled statuses,
  and the exact source commit;
- exact release approvals when supplied;
- a closed permission scope;
- a canonical integrity digest.

Generation, verification, and rollback rehearsal are allowed. Signing,
publishing, creating a release, and deploying are prohibited in the evidence
mission.

SHA-256 integrity is not an identity signature. Until an independently approved
signing mechanism and key boundary exist, signature and release assurance remain
`NOT_VERIFIED`. A `PASS` signature claim is rejected.

Artifact and benchmark inputs must be regular repository files reached without
symlinks. A generic check result cannot be relabeled as benchmark evidence.

## Rollback

The executable rollback command is a non-mutating private dry run. It verifies
the evidence, confirms no release-side action occurred, retains the exact
evidence, and describes reviewed revert or local artifact-discard options. It
does not run reset, history rewrite, tag deletion, release deletion, or package
deletion.

## Consequences

Evidence structure and artifact binding can pass before release approval.
Release assurance cannot pass merely because evidence generation passed.
