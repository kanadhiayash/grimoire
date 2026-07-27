from __future__ import annotations

import copy
import json
import subprocess
import sys
import tempfile
import unittest
from dataclasses import FrozenInstanceError
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from grimoire.errors import ManifestValidationError  # noqa: E402
from grimoire.models.manifest import ValidatedManifest  # noqa: E402
from grimoire.validation.manifest import (  # noqa: E402
    load_and_validate_manifest,
    supported_standards_versions,
    validate_manifest,
)
from benchmarks.manifest_validation.strict_500 import run_strict_500  # noqa: E402


FIXTURE_ROOT = ROOT / "tests" / "fixtures" / "manifest"


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def apply_case(base: dict[str, Any], case: dict[str, Any]) -> dict[str, Any]:
    value = copy.deepcopy(base)
    path = case["path"]
    parent: Any = value
    for key in path[:-1]:
        parent = parent[key]
    leaf = path[-1]
    if case["operation"] == "remove":
        del parent[leaf]
    elif case["operation"] in {"add", "replace"}:
        parent[leaf] = case["value"]
    else:
        raise ValueError(case["operation"])
    return value


class ManifestValidationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.valid = load_json(FIXTURE_ROOT / "valid" / "full.json")
        self.supported = supported_standards_versions(ROOT)

    def assert_issue(
        self,
        value: Any,
        code: str,
        path: str,
        *,
        actual: str | None = None,
    ) -> ManifestValidationError:
        with self.assertRaises(ManifestValidationError) as raised:
            validate_manifest(value, self.supported)
        observed = {(issue.code, issue.path, issue.actual) for issue in raised.exception.issues}
        if actual is None:
            self.assertTrue(
                any(item[0] == code and item[1] == path for item in observed),
                observed,
            )
        else:
            self.assertIn((code, path, actual), observed)
        return raised.exception

    def test_supported_version_is_derived_from_active_policy(self) -> None:
        policy = load_json(ROOT / "policies" / "standards-orchestrator.json")
        self.assertEqual(self.supported, (policy["module_version"],))
        self.assertEqual(self.supported, ("0.4.0",))

    def test_valid_0_5_x_manifest_normalizes_to_immutable_model(self) -> None:
        manifest = validate_manifest(self.valid, self.supported)
        self.assertIsInstance(manifest, ValidatedManifest)
        self.assertEqual(manifest.project.name, "Example Product")
        self.assertEqual(manifest.project.product_types, ("consumer-mobile",))
        self.assertEqual(manifest.standards.version, "0.4.0")
        with self.assertRaises(FrozenInstanceError):
            manifest.schema_version = 2  # type: ignore[misc]
        normalized = manifest.to_dict()
        self.assertEqual(normalized["markets"], [])
        self.assertEqual(normalized["stack"]["services"], [])

    def test_template_and_minimum_fixtures_are_valid(self) -> None:
        for path in sorted((FIXTURE_ROOT / "valid").glob("*.json")):
            with self.subTest(path=path.name):
                manifest = load_and_validate_manifest(path, self.supported)
                self.assertIsInstance(manifest, ValidatedManifest)

    def test_integral_json_schema_version_normalizes_to_integer(self) -> None:
        value = copy.deepcopy(self.valid)
        value["schema_version"] = 1.0
        manifest = validate_manifest(value, self.supported)
        self.assertEqual(manifest.schema_version, 1)
        self.assertIsInstance(manifest.schema_version, int)

    def test_audited_wrong_types_are_rejected_without_crashes(self) -> None:
        cases = {
            "users_string": (["users"], "abc", "$.users", "string"),
            "risk_string": (["risk"], "critical", "$.risk", "string"),
            "unknowns_string": (["unknowns"], "none", "$.unknowns", "string"),
            "personal_data_string": (
                ["data", "personal_data"],
                "false",
                "$.data.personal_data",
                "string",
            ),
        }
        for name, (path, replacement, expected_path, actual) in cases.items():
            value = copy.deepcopy(self.valid)
            parent: Any = value
            for key in path[:-1]:
                parent = parent[key]
            parent[path[-1]] = replacement
            with self.subTest(name=name):
                self.assert_issue(
                    value,
                    "type_mismatch",
                    expected_path,
                    actual=actual,
                )

    def test_unknown_top_level_and_nested_properties_are_rejected(self) -> None:
        for path in (
            ["unexpected"],
            ["project", "unexpected"],
            ["stack", "unexpected"],
            ["data", "unexpected"],
            ["ai", "unexpected"],
            ["risk", "unexpected"],
            ["standards", "unexpected"],
            ["zeref", "unexpected"],
        ):
            value = copy.deepcopy(self.valid)
            parent: Any = value
            for key in path[:-1]:
                parent = parent[key]
            parent[path[-1]] = True
            expected_path = "$." + ".".join(path)
            with self.subTest(path=expected_path):
                self.assert_issue(value, "unknown_property", expected_path)

    def test_nulls_empty_required_arrays_limits_and_controls_are_rejected(self) -> None:
        cases = [
            (
                {"project": None},
                "type_mismatch",
                "$.project",
            ),
            (
                {"project.product_types": []},
                "empty_collection",
                "$.project.product_types",
            ),
            (
                {"project.name": "x" * 201},
                "string_too_long",
                "$.project.name",
            ),
            (
                {"project.name": "unsafe\u0000name"},
                "control_character",
                "$.project.name",
            ),
        ]
        for replacements, code, expected_path in cases:
            value = copy.deepcopy(self.valid)
            for dotted, replacement in replacements.items():
                parent: Any = value
                parts = dotted.split(".")
                for key in parts[:-1]:
                    parent = parent[key]
                parent[parts[-1]] = replacement
            with self.subTest(code=code):
                self.assert_issue(value, code, expected_path)

    def test_unicode_format_characters_follow_the_schema_contract(self) -> None:
        value = copy.deepcopy(self.valid)
        value["project"]["name"] = "Family\u200dGuide"
        manifest = validate_manifest(value, self.supported)
        self.assertEqual(manifest.project.name, "Family\u200dGuide")

    def test_unsupported_standards_version_is_rejected(self) -> None:
        value = copy.deepcopy(self.valid)
        value["standards"]["version"] = "99.0.0"
        self.assert_issue(
            value,
            "unsupported_version",
            "$.standards.version",
            actual="string",
        )

    def test_multiple_issues_are_safe_sorted_and_do_not_echo_values(self) -> None:
        value = copy.deepcopy(self.valid)
        payload = "DO_NOT_ECHO_THIS_VALUE"
        value["risk"] = payload
        value["users"] = payload
        value["unexpected"] = payload
        error = self.assert_issue(value, "type_mismatch", "$.risk")
        issue_keys = [(issue.path, issue.code) for issue in error.issues]
        self.assertEqual(issue_keys, sorted(issue_keys))
        rendered = json.dumps(error.to_dict(), sort_keys=True)
        self.assertNotIn(payload, rendered)
        self.assertNotIn("value", rendered.lower())

    def test_hostile_unknown_property_names_are_not_echoed_or_unhandled(self) -> None:
        payload = "DO_NOT_ECHO\nUNKNOWN_PROPERTY"
        value = copy.deepcopy(self.valid)
        value[payload] = True
        error = self.assert_issue(value, "unknown_property", "$.*")
        self.assertNotIn(payload, json.dumps(error.to_dict(), sort_keys=True))

        mixed_keys = copy.deepcopy(self.valid)
        mixed_keys["safe_extra"] = True
        mixed_keys[7] = True
        error = self.assert_issue(mixed_keys, "unknown_property", "$.*")
        self.assertTrue(
            any(
                issue.code == "unknown_property"
                and issue.path == "$.safe_extra"
                for issue in error.issues
            )
        )

    def test_malformed_json_and_non_object_roots_are_controlled(self) -> None:
        cases = [
            ("malformed-json.txt", "malformed_json", "$"),
            ("root-array.json", "type_mismatch", "$"),
            ("root-null.json", "type_mismatch", "$"),
        ]
        for name, code, expected_path in cases:
            with self.subTest(name=name):
                with self.assertRaises(ManifestValidationError) as raised:
                    load_and_validate_manifest(
                        FIXTURE_ROOT / "invalid" / name,
                        self.supported,
                    )
                self.assertTrue(
                    any(
                        issue.code == code and issue.path == expected_path
                        for issue in raised.exception.issues
                    )
                )

    def test_project_manifest_schema_is_closed(self) -> None:
        schema = load_json(
            ROOT / "policies" / "schemas" / "project-manifest.schema.json"
        )
        self.assertFalse(schema["additionalProperties"])
        for name in (
            "project",
            "stack",
            "data",
            "ai",
            "risk",
            "standards",
            "zeref",
        ):
            self.assertFalse(schema["properties"][name]["additionalProperties"])

    def test_invalid_mutation_fixtures_fail_for_intended_issue(self) -> None:
        for directory in ("invalid", "hostile"):
            for path in sorted((FIXTURE_ROOT / directory).glob("*.case.json")):
                case = load_json(path)
                candidate = apply_case(self.valid, case)
                with self.subTest(path=path.name):
                    self.assert_issue(
                        candidate,
                        case["expected_code"],
                        case["expected_path"],
                    )

    def test_cli_routes_return_exit_2_with_structured_safe_errors(self) -> None:
        fixtures = (
            ("malformed-json.txt", "malformed_json"),
            ("root-array.json", "type_mismatch"),
            ("root-null.json", "type_mismatch"),
        )
        for command in (
            [
                sys.executable,
                "scripts/project_orchestrator.py",
            ],
            [
                sys.executable,
                "scripts/grimoire.py",
                "project",
                "boot",
            ],
        ):
            for fixture_name, expected_code in fixtures:
                with tempfile.TemporaryDirectory() as directory:
                    output = Path(directory) / "output"
                    completed = subprocess.run(
                        [
                            *command,
                            "--manifest",
                            str(FIXTURE_ROOT / "invalid" / fixture_name),
                            "--output",
                            str(output),
                        ],
                        cwd=ROOT,
                        text=True,
                        capture_output=True,
                        check=False,
                    )
                    with self.subTest(
                        command=command,
                        fixture=fixture_name,
                    ):
                        self.assertEqual(completed.returncode, 2)
                        self.assertEqual(completed.stdout, "")
                        error = json.loads(completed.stderr)
                        self.assertEqual(error["status"], "INVALID")
                        self.assertEqual(
                            error["error_code"],
                            "GRIM_MANIFEST_INVALID",
                        )
                        self.assertEqual(
                            error["issues"][0]["code"],
                            expected_code,
                        )
                        self.assertNotIn("Traceback", completed.stderr)
                        self.assertFalse(output.exists())

    def test_cli_integer_digit_limit_is_a_controlled_parse_error(self) -> None:
        for command in (
            [sys.executable, "scripts/project_orchestrator.py"],
            [
                sys.executable,
                "scripts/grimoire.py",
                "project",
                "boot",
            ],
        ):
            with tempfile.TemporaryDirectory() as directory:
                manifest_path = Path(directory) / "large-integer.json"
                output = Path(directory) / "output"
                manifest_path.write_text(
                    '{"schema_version":' + ("1" * 5_000) + "}",
                    encoding="utf-8",
                )
                completed = subprocess.run(
                    [
                        *command,
                        "--manifest",
                        str(manifest_path),
                        "--output",
                        str(output),
                    ],
                    cwd=ROOT,
                    text=True,
                    capture_output=True,
                    check=False,
                )
                with self.subTest(command=command):
                    self.assertEqual(completed.returncode, 2)
                    self.assertEqual(completed.stdout, "")
                    error = json.loads(completed.stderr)
                    self.assertEqual(
                        error["issues"][0]["code"],
                        "malformed_json",
                    )
                    self.assertNotIn("Traceback", completed.stderr)
                    self.assertFalse(output.exists())

    def test_ci_runs_and_uploads_current_500_case_evidence(self) -> None:
        workflow = (
            ROOT / ".github" / "workflows" / "standards-ci.yml"
        ).read_text(encoding="utf-8")
        command = (
            "python3 benchmarks/manifest_validation/strict_500.py "
            "--cases 500 --seed 20260727 "
            "--output artifacts/manifest-validation/strict-500.json"
        )
        self.assertIn(command, " ".join(workflow.split()))
        self.assertIn(
            "artifacts/manifest-validation/strict-500.json",
            workflow,
        )

    def test_500_case_current_acceptance_has_zero_unhandled_exceptions(self) -> None:
        first = run_strict_500(cases=500, seed=20260727)
        second = run_strict_500(cases=500, seed=20260727)
        self.assertEqual(first["cases"], 500)
        self.assertEqual(first["unhandled_exceptions"], 0)
        self.assertEqual(first["unexpected_accepts"], 0)
        self.assertEqual(first["unexpected_diagnostics"], 0)
        self.assertTrue(
            {
                "ai_string",
                "markets_null",
                "project_name_empty",
                "standards_string",
            }
            <= {result["mutation"] for result in first["results"]}
        )
        self.assertEqual(first["corpus_sha256"], second["corpus_sha256"])
        self.assertEqual(
            first["normalized_results_sha256"],
            second["normalized_results_sha256"],
        )


if __name__ == "__main__":
    unittest.main()
