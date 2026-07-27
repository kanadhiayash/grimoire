from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from grimoire.errors import ManifestValidationError  # noqa: E402
from grimoire.validation.manifest import (  # noqa: E402
    supported_standards_versions,
    validate_manifest,
)
from benchmarks.fuzz.manifest_fuzz import (  # noqa: E402
    FuzzResult,
    MutationCase,
    run_manifest_fuzz,
    write_artifacts,
)


REQUIRED_MUTATION_CLASSES = {
    "wrong_type",
    "null",
    "limit",
    "unicode_control",
    "deep_nesting",
    "path",
    "instruction_payload",
    "url",
    "timestamp",
    "missing_field",
    "unexpected_property",
    "unsupported_version",
    "malformed_nested",
}


class ManifestFuzzTests(unittest.TestCase):
    def test_same_seed_produces_identical_cases_and_results(self) -> None:
        first = run_manifest_fuzz(cases=200, seed=20260727)
        second = run_manifest_fuzz(cases=200, seed=20260727)

        self.assertEqual(first.mutation_cases, second.mutation_cases)
        self.assertEqual(first.results, second.results)
        self.assertEqual(first.corpus_sha256, second.corpus_sha256)
        self.assertEqual(first.results_sha256, second.results_sha256)
        self.assertEqual(
            first.mutation_cases[0].case_id,
            "GRM-FUZZ-20260727-00000",
        )

    def test_required_mutation_classes_all_appear(self) -> None:
        report = run_manifest_fuzz(cases=200, seed=20260727)
        observed = {
            case.mutation_class for case in report.mutation_cases
        }
        self.assertEqual(REQUIRED_MUTATION_CLASSES, observed)

    def test_runner_rejects_too_few_cases_for_complete_coverage(self) -> None:
        with self.assertRaisesRegex(ValueError, "at least 13"):
            run_manifest_fuzz(cases=12, seed=20260727)

    def test_results_are_controlled_and_diagnostics_are_stable(self) -> None:
        report = run_manifest_fuzz(cases=500, seed=20260727)
        self.assertEqual(report.case_count, 500)
        self.assertEqual(report.internal_failures, 0)
        self.assertEqual(report.unexpected_outcomes, 0)
        self.assertGreater(report.controlled_accepts, 0)
        self.assertGreater(report.controlled_rejections, 0)
        self.assertEqual(report.exit_code, 0)

        for result in report.results:
            with self.subTest(case_id=result.case_id):
                self.assertIsInstance(result, FuzzResult)
                self.assertEqual(len(result.diagnostic_sha256), 64)
                if result.outcome == "CONTROLLED_REJECTION":
                    self.assertTrue(result.issues)
                    for issue in result.issues:
                        self.assertTrue(issue.code)
                        self.assertTrue(issue.path.startswith("$"))

    def test_synthetic_validator_crash_is_an_internal_failure(self) -> None:
        def crash_validator(
            value: Any,
            supported_versions: tuple[str, ...],
        ) -> Any:
            raise RuntimeError("synthetic validator failure")

        report = run_manifest_fuzz(
            cases=20,
            seed=20260727,
            validator=crash_validator,
        )
        self.assertEqual(report.internal_failures, 20)
        self.assertEqual(report.exit_code, 1)
        self.assertTrue(
            all(
                result.outcome == "INTERNAL_FAILURE"
                for result in report.results
            )
        )

    def test_audit_manifest_corpus_has_no_unhandled_exceptions(self) -> None:
        supported = supported_standards_versions(ROOT)
        fixture_root = (
            ROOT / "benchmarks" / "audit" / "2026-07-27" / "fixtures"
        )
        fixture_names = (
            "manifest-users-string.json",
            "manifest-risk-string.json",
            "manifest-unknowns-string.json",
            "manifest-personal-data-string.json",
            "manifest-unsupported-version.json",
            "manifest-unknown-property.json",
        )
        for name in fixture_names:
            value = json.loads(
                (fixture_root / name).read_text(encoding="utf-8")
            )
            with self.subTest(name=name):
                with self.assertRaises(ManifestValidationError):
                    validate_manifest(value, supported)

    def test_cli_writes_only_fixed_files_inside_output_directory(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            temporary_root = Path(directory)
            output = temporary_root / "artifacts" / "manifest"
            outside = temporary_root / "outside.json"
            completed = subprocess.run(
                [
                    sys.executable,
                    "benchmarks/fuzz/manifest_fuzz.py",
                    "--cases",
                    "200",
                    "--seed",
                    "20260727",
                    "--output",
                    str(output),
                ],
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
            self.assertEqual(
                {path.name for path in output.iterdir()},
                {"cases.jsonl", "results.jsonl", "summary.json"},
            )
            self.assertEqual(
                {
                    path.relative_to(temporary_root)
                    for path in temporary_root.rglob("*")
                    if path.is_file()
                },
                {
                    Path("artifacts/manifest/cases.jsonl"),
                    Path("artifacts/manifest/results.jsonl"),
                    Path("artifacts/manifest/summary.json"),
                },
            )
            self.assertFalse(outside.exists())
            summary = json.loads(
                (output / "summary.json").read_text(encoding="utf-8")
            )
            self.assertEqual(summary["case_count"], 200)
            self.assertEqual(summary["internal_failures"], 0)
            self.assertEqual(summary["unexpected_outcomes"], 0)
            self.assertIn(
                summary["git_tree_state"],
                {"CLEAN", "DIRTY", "NOT_VERIFIED"},
            )
            self.assertEqual(
                summary["commit_exact"],
                summary["git_tree_state"] == "CLEAN",
            )

    def test_cli_supports_system_tmp_output(self) -> None:
        with tempfile.TemporaryDirectory(dir="/tmp") as directory:
            output = Path(directory) / "manifest"
            completed = subprocess.run(
                [
                    sys.executable,
                    "benchmarks/fuzz/manifest_fuzz.py",
                    "--cases",
                    "20",
                    "--seed",
                    "20260727",
                    "--output",
                    str(output),
                ],
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
            self.assertEqual(
                {path.name for path in output.iterdir()},
                {"cases.jsonl", "results.jsonl", "summary.json"},
            )

    def test_cli_refuses_symlinked_output_directory(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            temporary_root = Path(directory)
            actual = temporary_root / "actual"
            actual.mkdir()
            output = temporary_root / "requested"
            output.symlink_to(actual, target_is_directory=True)
            completed = subprocess.run(
                [
                    sys.executable,
                    "benchmarks/fuzz/manifest_fuzz.py",
                    "--cases",
                    "20",
                    "--seed",
                    "20260727",
                    "--output",
                    str(output),
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(completed.returncode, 1)
            self.assertEqual(list(actual.iterdir()), [])
            error = json.loads(completed.stderr)
            self.assertEqual(error["status"], "INTERNAL_FAILURE")
            self.assertEqual(error["error_type"], "ValueError")

    def test_cli_refuses_symlinked_output_parent(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            temporary_root = Path(directory)
            actual_parent = temporary_root / "actual-parent"
            actual_parent.mkdir()
            requested_parent = temporary_root / "requested-parent"
            requested_parent.symlink_to(
                actual_parent,
                target_is_directory=True,
            )
            output = requested_parent / "nested"
            completed = subprocess.run(
                [
                    sys.executable,
                    "benchmarks/fuzz/manifest_fuzz.py",
                    "--cases",
                    "20",
                    "--seed",
                    "20260727",
                    "--output",
                    str(output),
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(completed.returncode, 1)
            self.assertEqual(list(actual_parent.iterdir()), [])
            error = json.loads(completed.stderr)
            self.assertEqual(error["status"], "INTERNAL_FAILURE")
            self.assertEqual(error["error_type"], "ValueError")

    def test_cli_refuses_parent_traversal_before_creating_output(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            temporary_root = Path(directory)
            requested = temporary_root / "requested"
            requested.mkdir()
            outside = temporary_root / "outside"
            outside.mkdir()
            link = requested / "link"
            link.symlink_to(outside / "base", target_is_directory=True)
            output = link / ".." / "escaped"
            completed = subprocess.run(
                [
                    sys.executable,
                    "benchmarks/fuzz/manifest_fuzz.py",
                    "--cases",
                    "20",
                    "--seed",
                    "20260727",
                    "--output",
                    str(output),
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(completed.returncode, 1)
            self.assertEqual(list(outside.iterdir()), [])
            error = json.loads(completed.stderr)
            self.assertEqual(error["status"], "INTERNAL_FAILURE")
            self.assertEqual(error["error_type"], "ValueError")

    def test_ci_has_fast_subset_and_exact_head_full_gate(self) -> None:
        fast = (
            ROOT / ".github" / "workflows" / "standards-ci.yml"
        ).read_text(encoding="utf-8")
        full = (
            ROOT / ".github" / "workflows" / "manifest-fuzz.yml"
        ).read_text(encoding="utf-8")

        self.assertIn(
            "manifest_fuzz.py --cases 1000 --seed 20260727",
            " ".join(fast.split()),
        )
        self.assertIn("pull_request:", full)
        self.assertIn("schedule:", full)
        self.assertIn(
            "manifest_fuzz.py --cases 10000 --seed 20260727",
            " ".join(full.split()),
        )
        self.assertIn("github.event.pull_request.head.sha || github.sha", full)
        self.assertIn("EXPECTED_SHA", full)
        self.assertIn("artifacts/fuzz/manifest", full)

    def test_corpus_fixtures_are_valid_objects(self) -> None:
        supported = supported_standards_versions(ROOT)
        corpus_root = ROOT / "benchmarks" / "fuzz" / "corpus"
        paths = sorted(corpus_root.glob("*.json"))
        self.assertGreaterEqual(len(paths), 2)
        for path in paths:
            value = json.loads(path.read_text(encoding="utf-8"))
            with self.subTest(path=path.name):
                self.assertIsInstance(value, dict)
                validate_manifest(value, supported)

    def test_repository_index_registers_fuzz_contracts(self) -> None:
        index = json.loads(
            (ROOT / "REPOSITORY_INDEX.json").read_text(encoding="utf-8")
        )
        artifacts = index["artifacts"]
        self.assertEqual(
            artifacts["manifest_fuzz_runner"],
            "benchmarks/fuzz/manifest_fuzz.py",
        )
        self.assertEqual(
            artifacts["manifest_fuzz_corpus"],
            "benchmarks/fuzz/corpus",
        )
        self.assertEqual(
            artifacts["manifest_fuzz_workflow"],
            ".github/workflows/manifest-fuzz.yml",
        )

    def test_public_contracts_are_immutable(self) -> None:
        report = run_manifest_fuzz(cases=20, seed=20260727)
        case = report.mutation_cases[0]
        result = report.results[0]
        self.assertIsInstance(case, MutationCase)
        self.assertIsInstance(result, FuzzResult)
        with self.assertRaises((AttributeError, TypeError)):
            case.case_id = "changed"  # type: ignore[misc]

    def test_artifact_writer_rejects_mutated_case_with_stale_hashes(
        self,
    ) -> None:
        report = run_manifest_fuzz(cases=20, seed=20260727)
        report.mutation_cases[0].mutated_manifest["project"]["name"] = (
            "changed after hashing"
        )

        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "manifest"
            with self.assertRaisesRegex(ValueError, "case hash mismatch"):
                write_artifacts(report, output)
            self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()
