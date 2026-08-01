from __future__ import annotations

import json
import hashlib
import sys
import subprocess
import tempfile
import unittest
import urllib.error
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from grimoire.benchmarks import run_scale_benchmark  # noqa: E402
from checks import shiroe_trust_check  # noqa: E402


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

    def test_shiroe_trust_check_falls_back_to_pinned_checkout(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            checkout = workspace / "shiroe"
            checkout.mkdir()
            files = {
                "AGENTS.md": "# Agent spec\n",
                "CODEX.md": "# Codex adapter\n",
                "shiroe-registry.json": json.dumps(
                    {
                        "version": "3.0.0-alpha.1",
                        "skills": [f"skill-{index}" for index in range(15)],
                        "commands": [f"command-{index}" for index in range(8)],
                    },
                    sort_keys=True,
                )
                + "\n",
            }
            for name, content in files.items():
                (checkout / name).write_text(content, encoding="utf-8")
            subprocess.run(["git", "init", "--quiet"], cwd=checkout, check=True)
            subprocess.run(
                ["git", "config", "user.email", "test@example.invalid"],
                cwd=checkout,
                check=True,
            )
            subprocess.run(
                ["git", "config", "user.name", "Grimoire Test"],
                cwd=checkout,
                check=True,
            )
            subprocess.run(["git", "add", "."], cwd=checkout, check=True)
            subprocess.run(
                ["git", "commit", "--quiet", "-m", "fixture"],
                cwd=checkout,
                check=True,
            )
            commit = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=checkout,
                check=True,
                stdout=subprocess.PIPE,
                text=True,
            ).stdout.strip()
            contract = {
                "runtime_repository": "kanadhiayash/shiroe",
                "commit": commit,
                "required_files": [
                    {
                        "path": name,
                        "sha256": hashlib.sha256(
                            content.encode("utf-8")
                        ).hexdigest(),
                    }
                    for name, content in files.items()
                ],
                "required_registry": {
                    "version": "3.0.0-alpha.1",
                    "skills_minimum": 15,
                    "commands_minimum": 8,
                },
                "claims": {"verified": [], "not_claimed": []},
            }
            contract_path = workspace / "contract.json"
            output_path = workspace / "output.json"
            contract_path.write_text(
                json.dumps(contract, sort_keys=True),
                encoding="utf-8",
            )
            argv = [
                "shiroe_trust_check.py",
                "--contract",
                str(contract_path),
                "--output",
                str(output_path),
                "--source-checkout",
                str(checkout),
            ]
            with mock.patch.object(sys, "argv", argv):
                with mock.patch.object(
                    shiroe_trust_check,
                    "_fetch",
                    side_effect=urllib.error.URLError("blocked"),
                ):
                    self.assertEqual(0, shiroe_trust_check.main())
            result = json.loads(output_path.read_text(encoding="utf-8"))
            self.assertEqual("PASS", result["status"])
            self.assertEqual(
                {"source_checkout"},
                {record["transport"] for record in result["fetched"]},
            )


if __name__ == "__main__":
    unittest.main()
