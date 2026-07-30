from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from grimoire.benchmarks import (
    BenchmarkContractError,
    compare_benchmark_results,
    run_benchmark_suite,
    validate_benchmark_result,
)


class BenchmarkRunnerTests(unittest.TestCase):
    def _suite(self) -> dict:
        return {
            "schema_version": 1,
            "suite_id": "runner-contract",
            "sources": ["VERSION"],
            "cases": [
                {
                    "id": "passing-hard-gate",
                    "command": [sys.executable, "-c", "print('raw-pass')"],
                    "hard_gate": True,
                },
                {
                    "id": "failing-soft-check",
                    "command": [
                        sys.executable,
                        "-c",
                        "import sys; print('raw-fail'); sys.exit(3)",
                    ],
                    "hard_gate": False,
                },
            ],
        }

    def test_run_retains_complete_raw_and_normalized_evidence(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "evidence"
            result = run_benchmark_suite(
                self._suite(),
                root=ROOT,
                output=output,
                commit="a" * 40,
            )
            self.assertEqual(result["verdict"], "PARTIAL")
            self.assertNotIn("score", result)
            self.assertEqual(
                {path.name for path in output.iterdir()},
                {
                    "BENCHMARK_SUMMARY.md",
                    "BENCHMARK_RESULTS.json",
                    "RAW_OUTPUT",
                    "ENVIRONMENT.json",
                    "SOURCE_MANIFEST.json",
                    "REGRESSIONS.md",
                    "SCORECARD.md",
                },
            )
            self.assertEqual(
                (output / "RAW_OUTPUT" / "passing-hard-gate.stdout").read_text(),
                "raw-pass\n",
            )
            validate_benchmark_result(result, evidence_root=output)

    def test_failed_hard_gate_forces_fail_without_aggregate_override(self):
        suite = self._suite()
        suite["cases"][0]["command"] = [sys.executable, "-c", "raise SystemExit(2)"]
        with tempfile.TemporaryDirectory() as directory:
            result = run_benchmark_suite(
                suite,
                root=ROOT,
                output=Path(directory) / "evidence",
                commit="b" * 40,
            )
        self.assertEqual(result["verdict"], "FAIL")
        self.assertEqual(result["hard_gate_status"], "FAIL")

    def test_missing_commit_environment_source_or_raw_output_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "evidence"
            result = run_benchmark_suite(
                self._suite(),
                root=ROOT,
                output=output,
                commit="c" * 40,
            )
            for field in ("commit", "environment", "source_manifest"):
                broken = dict(result)
                broken.pop(field)
                with self.assertRaises(BenchmarkContractError):
                    validate_benchmark_result(broken, evidence_root=output)
            (output / "RAW_OUTPUT" / "passing-hard-gate.stdout").unlink()
            with self.assertRaises(BenchmarkContractError):
                validate_benchmark_result(result, evidence_root=output)

    def test_historical_compare_detects_configured_regression(self):
        baseline = {"metrics": {"compile_p95_ms": 200.0, "critical_recall": 1.0}}
        current = {"metrics": {"compile_p95_ms": 260.0, "critical_recall": 1.0}}
        thresholds = {
            "compile_p95_ms": {"max_increase": 25.0},
            "critical_recall": {"max_decrease": 0.0},
        }
        regressions = compare_benchmark_results(current, baseline, thresholds)
        self.assertEqual(
            regressions,
            [
                {
                    "metric": "compile_p95_ms",
                    "baseline": 200.0,
                    "current": 260.0,
                    "delta": 60.0,
                    "threshold": 25.0,
                    "direction": "increase",
                }
            ],
        )


if __name__ == "__main__":
    unittest.main()
