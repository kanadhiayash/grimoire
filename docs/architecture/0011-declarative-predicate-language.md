# ADR 0011: Declarative Predicate Language

## Status

Accepted.

## Context

Standards applicability must be executable without arbitrary code execution.
Registry records need a constrained expression language that can be evaluated
deterministically and explained with stable traces.

## Decision

Grimoire predicates are JSON objects using only:

- Boolean composition: `all`, `any`, `not`
- Field operations: `equals`, `in`, `contains`, `exists`, `non_empty`

Field paths use dot-separated object keys only. Predicates cannot import
modules, call functions, access the filesystem, execute shell commands, or use
implicit type coercion.

Empty `all` is true and represents universal applicability. Empty `any` is
false. Collection and depth limits are enforced by the runtime evaluator.

## Boundaries

- Predicate evaluation is local and dependency-free.
- Predicate traces explain selection logic, not legal or release compliance.
- Unsupported operators and malformed operands fail closed.
- This engine does not perform network, filesystem, shell, or runtime calls.

## Testing

Focused tests cover allowed operations, deterministic traces, unsupported
operators, malformed operands, non-executable payloads, depth limits, and
collection limits.
