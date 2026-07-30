from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from grimoire.benchmarks import (
    compile_scale_dataset,
    evaluate_scale_results,
    generate_scale_dataset,
    run_scale_benchmark,
    verify_scale_pack,
)


class PerformanceScaleTests(unittest.TestCase):
    def test_identical_seed_produces_identical_dataset_and_pack(self):
        first = generate_scale_dataset(1000, seed=20260730)
        second = generate_scale_dataset(1000, seed=20260730)
        self.assertEqual(first, second)
        first_pack = compile_scale_dataset(first)
        second_pack = compile_scale_dataset(second)
        self.assertEqual(first_pack, second_pack)
        self.assertEqual(verify_scale_pack(first_pack)["status"], "PASS")

    def test_ten_thousand_threshold_regression_fails_verdict(self):
        results = [
            {
                "control_count": 10000,
                "profile": "RELEASE_TARGET",
                "compile_median_ms": 101.0,
                "compile_p95_ms": 200.0,
                "verify_median_ms": 300.0,
                "memory_peak_bytes": 1,
                "pack_size_bytes": 1,
                "estimated_context_tokens": 1,
            }
        ]
        evaluated = evaluate_scale_results(
            results,
            {
                "target_control_count": 10000,
                "compile_median_max_ms": 100.0,
                "compile_p95_max_ms": 250.0,
                "verify_max_ms": 500.0,
                "memory_max_bytes": None,
                "context_token_ceiling": None,
            },
        )
        self.assertEqual(evaluated["verdict"], "FAIL")
        self.assertIn("compile_median_ms", evaluated["regressions"])

    def test_full_matrix_executes_and_stress_is_not_release_target(self):
        with tempfile.TemporaryDirectory() as directory:
            report = run_scale_benchmark(
                sizes=(100, 1000, 10000, 50000),
                seed=20260730,
                repeats=2,
                thresholds={
                    "target_control_count": 10000,
                    "compile_median_max_ms": 10000.0,
                    "compile_p95_max_ms": 10000.0,
                    "verify_max_ms": 10000.0,
                    "memory_max_bytes": None,
                    "context_token_ceiling": None,
                },
                output=Path(directory) / "performance",
            )
        self.assertEqual(
            [item["control_count"] for item in report["datasets"]],
            [100, 1000, 10000, 50000],
        )
        stress = report["datasets"][-1]
        self.assertEqual(stress["profile"], "STRESS_OBSERVATION")
        self.assertFalse(stress["eligible_release_target"])
        self.assertEqual(report["memory_gate"], "NOT_VERIFIED")
        self.assertEqual(report["context_token_gate"], "NOT_VERIFIED")

    def test_fast_supporting_subset_does_not_claim_target_measurement(self):
        with tempfile.TemporaryDirectory() as directory:
            report = run_scale_benchmark(
                sizes=(100, 1000),
                seed=20260730,
                repeats=2,
                thresholds={
                    "target_control_count": 10000,
                    "compile_median_max_ms": 100.0,
                    "compile_p95_max_ms": 250.0,
                    "verify_max_ms": 500.0,
                    "memory_max_bytes": None,
                    "context_token_ceiling": None,
                },
                output=Path(directory) / "performance",
            )
        self.assertFalse(report["target_measured"])
        self.assertEqual(report["verdict"], "PARTIAL")
        self.assertEqual(report["regressions"], [])


if __name__ == "__main__":
    unittest.main()
