from __future__ import annotations

import socket
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from grimoire.benchmarks import run_trust_boundary_suite


class TrustBoundaryBenchmarkTests(unittest.TestCase):
    def test_all_inert_cases_return_controlled_expected_outcomes(self):
        with tempfile.TemporaryDirectory() as directory:
            with patch.object(
                socket,
                "create_connection",
                side_effect=AssertionError("network_forbidden"),
            ):
                report = run_trust_boundary_suite(
                    root=ROOT,
                    artifact_root=Path(directory),
                )
        self.assertEqual(report["verdict"], "PASS")
        self.assertEqual(report["unhandled_exceptions"], 0)
        self.assertEqual(report["external_side_effects"], 0)
        self.assertEqual(report["critical_failures"], 0)
        self.assertEqual(
            {case["id"] for case in report["cases"]},
            {
                "benchmark-output-symlink",
                "benchmark-output-replay",
                "context-instruction-payload",
                "manifest-oversized-value",
                "manifest-path-payload",
                "pack-hash-substitution",
                "pack-receipt-replay",
                "pack-future-timestamp",
                "pack-unexpected-file",
                "crosswalk-version-substitution",
                "crosswalk-control-substitution",
                "registry-duplicate-control",
                "registry-malformed-record",
            },
        )
        self.assertTrue(
            all(case["status"] == "PASS" for case in report["cases"])
        )

    def test_generated_inputs_do_not_escape_artifact_root(self):
        with tempfile.TemporaryDirectory() as directory:
            artifact_root = Path(directory) / "artifacts"
            outside = Path(directory) / "outside-marker"
            report = run_trust_boundary_suite(
                root=ROOT,
                artifact_root=artifact_root,
            )
            self.assertEqual(report["external_side_effects"], 0)
            self.assertFalse(outside.exists())
            self.assertEqual(
                sorted(
                    str(path.relative_to(artifact_root))
                    for path in artifact_root.rglob("*")
                    if path.is_file()
                ),
                ["TRUST_BOUNDARY_RESULTS.json"],
            )


if __name__ == "__main__":
    unittest.main()
