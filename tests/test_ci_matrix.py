from __future__ import annotations

import json
import platform
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "standards-ci.yml"


class SupportedCiMatrixTests(unittest.TestCase):
    def test_required_python_and_platform_matrix_is_blocking(self) -> None:
        workflow = WORKFLOW.read_text(encoding="utf-8")

        self.assertIn("runtime-matrix:", workflow)
        self.assertIn("os: [ubuntu-latest, macos-latest]", workflow)
        self.assertIn('python: ["3.11", "3.12", "3.13"]', workflow)
        matrix_section = workflow.split("runtime-matrix:", 1)[1]
        self.assertNotIn("continue-on-error:", matrix_section)
        self.assertIn("python scripts/grimoire.py check", matrix_section)
        self.assertIn("benchmarks/manifest_validation/strict_500.py", matrix_section)
        self.assertIn("benchmarks/fuzz/manifest_fuzz.py", matrix_section)

    def test_matrix_retains_exact_environment_evidence(self) -> None:
        workflow = WORKFLOW.read_text(encoding="utf-8")
        matrix_section = workflow.split("runtime-matrix:", 1)[1]

        self.assertIn("scripts/write_ci_environment.py", matrix_section)
        self.assertIn("github.event.pull_request.head.sha || github.sha", matrix_section)
        self.assertIn("actions/upload-artifact@", matrix_section)
        self.assertIn("matrix-environment-", matrix_section)

    def test_windows_is_explicitly_not_verified(self) -> None:
        adr = (
            ROOT
            / "docs"
            / "architecture"
            / "0021-supported-runtime-matrix.md"
        ).read_text(encoding="utf-8")

        self.assertIn("Windows: `NOT_VERIFIED`", adr)
        self.assertIn("Python 3.11, 3.12, and 3.13", adr)
        self.assertNotIn("Windows: `PASS`", adr)

    def test_environment_writer_binds_exact_commit(self) -> None:
        expected = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        ).stdout.strip()
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "environment.json"
            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/write_ci_environment.py",
                    "--output",
                    str(output),
                    "--expected-sha",
                    expected,
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)
            evidence = json.loads(output.read_text(encoding="utf-8"))

        self.assertEqual(evidence["commit"], expected)
        self.assertTrue(evidence["commit_exact"])
        self.assertEqual(evidence["python_version"], platform.python_version())
        self.assertTrue(evidence["platform"])
        self.assertTrue(evidence["os"])


if __name__ == "__main__":
    unittest.main()
