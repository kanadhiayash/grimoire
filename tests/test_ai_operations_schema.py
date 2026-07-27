from __future__ import annotations

import copy
import json
import re
import subprocess
import sys
import unittest
from pathlib import Path
from typing import Any

try:
    from jsonschema import Draft202012Validator
except ImportError:  # The external validator is installed only in schema CI.
    Draft202012Validator = None  # type: ignore[assignment]


ROOT = Path(__file__).resolve().parents[1]
POLICY_PATH = ROOT / "policies" / "ai-operations.json"
SCHEMA_PATH = ROOT / "policies" / "schemas" / "ai-operations.schema.json"
FIXTURE_ROOT = ROOT / "tests" / "fixtures" / "schema" / "ai-operations"
COMMANDS = {
    "activate",
    "ingest",
    "resume",
    "audit",
    "council",
    "plan",
    "lock",
    "approve",
    "execute",
    "verify",
    "ship",
    "handoff",
    "park",
    "promote_memory",
    "halt",
}
AUTONOMY_LEVELS = {"0", "1", "2", "3", "4", "5"}


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
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


class AIOperationsSchemaTests(unittest.TestCase):
    def setUp(self) -> None:
        self.policy = load_json(POLICY_PATH)
        self.schema = load_json(SCHEMA_PATH)

    def test_schema_declares_explicit_command_properties(self) -> None:
        commands = self.schema["properties"]["commands"]
        self.assertEqual(set(commands["required"]), COMMANDS)
        self.assertEqual(set(commands["properties"]), COMMANDS)
        self.assertFalse(commands["additionalProperties"])
        for name, command_schema in commands["properties"].items():
            self.assertIn("$ref", command_schema, name)

    def test_command_contracts_are_exact_and_closed(self) -> None:
        contracts = self.schema["properties"]["command_contracts"]
        self.assertEqual(set(contracts["required"]), COMMANDS)
        self.assertEqual(set(contracts["properties"]), COMMANDS)
        self.assertFalse(contracts["additionalProperties"])

    def test_autonomy_levels_are_exact_and_closed(self) -> None:
        autonomy = self.schema["properties"]["autonomy_levels"]
        self.assertEqual(set(autonomy["required"]), AUTONOMY_LEVELS)
        self.assertEqual(set(autonomy["properties"]), AUTONOMY_LEVELS)
        self.assertFalse(autonomy["additionalProperties"])
        for level, level_schema in autonomy["properties"].items():
            self.assertIn("$ref", level_schema, level)

    def test_finite_nested_objects_are_closed(self) -> None:
        for name in (
            "scope_boundaries",
            "conflict_policy",
            "approval",
            "assurance_modes",
            "session_outputs",
            "completion_display_labels",
            "memory",
            "external_action_gate",
            "currentness",
        ):
            with self.subTest(name=name):
                self.assertFalse(
                    self.schema["properties"][name]["additionalProperties"]
                )

    @unittest.skipUnless(
        Draft202012Validator is not None,
        "jsonschema is installed only for schema validation",
    )
    def test_current_policy_validates_under_draft_2020_12(self) -> None:
        Draft202012Validator.check_schema(self.schema)
        errors = list(Draft202012Validator(self.schema).iter_errors(self.policy))
        self.assertEqual([], errors)

    @unittest.skipUnless(
        Draft202012Validator is not None,
        "jsonschema is installed only for schema validation",
    )
    def test_valid_fixtures_validate(self) -> None:
        validator = Draft202012Validator(self.schema)
        for path in sorted((FIXTURE_ROOT / "valid").glob("*.json")):
            fixture = load_json(path)
            candidate = load_json(ROOT / fixture["source"])
            with self.subTest(path=path.name):
                self.assertEqual([], list(validator.iter_errors(candidate)))

    @unittest.skipUnless(
        Draft202012Validator is not None,
        "jsonschema is installed only for schema validation",
    )
    def test_invalid_fixtures_fail_for_their_intended_reason(self) -> None:
        validator = Draft202012Validator(self.schema)
        for path in sorted((FIXTURE_ROOT / "invalid").glob("*.json")):
            fixture = load_json(path)
            candidate = apply_fixture(self.policy, fixture)
            errors = sorted(
                validator.iter_errors(candidate),
                key=lambda error: (list(error.path), error.validator or ""),
            )
            observed = {
                (tuple(error.path), error.validator) for error in errors
            }
            expected = (
                tuple(fixture["expected_path"]),
                fixture["expected_validator"],
            )
            with self.subTest(path=path.name):
                self.assertIn(expected, observed)

    def test_ci_lock_is_fully_hashed(self) -> None:
        lock = (ROOT / "requirements" / "ci-schema.txt").read_text(
            encoding="utf-8"
        )
        self.assertIn("jsonschema==4.26.0", lock)
        requirement_lines = [
            line for line in lock.splitlines() if re.match(r"^[a-z0-9-]+==", line)
        ]
        packages = {line.split("==", 1)[0] for line in requirement_lines}
        self.assertEqual(
            packages,
            {
                "attrs",
                "jsonschema",
                "jsonschema-specifications",
                "referencing",
                "rpds-py",
                "typing-extensions",
            },
        )
        self.assertEqual(lock.count("--hash=sha256:"), len(requirement_lines))
        self.assertIn("--only-binary=:all:", lock)

    def test_runtime_does_not_import_external_validator(self) -> None:
        for directory in ("src", "scripts"):
            for path in (ROOT / directory).rglob("*.py"):
                with self.subTest(path=path.relative_to(ROOT)):
                    self.assertNotIn(
                        "jsonschema",
                        path.read_text(encoding="utf-8"),
                    )

    def test_ci_validates_schema_before_dependency_free_check(self) -> None:
        workflow = (
            ROOT / ".github" / "workflows" / "standards-ci.yml"
        ).read_text(encoding="utf-8")
        install = workflow.index(
            "python3 -m pip install --require-hashes"
        )
        schema = workflow.index("python3 checks/json_schema_check.py")
        conformance = workflow.index("python3 scripts/grimoire.py check")
        self.assertLess(install, schema)
        self.assertLess(schema, conformance)

    @unittest.skipUnless(
        Draft202012Validator is not None,
        "jsonschema is installed only for schema validation",
    )
    def test_schema_check_cli_passes(self) -> None:
        completed = subprocess.run(
            [sys.executable, "checks/json_schema_check.py"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(
            completed.returncode,
            0,
            msg=f"stdout:\n{completed.stdout}\nstderr:\n{completed.stderr}",
        )


if __name__ == "__main__":
    unittest.main()
