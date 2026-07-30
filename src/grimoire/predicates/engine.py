"""Deterministic, non-executable predicate evaluation."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

MAX_DEPTH = 8
MAX_COLLECTION = 64
FIELD = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)*$")
COMPOSITIONS = {"all", "any", "not"}
LEAF_OPERATORS = {"equals", "in", "contains", "exists", "non_empty"}


class PredicateValidationError(ValueError):
    """Raised when a predicate is outside the constrained language."""

    def __init__(self, reason_codes: set[str]):
        if not reason_codes:
            raise ValueError("predicate validation requires at least one reason")
        self.reason_codes = tuple(sorted(reason_codes))
        super().__init__(", ".join(self.reason_codes))


@dataclass(frozen=True)
class PredicateResult:
    result: bool
    trace: dict[str, Any]
    reason_codes: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "result": self.result,
            "reason_codes": list(self.reason_codes),
            "trace": self.trace,
        }


def _get_field(context: dict[str, Any], field: str) -> tuple[bool, Any]:
    current: Any = context
    for part in field.split("."):
        if not isinstance(current, dict) or part not in current:
            return False, None
        current = current[part]
    return True, current


def _require_collection(value: Any, reasons: set[str]) -> list[Any]:
    if not isinstance(value, list):
        reasons.update({"invalid_predicate", "malformed_operand"})
        return []
    if len(value) > MAX_COLLECTION:
        reasons.add("predicate_limit_exceeded")
    return value


def _validate(predicate: Any, *, depth: int, reasons: set[str]) -> None:
    if depth > MAX_DEPTH:
        reasons.add("predicate_limit_exceeded")
        return
    if not isinstance(predicate, dict) or not predicate:
        reasons.add("invalid_predicate")
        return

    composition_keys = set(predicate) & COMPOSITIONS
    if composition_keys:
        if len(predicate) != 1 or len(composition_keys) != 1:
            reasons.add("invalid_predicate")
            return
        key = next(iter(composition_keys))
        value = predicate[key]
        if key == "not":
            _validate(value, depth=depth + 1, reasons=reasons)
            return
        children = _require_collection(value, reasons)
        for child in children:
            _validate(child, depth=depth + 1, reasons=reasons)
        return

    operator = predicate.get("op")
    field = predicate.get("field")
    if operator not in LEAF_OPERATORS:
        reasons.update({"invalid_predicate", "unsupported_operator"})
        return
    if not isinstance(field, str) or not FIELD.fullmatch(field):
        reasons.update({"invalid_predicate", "invalid_field"})
    value_operators = {"equals", "contains", "in"}
    if operator in {"equals", "contains"} and "value" not in predicate:
        reasons.update({"invalid_predicate", "malformed_operand"})
    if operator == "in":
        if "value" not in predicate:
            reasons.update({"invalid_predicate", "malformed_operand"})
        else:
            _require_collection(predicate.get("value"), reasons)
    allowed_keys = {"field", "op"} | ({"value"} if operator in value_operators else set())
    unexpected = set(predicate) - allowed_keys
    if unexpected:
        reasons.add("invalid_predicate")


def validate_predicate(predicate: Any) -> None:
    reasons: set[str] = set()
    _validate(predicate, depth=0, reasons=reasons)
    if reasons:
        raise PredicateValidationError(reasons)


def _evaluate(predicate: dict[str, Any], context: dict[str, Any], depth: int) -> PredicateResult:
    if "all" in predicate:
        children = [
            _evaluate(child, context, depth + 1)
            for child in predicate["all"]
        ]
        result = all(child.result for child in children)
        return PredicateResult(
            result,
            {
                "op": "all",
                "result": result,
                "children": [child.trace for child in children],
            },
            ("predicate_matched" if result else "predicate_not_matched",),
        )
    if "any" in predicate:
        children = [
            _evaluate(child, context, depth + 1)
            for child in predicate["any"]
        ]
        result = any(child.result for child in children)
        return PredicateResult(
            result,
            {
                "op": "any",
                "result": result,
                "children": [child.trace for child in children],
            },
            ("predicate_matched" if result else "predicate_not_matched",),
        )
    if "not" in predicate:
        child = _evaluate(predicate["not"], context, depth + 1)
        result = not child.result
        return PredicateResult(
            result,
            {"op": "not", "result": result, "child": child.trace},
            ("predicate_matched" if result else "predicate_not_matched",),
        )

    field = predicate["field"]
    operator = predicate["op"]
    exists, actual = _get_field(context, field)
    expected = predicate.get("value")
    result = False
    if operator == "exists":
        result = exists
    elif operator == "non_empty":
        result = exists and isinstance(actual, list) and bool(actual)
    elif operator == "equals":
        result = exists and type(actual) is type(expected) and actual == expected
    elif operator == "contains":
        result = exists and isinstance(actual, list) and any(
            type(candidate) is type(expected) and candidate == expected
            for candidate in actual
        )
    elif operator == "in":
        result = exists and any(
            type(actual) is type(candidate) and actual == candidate
            for candidate in expected
        )
    return PredicateResult(
        result,
        {
            "op": operator,
            "field": field,
            "exists": exists,
            "result": result,
        },
        ("predicate_matched" if result else "predicate_not_matched",),
    )


def evaluate_predicate(predicate: Any, context: dict[str, Any]) -> PredicateResult:
    validate_predicate(predicate)
    return _evaluate(predicate, context, 0)
