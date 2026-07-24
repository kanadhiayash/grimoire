# ADR-0005: One canonical Standards Orchestrator repository

- Status: Accepted
- Date: 2026-07-24
- Owners: Repository maintainers

## Context

Product design, engineering, legal, accessibility, AI, cloud, cost, Git, and operational standards need one canonical entrypoint. Separate standards repositories would require multiple reads, compatibility tracking, duplicated controls, and cross-repository drift.

## Decision

Keep one canonical repository. Organize standards as independent domains and overlays. A project declares facts in `.standards/project.json`. The Orchestrator compiles one bounded pack for human and AI use.

## Alternatives considered

- Separate product-design and engineering repositories: rejected because it increases reads and version drift.
- A third aggregator repository: rejected because it creates another source of truth.
- One monolithic instruction file: rejected because full-corpus loading wastes context and weakens instruction adherence.

## Consequences

### Positive

- One version, one entrypoint, one compiler, and one verification surface.
- Detailed standards remain available without loading all content into every task.
- Project-local facts do not contaminate global policy.

### Negative

- The repository becomes larger.
- Internal domain ownership and compiler tests become mandatory.

### Risks

A compiler bug could omit a critical control. Critical-control recall tests and conservative `INSUFFICIENT_FACTS` behavior are required.

## Verification

- One project manifest compiles one complete context pack.
- Neutral instructions do not contain personal identity.
- No consuming project needs a second standards repository.
