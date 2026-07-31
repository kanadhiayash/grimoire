from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from checks.ci_policy_check import (  # noqa: E402
    evaluate_ci_policy,
    is_immutable_action_reference,
)


class CiPolicyGateTests(unittest.TestCase):
    @staticmethod
    def _head() -> str:
        return subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        ).stdout.strip()

    def test_action_references_require_full_commit_sha(self) -> None:
        self.assertTrue(
            is_immutable_action_reference(
                "actions/checkout@"
                "9c091bb21b7c1c1d1991bb908d89e4e9dddfe3e0"
            )
        )
        self.assertFalse(is_immutable_action_reference("actions/checkout@v7"))
        self.assertFalse(is_immutable_action_reference("owner/action@main"))

    def test_repository_policy_passes_without_runtime_dependency(self) -> None:
        result = evaluate_ci_policy(ROOT, expected_sha=self._head())

        self.assertEqual(result["status"], "PASS", result["findings"])
        self.assertEqual(result["runtime_external_imports"], [])
        self.assertGreater(result["action_reference_count"], 0)
        self.assertGreater(result["hashed_ci_dependency_count"], 0)
        self.assertEqual(result["cyber_tooling_status"], "NOT_VERIFIED")

    def test_cli_writes_reviewable_exact_commit_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "ci-policy.json"
            completed = subprocess.run(
                [
                    sys.executable,
                    "checks/ci_policy_check.py",
                    "--json-output",
                    str(output),
                    "--expected-sha",
                    self._head(),
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)
            evidence = json.loads(output.read_text(encoding="utf-8"))

        self.assertEqual(evidence["status"], "PASS")
        self.assertEqual(len(evidence["commit"]), 40)
        self.assertIn(evidence["tree_state"], {"CLEAN", "DIRTY"})
        self.assertTrue(evidence["workflows"])

    def test_workflow_runs_policy_as_blocking_read_only_job(self) -> None:
        workflow = (
            ROOT / ".github" / "workflows" / "standards-ci.yml"
        ).read_text(encoding="utf-8")
        policy = workflow.split("ci-policy:", 1)[1]

        self.assertIn("python checks/ci_policy_check.py", policy)
        self.assertIn("actions/upload-artifact@", policy)
        self.assertNotIn("continue-on-error:", policy)
        self.assertIn("permissions:\n  contents: read", workflow)

    def test_unpinned_action_and_suppressed_failure_cannot_pass(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            workflow_root = root / ".github" / "workflows"
            workflow_root.mkdir(parents=True)
            (workflow_root / "unsafe.yml").write_text(
                "permissions:\n"
                "  contents: read\n"
                "jobs:\n"
                "  unsafe:\n"
                "    continue-on-error: true\n"
                "    steps:\n"
                "      - uses: actions/checkout@main\n",
                encoding="utf-8",
            )
            requirement_root = root / "requirements"
            requirement_root.mkdir()
            (requirement_root / "ci-schema.txt").write_text(
                "example==1.0 \\\n"
                "  --hash=sha256:" + ("a" * 64) + "\n",
                encoding="utf-8",
            )
            package = root / "src" / "grimoire"
            package.mkdir(parents=True)
            (package / "__init__.py").write_text("", encoding="utf-8")

            result = evaluate_ci_policy(root, expected_sha="a" * 40)

        codes = {finding["code"] for finding in result["findings"]}
        self.assertEqual(result["status"], "FAIL")
        self.assertIn("action_reference_not_immutable", codes)
        self.assertIn("workflow_failure_suppressed", codes)

    def test_extra_permissions_and_soft_failure_forms_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            workflow_root = root / ".github" / "workflows"
            workflow_root.mkdir(parents=True)
            (workflow_root / "unsafe.yml").write_text(
                "permissions:\n"
                "  contents: read\n"
                "  issues: write\n"
                "  pull-requests: write\n"
                "jobs:\n"
                "  unsafe:\n"
                "    continue-on-error: \"${{ matrix.soft_fail }}\"\n"
                "    permissions:\n"
                "      checks: write\n"
                "    steps:\n"
                "      - uses: actions/checkout@"
                "9c091bb21b7c1c1d1991bb908d89e4e9dddfe3e0\n",
                encoding="utf-8",
            )
            requirement_root = root / "requirements"
            requirement_root.mkdir()
            (requirement_root / "ci-schema.txt").write_text(
                "example==1.0 \\\n"
                "  --hash=sha256:" + ("a" * 64) + "\n",
                encoding="utf-8",
            )
            package = root / "src" / "grimoire"
            package.mkdir(parents=True)
            (package / "__init__.py").write_text("", encoding="utf-8")

            result = evaluate_ci_policy(root, expected_sha="a" * 40)

        codes = {finding["code"] for finding in result["findings"]}
        self.assertIn("workflow_permissions_not_read_only", codes)
        self.assertIn("job_permissions_override", codes)
        self.assertIn("workflow_failure_suppressed", codes)


if __name__ == "__main__":
    unittest.main()
