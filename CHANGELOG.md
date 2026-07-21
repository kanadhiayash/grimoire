# Changelog

All notable changes to Engineering Standards are recorded here.

The format follows Keep a Changelog principles. Versions follow Semantic Versioning.

## [Unreleased]

### Reconciled

- Resolved parallel AI operations implementations by retaining the canonical `ai-operations` layout from pull request #2.
- Added explicit scope boundaries, source precedence, same-level conflict arbitration, command aliases, command output contracts, approval invalidation, currentness categories, and behavior cases.
- Preserved `NOT_VERIFIED` as the machine status while defining `NOT VERIFIED` as the human-facing label.
- Added ADR-0003 and reconciliation conformance tests.

### Planned

- Inventory and reconcile the four legacy practice repositories
- Expand stack-specific overlays
- Generate adapters from machine-readable policy
- Add consuming-project installation and synchronization commands
- Add policy compatibility tests

## [0.2.0] - 2026-07-21

### Added

- Provider-neutral AI operations governance standard
- Machine-readable command, autonomy, approval, assurance, memory, and lifecycle policy
- Mission, approval, run-report, escalation, and cross-harness handoff templates
- AI operations adapter contract
- Architecture decision for the AI operations control plane
- Conformance checks for command grammar, autonomy levels, completion statuses, and memory lifecycle

### Changed

- Baseline policy now requires bounded AI operations controls
- Policy schema now includes the AI operations section
- JSON checks now include nested policy schemas

## [0.1.0] - 2026-07-09

### Added

- Private canonical repository scaffold
- Agent operating contract
- Governance and security policies
- Machine-readable baseline and profile definitions
- Initial human-readable standards
- Harness adapter contracts
- Dependency-free doctor and conformance tests
- GitHub Actions verification workflow
