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

from grimoire.applicability import DecisionState, resolve_applicability  # noqa: E402
from grimoire.registry import load_standard_registry  # noqa: E402
from scripts.project_orchestrator import compile_project, validate_manifest  # noqa: E402


class ControlTraceTests(unittest.TestCase):
    def manifest(self) -> dict[str, object]:
        return {
            "schema_version": 1,
            "project": {
                "name": "Trace Example",
                "lifecycle_stage": "BUILD_READY",
                "product_types": ["consumer-mobile"],
            },
            "users": ["authenticated"],
            "markets": ["Canada"],
            "platforms": ["ios"],
            "stack": {"languages": ["python"], "frameworks": []},
            "data": {"personal_data": True, "sensitive": []},
            "ai": {"user_facing": False, "automated_decisions": False},
            "risk": {"level": "high"},
            "standards": {"version": "0.4.0"},
            "zeref": {"mode": "standard", "cost_ceiling": "bounded"},
            "unknowns": [],
        }

    def test_compiler_writes_one_complete_trace_per_registry_control(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            compile_project(self.manifest(), output, deterministic=True)

            trace = json.loads((output / "CONTROL_TRACE.json").read_text("utf-8"))
            exclusions = json.loads((output / "EXCLUSIONS.json").read_text("utf-8"))
            conflicts = json.loads((output / "CONFLICT_REPORT.json").read_text("utf-8"))
            control_pack = json.loads((output / "CONTROL_PACK.json").read_text("utf-8"))

        self.assertEqual(trace["trace_completeness"], {"actual": 23, "expected": 23, "status": "PASS"})
        self.assertEqual(len(trace["controls"]), 23)
        self.assertEqual(
            [control["standard_id"] for control in trace["controls"]],
            sorted(control["standard_id"] for control in trace["controls"]),
        )
        self.assertTrue(all(control["reason_codes"] for control in trace["controls"]))
        self.assertTrue(all("provenance" in control for control in trace["controls"]))
        self.assertEqual(exclusions["controls"], ["GRIM-STD-0004"])
        self.assertEqual(conflicts, {"conflicts": [], "status": "PASS"})
        self.assertEqual(
            control_pack["selected_controls"],
            [
                "GRIM-STD-0001", "GRIM-STD-0002", "GRIM-STD-0003", "GRIM-STD-0005",
                "GRIM-STD-0006", "GRIM-STD-0007", "GRIM-STD-0008", "GRIM-STD-0009",
                "GRIM-STD-0010", "GRIM-STD-0011", "GRIM-STD-0012",
                "GRIM-STD-0013", "GRIM-STD-0014", "GRIM-STD-0015", "GRIM-STD-0016",
                "GRIM-STD-0017", "GRIM-STD-0018",
                "GRIM-STD-0019", "GRIM-STD-0020",
                "GRIM-STD-0021",
                "GRIM-STD-0022",
                "GRIM-STD-0023",
            ],
        )

    def test_conflicting_fact_blocks_the_applicability_dimension(self):
        registry = load_standard_registry(ROOT / "registry" / "standards", root=ROOT)
        report = resolve_applicability(
            validate_manifest(self.manifest()),
            registry,
            overlays=(
                {"id": "one", "facts": {"markets": ["Canada"]}},
                {"id": "two", "facts": {"markets": ["United States"]}},
            ),
        )

        self.assertTrue(report.conflicts)
        self.assertEqual(
            report.by_id("GRIM-STD-0005").state,
            DecisionState.CONFLICTED,
        )

    def test_cli_explain_matches_trace_without_echoing_untrusted_input(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "pack"
            compile_project(self.manifest(), output, deterministic=True)
            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/grimoire.py",
                    "project",
                    "explain",
                    "--directory",
                    str(output),
                    "--standard-id",
                    "GRIM-STD-0004",
                    "--json",
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            hostile = subprocess.run(
                [
                    sys.executable,
                    "scripts/grimoire.py",
                    "project",
                    "explain",
                    "--directory",
                    str(output),
                    "--standard-id",
                    "<untrusted-value>",
                    "--json",
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(json.loads(completed.stdout)["state"], "EXCLUDED")
        self.assertEqual(hostile.returncode, 2)
        self.assertNotIn("untrusted-value", hostile.stdout + hostile.stderr)


if __name__ == "__main__":
    unittest.main()
