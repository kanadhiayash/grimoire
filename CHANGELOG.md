# Changelog

All notable changes to Engineering Standards are recorded here.

The format follows Keep a Changelog principles. Versions follow Semantic Versioning.

## [Unreleased]

### Added

- Paste-ready personal instruction pack for Claude Global, Claude Cowork, Claude Projects, Claude Cowork project folders, ChatGPT Global, ChatGPT Projects, and Codex Global customization.
- Character-budget manifest, cross-surface smoke tests, and repository-native unit tests for instruction precedence, Zeref truthfulness, cost routing, approval boundaries, and completion statuses.

### Planned

- Inventory and reconcile the four legacy practice repositories.
- Expand stack-specific overlays.
- Generate all remaining adapters from machine-readable policy.
- Add optional connector-backed source refresh after a separate approval.
- Add policy compatibility tests across released source-pack versions.
- Add signed source-pack manifests after a separate security review.

## [0.3.0] - 2026-07-23

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
- `REPOSITORY_INDEX.json` and its schema as the machine-readable navigation contract for canonical sources, entrypoints, commands, and supported surfaces.
- Dependency-free unified CLI at `scripts/standards.py` for status, catalog, doctor, tests, full checks, browser-pack workflows, and harness management.
- Repository-index conformance checks and tests for path safety, missing files, machine status output, and command delegation.
- Human quickstart and AI-agent entrypoint guides under `docs/operations/`.
- Component policy-version declarations and compatibility validation.
- Release notes and migration guidance for version `0.3.0`.

### Changed

- Baseline policy and schema now require surface activation controls and explicit component policy versions.
- Doctor now validates the core Engineering Standards policy, cross-surface activation policy, repository index, and component-version compatibility.
- Adapter contract now includes browser surfaces, activation receipts, and runtime-versus-simulation truthfulness.
- Root `AGENTS.md` now provides exact boot, task-routing, implementation-stack, precedence, Zeref-boundary, and verification contracts.
- README now provides distinct human and AI-agent start paths and documents the unified CLI.
- Make targets and Standards CI now use the same operational Python command surface and can produce a JSON verification report.
- Governance now describes cross-surface activation ownership and release requirements.

### Reconciled

- Retained the canonical `ai-operations` layout from pull request #2 while preserving the locked workflow semantics added in pull request #3.
- Added explicit scope boundaries, source precedence, same-level conflict arbitration, command aliases, command output contracts, approval invalidation, currentness categories, and behavior cases.
- Preserved `NOT_VERIFIED` as the machine status while defining `NOT VERIFIED` as the human-facing label.
- Kept the stable AI Operations policy module at version `0.2.0` while releasing the repository and Surface Activation module as `0.3.0`.

## [0.2.0] - 2026-07-21

### Added

- Provider-neutral AI operations governance standard.
- Machine-readable command, autonomy, approval, assurance, memory, and lifecycle policy.
- Mission, approval, run-report, escalation, and cross-harness handoff templates.
- AI operations adapter contract.
- Architecture decision for the AI operations control plane.
- Conformance checks for command grammar, autonomy levels, completion statuses, and memory lifecycle.

### Changed

- Baseline policy now requires bounded AI operations controls.
- Policy schema now includes the AI operations section.
- JSON checks now include nested policy schemas.

## [0.1.0] - 2026-07-09

### Added

- Private canonical repository scaffold.
- Agent operating contract.
- Governance and security policies.
- Machine-readable baseline and profile definitions.
- Initial human-readable standards.
- Harness adapter contracts.
- Dependency-free doctor and conformance tests.
- GitHub Actions verification workflow.
