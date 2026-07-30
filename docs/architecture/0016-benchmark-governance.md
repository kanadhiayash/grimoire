# ADR 0016: Benchmark Governance

## Status

Accepted for Phase 6.

## Context

Grimoire needs executable benchmark runs, historical comparison, and exact evidence without treating repository size, line coverage, or a calculated score as product assurance.

## Decision

- Benchmark execution remains Python standard-library only.
- A run is bound to a 40-character commit SHA, environment record, source hashes, exact commands, exit codes, and hashed raw output.
- Evidence packages use the seven canonical files and directories defined by the benchmark standard.
- Hard-gate failure always produces a failing verdict.
- Soft-check failure produces `PARTIAL`, not `PASS`.
- The runner never emits an aggregate product score.
- Historical comparison reports only configured numeric regressions.
- Output directories are immutable run targets: a non-empty target is rejected.

## Boundaries

Benchmark PASS describes only the executed suite and pinned inputs. It does not certify legal compliance, accessibility, security, release readiness, Zeref execution, or product quality outside the recorded evidence.

## Tradeoffs

The Phase 6.1 runner does not infer metrics from arbitrary command text. Scenario and performance missions add reviewed, typed metrics on top of this evidence contract.
