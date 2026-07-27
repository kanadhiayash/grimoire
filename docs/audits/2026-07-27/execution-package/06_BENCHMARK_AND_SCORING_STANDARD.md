# Benchmark and Scoring Standard

## 1. Purpose

This document defines what 10/10 means.

A score is a summary of evidence. It is not evidence by itself.

## 2. Scoring model

| Domain | Weight |
|---|---:|
| Product concept and architecture | 15% |
| Compiler correctness and traceability | 20% |
| Enforcement and assurance truthfulness | 20% |
| Security and supply chain | 10% |
| Legal, privacy, and accessibility routing | 10% |
| AI and Zeref integration | 10% |
| Test and benchmark quality | 10% |
| Portability, performance, and operator experience | 5% |

## 3. 10/10 rule

A release receives 10/10 only when:

- weighted score is at least 9.7;
- every domain score is at least 9.5;
- every hard gate passes;
- no critical or high finding remains open;
- benchmark evidence is reproducible;
- an independent reviewer confirms the result;
- no aggregate score hides a failed control.

## 4. Hard gates

### Truthfulness

- false project readiness `PASS`: 0
- false release assurance `PASS`: 0
- automated legal `COMPLIANT`: 0
- browser simulation described as verified local runtime: 0

### Validation

- uncaught exceptions across 10,000 manifest mutations: 0
- schema-invalid policies accepted by CI: 0
- unsupported standards version silently accepted: 0

### Compiler

- enforced controls without standard ID: 0
- enforced controls without version: 0
- enforced controls without source record: 0
- selected controls without rationale: 0
- excluded critical controls without rationale: 0

### Security

- successful symlink overwrite: 0
- path escape: 0
- untrusted manifest instruction execution: 0
- future timestamp accepted: 0
- dirty output silently retained: 0
- critical or high security finding: 0

### Evidence

- verified control without evidence: 0
- evidence not tied to commit or build: 0 for release-blocking controls
- stale evidence accepted as current: 0

### Standards

- enforced standard failing authoring schema: 0
- duplicate standard IDs: 0
- superseded source treated as active: 0

### Zeref

- receipt accepted with mismatched plan revision: 0
- receipt accepted with mismatched pack hash: 0
- unapproved external action treated as valid: 0

## 5. Concept benchmark

Measures whether Grimoire defines a coherent product.

Criteria:

- one canonical source;
- explicit ownership boundaries;
- complete lifecycle;
- complete status model;
- traceable sources;
- predictable extension points;
- explicit non-goals;
- migration and compatibility;
- human and AI usability;
- no contradictory definitions.

A 10 requires zero unresolved architectural contradictions and all material decisions recorded.

## 6. Compiler benchmark

### Gold scenarios

Minimum suite:

1. simple static website;
2. public marketing site with analytics;
3. authenticated B2B SaaS;
4. consumer mobile application;
5. fintech mobile application with location data;
6. health application inside and outside regulated scope;
7. child-directed social product;
8. EU consumer AI assistant;
9. California subscription product using automated decisions;
10. public-sector accessible service;
11. API platform;
12. marketplace with user-generated content;
13. connected product;
14. internal enterprise tool;
15. agentic automation with external tools.

For every scenario, define:

- manifest;
- expected selected controls;
- expected excluded controls;
- expected uncertain controls;
- expected conflicts;
- required documents;
- required evidence;
- required counsel questions;
- expected status.

### Metrics

- critical control recall;
- precision;
- false applicability;
- false non-applicability;
- document selection accuracy;
- conflict recall;
- missing-fact recall;
- deterministic output;
- pack size;
- compile time.

Targets:

- critical recall: 100%
- critical false non-applicability: 0
- overall recall: at least 98%
- overall precision: at least 97%
- deterministic mismatch: 0

## 7. Fuzz benchmark

Input classes:

- wrong types;
- nulls;
- oversized strings;
- Unicode controls;
- duplicate logical IDs;
- deeply nested data;
- path payloads;
- prompt payloads;
- malicious URLs;
- malformed timestamps;
- unsupported schema versions;
- missing nested fields;
- unexpected properties.

Targets:

- 10,000 cases;
- zero unhandled exceptions;
- zero filesystem escape;
- stable error codes;
- all failures produce structured diagnostics.

## 8. Security benchmark

Include:

- symlink attacks;
- hard-link attacks where applicable;
- path traversal;
- race conditions;
- temporary-file permissions;
- prompt injection;
- Markdown injection;
- future timestamps;
- replayed receipts;
- source substitution;
- hash substitution;
- duplicate controls;
- malicious standard records;
- untrusted external source records;
- zip slip for imported packs;
- oversized pack denial of service.

Map security controls to:

- NIST SSDF 1.1;
- OWASP ASVS 5.0.0;
- OWASP MASVS for mobile;
- OWASP AISVS 1.0 for AI-enabled systems;
- SLSA 1.2 for supply chain.

## 9. Accessibility benchmark

For web scenarios:

- map applicable controls to WCAG 2.2 IDs;
- require A and AA coverage;
- distinguish automated and manual tests;
- include assistive-technology evidence;
- prevent a global accessibility `PASS` when only automated checks ran.

Target:

- 100% expected criterion mapping for gold scenarios;
- zero false conformance claims.

## 10. Legal and privacy benchmark

Measures issue spotting and routing, not legal certification.

Targets:

- critical jurisdiction trigger recall: 100%;
- correct `COUNSEL_REVIEW_REQUIRED`: 100% on ambiguous high-risk cases;
- official source requirement: 100%;
- stale-source detection: 100%;
- proposal or draft treated as binding law: 0;
- automated final compliance certification: 0.

## 11. AI and Zeref benchmark

Scenarios:

- prompt injection in project facts;
- tool permission escalation;
- model fallback;
- missing approval;
- mismatched plan revision;
- cost ceiling exceeded;
- retry exhaustion;
- memory promotion without approval;
- browser simulation;
- partial runtime;
- source conflict;
- incomplete execution receipt.

Targets:

- stop-condition recall: 100%;
- unauthorized external action accepted: 0;
- receipt mismatch accepted: 0;
- fabricated council execution claim: 0.

## 12. Performance benchmark

Datasets:

- 100 controls;
- 1,000 controls;
- 10,000 controls;
- 50,000 controls stress profile.

Targets for 10,000 controls:

- median compile under 100 ms;
- p95 under 250 ms;
- verifier under 500 ms offline;
- memory use under an approved budget;
- context pack within configured token ceiling.

## 13. Compatibility benchmark

Must test:

- current CLI;
- deprecated 0.5.x aliases;
- 0.5.x browser packs;
- schema migrations;
- old managed harness blocks;
- unsupported versions fail with migration guidance.

## 14. Test quality benchmark

Targets:

- critical-module line coverage at least 90%;
- critical-module branch coverage at least 85%;
- mutation score at least 85%;
- every P1 audit finding has a red-green regression test;
- no test depends on network unless marked integration;
- benchmark fixtures are versioned and immutable;
- flaky test rate below 0.5%.

## 15. Evidence package

Each benchmark run must emit:

```text
BENCHMARK_SUMMARY.md
BENCHMARK_RESULTS.json
RAW_OUTPUT/
ENVIRONMENT.json
SOURCE_MANIFEST.json
REGRESSIONS.md
SCORECARD.md
```

## 16. Score governance

- score code is reviewed like production code;
- weights are versioned;
- hard gates cannot be bypassed by aggregate score;
- changes to scoring require an ADR;
- benchmark fixtures cannot be changed in the same PR as a failing implementation unless the expected behavior was wrong and independently approved;
- historical results remain retained.
