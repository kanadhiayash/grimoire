# Git and Delivery Operations

## Purpose

Make every change traceable, reviewable, testable, releasable, and reversible.

## Expected outcome

Issues, branches, commits, pull requests, checks, releases, deployments, and rollbacks have clear scope and evidence.

## Applicability

All version-controlled projects and standards repositories.

## Non-applicability

Temporary local experiments still require safe handling before promotion to a shared repository.

## Required inputs

Repository policy, protected branches, issue or mission scope, release model, environments, approvals, and required checks.

## Unknowns to resolve

Integration branch, release branch, required reviewers, deployment owner, rollback, and artifact provenance.

## Required actions

Use one mission per branch, focused commits, Conventional Commits, reviewable PRs, protected release branches, required checks, explicit release notes, versioning, provenance, rollback, and branch cleanup.

## Required decisions

Branch model, merge method, versioning, release cadence, artifact signing, environment promotion, and emergency process.

## Required details

Issue, scope, branch, base, files, tests, risks, approvals, commit, build, environment, release, rollback, and status.

## Expected documents and artifacts

Issue, implementation plan, PR, check report, release notes, release evidence, deployment record, rollback plan, and incident link where applicable.

## Document structure

Every PR states problem, scope, before and after behavior, compatibility, evidence, tests, migration, risks, and approval boundaries.

## Acceptance criteria

- Material work has a focused branch and PR.
- Protected branches are not pushed directly.
- Required checks pass on the exact head.
- Release artifacts map to a commit or build.
- Merge and deployment are separately approved when policy requires it.
- Rollback is defined for material releases.

## Verification method

Branch comparison, status checks, review-thread check, artifact digest, deployment verification, and rollback readiness review.

## Evidence required

Commit SHA, PR, checks, review status, artifact digest, release record, and deployment evidence.

## Failure conditions

Direct protected push, mixed missions, invented checks, stale head approval, merge with failed checks, or deployment represented as merge.

## Risks and abuse cases

Supply-chain compromise, history rewriting, secret commits, bypassed review, untraceable artifact, and emergency process abuse.

## Guards and limits

Do not merge, deploy, publish, or delete branches without explicit authority. Do not use `--force` on shared refs without a reviewed recovery reason.

## Exceptions

Emergency exceptions require incident ID, approver, scope, commands, evidence, follow-up review, and expiry.

## Cost considerations

Prefer automation that reduces repeated manual error without adding opaque or high-maintenance release machinery.

## Dependencies

Governance, security, testing, release, and source-discipline standards.

## Related standards

Minimum Correct Change and Release Evidence.

## Source provenance

Use official Git and GitHub guidance plus repository policy.

## Owner and review cycle

Repository maintainers. Review on branch, CI, release, or deployment process changes.

## Zeref execution behavior

Zeref may prepare branches, commits, and PRs within approved scope. Merge, deploy, publish, destructive history changes, and credential actions remain approval-gated.

## Examples

A feature issue maps to one branch, one PR, exact-head checks, a squash merge, and a separate deployment approval.

## Anti-patterns

“CI passed earlier” used to approve a moved head.
