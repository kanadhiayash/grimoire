#!/usr/bin/env python3
"""Independently validate Draft 2020-12 schemas and AI Operations fixtures."""

from __future__ import annotations

import copy
import importlib.metadata
import json
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_ROOT = ROOT / "policies" / "schemas"
AI_POLICY = ROOT / "policies" / "ai-operations.json"
AI_SCHEMA = SCHEMA_ROOT / "ai-operations.schema.json"
PROJECT_TEMPLATE = ROOT / "templates" / "project" / "project.json"
PROJECT_SCHEMA = SCHEMA_ROOT / "project-manifest.schema.json"
STANDARD_REGISTRY = ROOT / "registry" / "standards"
STANDARD_SCHEMA = SCHEMA_ROOT / "standards" / "standard-registry-record.schema.json"
SOURCE_REGISTRY = ROOT / "registry" / "sources"
SOURCE_SCHEMA = SCHEMA_ROOT / "standards" / "source-record.schema.json"
FIXTURE_ROOT = ROOT / "tests" / "fixtures" / "schema" / "ai-operations"
EXPECTED_JSONSCHEMA_VERSION = "4.26.0"


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path.relative_to(ROOT)} must contain a JSON object")
    return value


def json_path(parts: list[Any]) -> str:
    value = "$"
    for part in parts:
        if isinstance(part, int):
            value += f"[{part}]"
        else:
            value += f".{part}"
    return value


def apply_fixture(
    base: dict[str, Any],
    fixture: dict[str, Any],
) -> dict[str, Any]:
    value = copy.deepcopy(base)
    path = fixture["path"]
    parent: Any = value
    for key in path[:-1]:
        parent = parent[key]
    leaf = path[-1]
    operation = fixture["operation"]
    if operation == "remove":
        del parent[leaf]
    elif operation in {"add", "replace"}:
        parent[leaf] = fixture["value"]
    else:
        raise ValueError(f"unsupported fixture operation: {operation}")
    return value


def validate() -> list[str]:
    failures: list[str] = []
    installed = importlib.metadata.version("jsonschema")
    if installed != EXPECTED_JSONSCHEMA_VERSION:
        failures.append(
            "jsonschema version "
            f"{installed!r} does not match {EXPECTED_JSONSCHEMA_VERSION!r}"
        )
        return failures

    for path in sorted(SCHEMA_ROOT.rglob("*.json")):
        schema = load_json(path)
        if schema.get("$schema") != "https://json-schema.org/draft/2020-12/schema":
            failures.append(
                f"{path.relative_to(ROOT)} does not declare Draft 2020-12"
            )
            continue
        try:
            Draft202012Validator.check_schema(schema)
        except Exception as exc:
            failures.append(f"{path.relative_to(ROOT)}: invalid schema: {exc}")

    policy = load_json(AI_POLICY)
    schema = load_json(AI_SCHEMA)
    validator = Draft202012Validator(schema)
    for error in sorted(
        validator.iter_errors(policy),
        key=lambda item: (list(item.path), item.validator or ""),
    ):
        failures.append(
            f"{AI_POLICY.relative_to(ROOT)} {json_path(list(error.path))}: "
            f"{error.validator}"
        )

    project_template = load_json(PROJECT_TEMPLATE)
    project_schema = load_json(PROJECT_SCHEMA)
    project_validator = Draft202012Validator(project_schema)
    for error in sorted(
        project_validator.iter_errors(project_template),
        key=lambda item: (list(item.path), item.validator or ""),
    ):
        failures.append(
            f"{PROJECT_TEMPLATE.relative_to(ROOT)} "
            f"{json_path(list(error.path))}: {error.validator}"
        )

    standard_validator = Draft202012Validator(load_json(STANDARD_SCHEMA))
    for path in sorted(STANDARD_REGISTRY.rglob("*.json")):
        value = load_json(path)
        for error in sorted(
            standard_validator.iter_errors(value),
            key=lambda item: (list(item.path), item.validator or ""),
        ):
            failures.append(
                f"{path.relative_to(ROOT)} {json_path(list(error.path))}: "
                f"{error.validator}"
            )

    source_validator = Draft202012Validator(load_json(SOURCE_SCHEMA))
    for path in sorted(SOURCE_REGISTRY.rglob("*.json")):
        value = load_json(path)
        for error in sorted(
            source_validator.iter_errors(value),
            key=lambda item: (list(item.path), item.validator or ""),
        ):
            failures.append(
                f"{path.relative_to(ROOT)} {json_path(list(error.path))}: "
                f"{error.validator}"
            )

    for path in sorted((FIXTURE_ROOT / "valid").glob("*.json")):
        fixture = load_json(path)
        candidate = load_json(ROOT / fixture["source"])
        errors = list(validator.iter_errors(candidate))
        if errors:
            failures.append(
                f"{path.relative_to(ROOT)}: expected valid, got "
                f"{errors[0].validator} at {json_path(list(errors[0].path))}"
            )

    for path in sorted((FIXTURE_ROOT / "invalid").glob("*.json")):
        fixture = load_json(path)
        candidate = apply_fixture(policy, fixture)
        errors = sorted(
            validator.iter_errors(candidate),
            key=lambda item: (list(item.path), item.validator or ""),
        )
        observed = {
            (tuple(error.path), error.validator) for error in errors
        }
        expected = (
            tuple(fixture["expected_path"]),
            fixture["expected_validator"],
        )
        if expected not in observed:
            failures.append(
                f"{path.relative_to(ROOT)}: expected "
                f"{fixture['expected_validator']} at "
                f"{json_path(fixture['expected_path'])}"
            )
    return failures


def main() -> int:
    try:
        failures = validate()
    except (
        OSError,
        ValueError,
        KeyError,
        TypeError,
        json.JSONDecodeError,
        importlib.metadata.PackageNotFoundError,
    ) as exc:
        print(f"FAIL  schema validation setup: {exc}")
        return 1
    if failures:
        for failure in failures:
            print(f"FAIL  {failure}")
        return 1
    print(
        "PASS  Draft 2020-12 schemas, AI Operations fixtures, "
        "and project template"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
