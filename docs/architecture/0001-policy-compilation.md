# ADR-0001: Compile standards into project-local contracts

- Status: Accepted
- Date: 2026-07-09
- Owner: Yash Kanadhia

## Context

AI harnesses differ in instruction precedence, context limits, file discovery, and persistence. Requiring every harness to read an entire standards repository on every task is unreliable and wasteful.

## Decision

Maintain detailed standards centrally, represent mandatory behavior in machine-readable policy, and expose compact project-local bootstrap files and manifests. Harness adapters translate the policy into surface-specific instructions. Local and CI checks verify conformance.

## Consequences

- Standards remain centralized and versioned.
- Projects receive only relevant rules.
- Different harnesses can consume equivalent contracts.
- Instructions still require automated verification because text alone cannot enforce behavior.
