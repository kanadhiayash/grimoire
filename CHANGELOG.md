# Changelog

All notable changes to Engineering Standards are recorded here.

The format follows Keep a Changelog principles. Versions follow Semantic Versioning.

## [Unreleased]

### Added

- Cross-surface Zeref activation policy and JSON schema.
- Explicit local runtime, browser project simulation, browser chat simulation, instruction-only, unavailable, and unverified states.
- Activation, verification, writeback, and external-action receipts.
- Browser source-pack compiler with pinned source commits and SHA-256 integrity records.
- Browser source-pack verifier with tamper, stale-pack, and false-runtime-claim checks.
- ChatGPT Project, Claude Project, Gemini Gem, and generic browser-chat adapters.
- Claude Code, Codex, and Gemini CLI global activation fragments.
- Safe local harness installer with dry-run planning, backups, idempotent managed blocks, verification, and uninstall.
- Surface capability matrix, browser-pack standard, and ADR-0004.
- Thirteen focused tests covering classification, compilation, tamper detection, provenance pins, installer preservation, uninstall, and idempotency.

### Changed

- Baseline policy and schema now require surface activation controls.
- Doctor now validates both the core Engineering Standards policy and cross-surface activation policy.
- Adapter contract now includes browser surfaces, activation receipts, and runtime-versus-simulation truthfulness.
- README and governance now describe cross-surface activation ownership and release requirements.

### Reconciled

- Resolved parallel AI operations implementations by retaining the canonical `ai-operations` layout from pull request #2.
- Added explicit scope boundaries, source precedence, same-level conflict arbitration, command aliases, command output contracts, approval invalidation, currentness categories, and behavior cases.
- Preserved `NOT_VERIFIED` as the machine status while defining `NOT VERIFIED` as the human-facing label.
- Added ADR-0003 and reconciliation conformance tests.

### Planned

- Inventory and reconcile the four legacy practice repositories
- Expand stack-specific overlays
- Generate all remaining adapters from machine-readable policy
- Add optional connector-backed source refresh after a separate approval
- Add policy compatibility tests across released source-pack versions

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
