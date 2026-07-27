# Grimoire Codex 10/10 Execution Package

## Purpose

This package converts the July 27, 2026 Grimoire audit into a Codex-ready product requirements and execution system.

The target is not a cosmetic score. Grimoire earns 10/10 only when its concepts are internally consistent, its runtime enforces those concepts, its benchmarks are executable and reproducible, and no project receives a false assurance result.

## Canonical target

**Product:** Grimoire  
**Descriptor:** Global Product Engineering Standards Orchestrator  
**Repository:** `kanadhiayash/grimoire`  
**Execution partner:** Zeref  
**Primary implementation surface:** Codex  
**Target release:** Grimoire 1.0.0  
**Current audited release:** Grimoire 0.5.0  
**Audited merge commit:** `72015acac8a57146ad8b00a6c7b4725b8d86a9c8`

## Package contents

| File | Purpose |
|---|---|
| `01_MASTER_PRD.md` | Complete product requirements document for Codex |
| `02_EXECUTIVE_AUDIT_AND_BRUTAL_VERDICT.md` | Current-state findings and scorecard |
| `03_SANDBOX_TEST_EVIDENCE.md` | Exact tests, results, limitations, and reproduction requirements |
| `04_TARGET_PRODUCT_AND_SYSTEM_ARCHITECTURE.md` | Target architecture for the compiler, registry, verifier, and Zeref bridge |
| `05_CODEX_COUNCIL_SWARM_OPERATING_CONTRACT.md` | Senior-agent roles, routing, review, and evidence rules |
| `06_BENCHMARK_AND_SCORING_STANDARD.md` | 10/10 rubric, hard gates, metrics, and benchmark governance |
| `07_PHASED_PR_EXECUTION_PLAN.md` | Ordered pull-request program from 0.5.0 to 1.0.0 |
| `08_TEST_MATRIX_AND_FIXTURE_CATALOG.md` | Unit, integration, fuzz, security, performance, and compatibility tests |
| `09_SECURITY_PRIVACY_LEGAL_ACCESSIBILITY_AI_PLAN.md` | Cross-domain control mappings and enforcement requirements |
| `10_ZEREF_RUNTIME_INTEGRATION_PLAN.md` | Grimoire to Zeref execution and receipt round trip |
| `11_REPOSITORY_FILE_CHANGE_MAP.md` | Proposed folders, files, ownership, and migration map |
| `12_ACCEPTANCE_CRITERIA_AND_RELEASE_GATES.md` | Feature, PR, release, and assurance gates |
| `13_RISK_REGISTER_AND_FAILURE_MODES.md` | Program risks, failure modes, triggers, and mitigations |
| `14_SOURCE_AND_EVIDENCE_MANIFEST.md` | Audit provenance and external authoritative sources |
| `15_CODEX_COPY_PASTE_BOOT_PROMPT.md` | Ready-to-paste Codex activation prompt |
| `16_DECISION_LOG_AND_LOCKED_CONSTRAINTS.md` | Locked decisions and decisions requiring ADRs |
| `17_DEFINITION_OF_DONE.md` | Final 1.0.0 completion contract |

## Reading order for Codex

1. `15_CODEX_COPY_PASTE_BOOT_PROMPT.md`
2. `01_MASTER_PRD.md`
3. `16_DECISION_LOG_AND_LOCKED_CONSTRAINTS.md`
4. `03_SANDBOX_TEST_EVIDENCE.md`
5. `06_BENCHMARK_AND_SCORING_STANDARD.md`
6. `07_PHASED_PR_EXECUTION_PLAN.md`
7. The remaining domain documents only when relevant to the active PR

## Operating rule

Use one lead role, up to three support roles, and one independent quality gate for each PR. The full council is a roster, not a requirement to load every role into every task.

## Status vocabulary

- `PASS`: the scoped claim is proven by current evidence
- `PARTIAL`: part of the scoped claim is proven and the gap is explicit
- `BLOCKED`: a required dependency, decision, or approval prevents safe progress
- `NOT_VERIFIED`: no current evidence proves the claim

## Approval boundary

This package authorizes planning and implementation inside feature branches. It does not authorize:

- merging into `main`
- publishing the private repository
- deploying external services
- changing Zeref internals without a separately approved plan
- issuing legal compliance certifications
- weakening tests or controls to obtain green CI
