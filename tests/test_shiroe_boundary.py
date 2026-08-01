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

from grimoire.benchmarks import run_scale_benchmark  # noqa: E402


class ShiroeBoundaryTests(unittest.TestCase):
    def test_active_runtime_boundary_names_shiroe(self) -> None:
        policy = json.loads(
            (ROOT / "policies" / "standards-orchestrator.json").read_text(
                encoding="utf-8"
            )
        )
        boundary = policy["shiroe_boundary"]
        self.assertEqual("kanadhiayash/shiroe", boundary["runtime_repository"])
        self.assertIn("routing", boundary["shiroe_owns"])
        self.assertIn("duplicate shiroe internals", boundary["forbidden"])

    def test_surface_activation_points_to_shiroe(self) -> None:
        policy = json.loads(
            (ROOT / "policies" / "surface-activation.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual("shiroe", policy["runtime_owner"])
        self.assertEqual(
            "https://github.com/kanadhiayash/shiroe",
            policy["canonical_sources"]["shiroe"],
        )

    def test_release_candidate_has_no_declared_unverified_hard_gates(self) -> None:
        suite = json.loads(
            (ROOT / "benchmarks" / "release-candidate" / "suite.json").read_text(
                encoding="utf-8"
            )
        )
        declared = [gate for gate in suite["gates"] if "declared_status" in gate]
        self.assertEqual([], declared)
        gate_ids = {gate["id"] for gate in suite["gates"]}
        self.assertIn("gold-scenario-quality-metrics", gate_ids)
        self.assertIn("scale-resource-budgets", gate_ids)
        self.assertIn("shiroe-external-runtime", gate_ids)
        categories = {gate["category"] for gate in suite["gates"]}
        self.assertIn("shiroe", categories)
        self.assertNotIn("zeref", categories)

    def test_scale_thresholds_verify_memory_and_context_budgets(self) -> None:
        thresholds = json.loads(
            (
                ROOT / "benchmarks" / "performance" / "thresholds.json"
            ).read_text(encoding="utf-8")
        )
        self.assertIsInstance(thresholds["memory_max_bytes"], int)
        self.assertIsInstance(thresholds["context_token_ceiling"], int)
        with tempfile.TemporaryDirectory() as directory:
            report = run_scale_benchmark(
                sizes=(10000,),
                seed=20260730,
                repeats=2,
                thresholds=thresholds,
                output=Path(directory) / "performance",
            )
        self.assertEqual("PASS", report["memory_gate"])
        self.assertEqual("PASS", report["context_token_gate"])
        self.assertEqual("PASS", report["verdict"])


if __name__ == "__main__":
    unittest.main()
