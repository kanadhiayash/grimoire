from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from grimoire.benchmarks import (  # noqa: E402
    BenchmarkContractError,
    compare_release_candidate_runs,
    run_release_candidate,
    validate_release_candidate_run,
)


class ReleaseCandidateBenchmarkTests(unittest.TestCase):
    def _repository(self, directory: str) -> tuple[Path, str]:
        root = Path(directory) / "repo"
        root.mkdir()
        (root / "VERSION").write_text("0.5.0\n", encoding="utf-8")
        subprocess.run(["git", "init", "-q"], cwd=root, check=True)
        subprocess.run(
            ["git", "config", "user.email", "benchmark@example.invalid"],
            cwd=root,
            check=True,
        )
        subprocess.run(
            ["git", "config", "user.name", "Benchmark Fixture"],
            cwd=root,
            check=True,
        )
        subprocess.run(["git", "add", "VERSION"], cwd=root, check=True)
        subprocess.run(
            ["git", "commit", "-qm", "fixture"], cwd=root, check=True
        )
        commit = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=root,
            check=True,
            text=True,
            capture_output=True,
        ).stdout.strip()
        return root, commit

    def _suite(
        self,
        *,
        exit_code: int = 0,
        include_unverified: bool = False,
    ) -> dict:
        gates = [
            {
                "id": "executable-gate",
                "category": "validation",
                "command": [
                    "{python}",
                    "-c",
                    f"print('evidence'); raise SystemExit({exit_code})",
                ],
                "hard_gate": True,
            }
        ]
        if include_unverified:
            gates.append(
                {
                    "id": "external-runtime",
                    "category": "zeref",
                    "declared_status": "NOT_VERIFIED",
                    "reason_codes": ["external_runtime_evidence_missing"],
                    "hard_gate": True,
                }
            )
        return {
            "schema_version": 1,
            "suite_id": "release-candidate-fixture",
            "sources": ["VERSION"],
            "gates": gates,
        }

    def test_failed_hard_gate_forces_release_candidate_fail(self):
        with tempfile.TemporaryDirectory() as directory:
            root, commit = self._repository(directory)
            result = run_release_candidate(
                self._suite(exit_code=9),
                root=root,
                output=Path(directory) / "run",
                expected_commit=commit,
                run_id="run-1",
            )
        self.assertEqual(result["verdict"], "FAIL")
        self.assertEqual(result["hard_gate_status"], "FAIL")

    def test_missing_environment_or_raw_output_invalidates_run(self):
        with tempfile.TemporaryDirectory() as directory:
            root, commit = self._repository(directory)
            output = Path(directory) / "run"
            result = run_release_candidate(
                self._suite(),
                root=root,
                output=output,
                expected_commit=commit,
                run_id="run-1",
            )
            (output / "ENVIRONMENT.json").unlink()
            with self.assertRaisesRegex(
                BenchmarkContractError, "missing_environment"
            ):
                validate_release_candidate_run(
                    result,
                    evidence_root=output,
                    expected_commit=commit,
                )
            (output / "ENVIRONMENT.json").write_text(
                json.dumps(result["environment"]), encoding="utf-8"
            )
            (output / "RAW_OUTPUT" / "executable-gate.stdout").unlink()
            with self.assertRaisesRegex(
                BenchmarkContractError, "missing_raw_output"
            ):
                validate_release_candidate_run(
                    result,
                    evidence_root=output,
                    expected_commit=commit,
                )

    def test_dirty_or_mismatched_commit_is_rejected_before_execution(self):
        with tempfile.TemporaryDirectory() as directory:
            root, commit = self._repository(directory)
            with self.assertRaisesRegex(
                BenchmarkContractError, "commit_mismatch"
            ):
                run_release_candidate(
                    self._suite(),
                    root=root,
                    output=Path(directory) / "mismatch",
                    expected_commit="f" * 40,
                    run_id="run-1",
                )
            (root / "dirty.txt").write_text("dirty\n", encoding="utf-8")
            with self.assertRaisesRegex(
                BenchmarkContractError, "dirty_repository"
            ):
                run_release_candidate(
                    self._suite(),
                    root=root,
                    output=Path(directory) / "dirty",
                    expected_commit=commit,
                    run_id="run-1",
                )

    def test_unverified_hard_gate_remains_not_verified(self):
        with tempfile.TemporaryDirectory() as directory:
            root, commit = self._repository(directory)
            result = run_release_candidate(
                self._suite(include_unverified=True),
                root=root,
                output=Path(directory) / "run",
                expected_commit=commit,
                run_id="run-1",
            )
        self.assertEqual(result["verdict"], "NOT_VERIFIED")
        self.assertEqual(result["hard_gate_status"], "NOT_VERIFIED")

    def test_comparison_requires_three_same_commit_zero_variance_runs(self):
        with tempfile.TemporaryDirectory() as directory:
            root, commit = self._repository(directory)
            packages = []
            for index in range(1, 4):
                output = Path(directory) / f"run-{index}"
                run_release_candidate(
                    self._suite(),
                    root=root,
                    output=output,
                    expected_commit=commit,
                    run_id=f"run-{index}",
                )
                packages.append(output)
            comparison = compare_release_candidate_runs(
                packages,
                expected_commit=commit,
            )
            self.assertEqual(comparison["run_count"], 3)
            self.assertEqual(comparison["status_variance"], 0)
            self.assertEqual(comparison["verdict"], "PASS")
            with self.assertRaisesRegex(
                BenchmarkContractError, "expected_three_runs"
            ):
                compare_release_candidate_runs(
                    packages[:2],
                    expected_commit=commit,
                )

    def test_canonical_suite_covers_required_release_candidate_domains(self):
        suite = json.loads(
            (
                ROOT
                / "benchmarks"
                / "release-candidate"
                / "suite.json"
            ).read_text(encoding="utf-8")
        )
        categories = {gate["category"] for gate in suite["gates"]}
        self.assertTrue(
            {
                "validation",
                "compiler",
                "verifier",
                "standards",
                "crosswalk",
                "compatibility",
                "scale",
                "zeref",
                "documentation",
            }.issubset(categories)
        )
        external = next(
            gate
            for gate in suite["gates"]
            if gate["id"] == "zeref-external-runtime"
        )
        self.assertEqual(external["declared_status"], "NOT_VERIFIED")
        self.assertTrue(external["hard_gate"])

    def test_workflow_runs_three_clean_exact_head_reproductions(self):
        workflow = (
            ROOT / ".github" / "workflows" / "release-candidate.yml"
        ).read_text(encoding="utf-8")
        self.assertIn("run-id: [run-1, run-2, run-3]", workflow)
        self.assertIn(
            "ref: ${{ github.event.pull_request.head.sha || github.sha }}",
            workflow,
        )
        self.assertIn("git status --porcelain", workflow)
        self.assertIn("compare", workflow)
        self.assertIn("release-candidate-comparison", workflow)


if __name__ == "__main__":
    unittest.main()
