# Standards Orchestrator v0.4.0 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox syntax for tracking.

**Goal:** Upgrade Engineering Standards into a neutral, one-entrypoint Standards Orchestrator that compiles product-specific controls, documents, gates, evidence requirements, and Zeref execution metadata.

**Architecture:** Keep one canonical repository and one project-local JSON manifest. Human-readable standards and machine policies remain modular at rest. The project compiler emits one bounded AI context pack for execution.

**Tech Stack:** Python 3.11+ standard library, JSON Schema draft 2020-12, JSON, Markdown, GitHub Actions.

## Global Constraints

- Keep the repository dependency-free.
- Do not modify Zeref Memory Engine.
- Keep neutral global instructions separate from the Yash personal overlay.
- Do not claim legal compliance from automated checks.
- Require fresh evidence before PASS.
- Require explicit approval for merge, deployment, publication, destructive changes, credential changes, and canonical memory writes.

---

### Task 1: Lock architecture and terminology
- [ ] Add ADRs for the single-repository orchestrator, document contracts, instruction layers, and Zeref boundary.
- [ ] Add the authoring, naming, priority, legal-control, product-design, and Minimum Correct Change standards.
- [ ] Verify every normative document separates requirements, evidence, exceptions, and sources.

### Task 2: Add machine contracts
- [ ] Add the Orchestrator policy.
- [ ] Add schemas for project manifests, standard records, document requirements, and Zeref execution profiles.
- [ ] Validate every JSON document with the repository checker.

### Task 3: Build the one-call compiler
- [ ] Write failing tests for manifest validation, pack outputs, lifecycle validation, and unknown handling.
- [ ] Implement `scripts/project_orchestrator.py`.
- [ ] Integrate `project boot` into the unified CLI.
- [ ] Confirm the compiler emits the twelve required files and SHA-256 receipt.

### Task 4: Add human and AI templates
- [ ] Add project manifest, product brief, user flow, implementation plan, release evidence, standard record, and document requirement templates.
- [ ] Ensure every template contains expected outcomes, inputs, details, acceptance, verification, evidence, risks, guards, costs, owners, and next gate where applicable.

### Task 5: Add instruction layers
- [ ] Add neutral global instruction modules.
- [ ] Add surface-neutral manifest metadata.
- [ ] Add the private Yash copy-paste overlay.
- [ ] Test that neutral files contain no personal identity strings.

### Task 6: Add legal source governance
- [ ] Add legal source classification and applicability rules.
- [ ] Add an initial official-source registry with freshness and review metadata.
- [ ] Prevent automated compliance claims and stale-source promotion.

### Task 7: Add checks, benchmarks, and release records
- [ ] Add the Orchestrator checker and unit tests.
- [ ] Add benchmark scenarios and hard safety targets.
- [ ] Update README, AGENTS, GOVERNANCE, REPOSITORY_INDEX, VERSION, CHANGELOG, and release notes.
- [ ] Run `python3 scripts/standards.py check` and record exact results.
