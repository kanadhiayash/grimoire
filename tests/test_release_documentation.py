from __future__ import annotations

import json
import os
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.project_orchestrator import OUTPUT_FILES  # noqa: E402


class ReleaseDocumentationTests(unittest.TestCase):
    def test_readme_uses_locked_identity_and_complete_pack_contract(self) -> None:
        readme = (ROOT / "README.md").read_text(encoding="utf-8")

        self.assertIn("Global Product Engineering Standards Orchestrator", readme)
        self.assertNotIn("will later be renamed", readme)
        self.assertNotIn("Private internal policy", readme)
        self.assertNotIn("Do not publish repository content", readme)
        for filename in OUTPUT_FILES:
            with self.subTest(filename=filename):
                self.assertIn(filename, readme)

    def test_public_facing_root_docs_are_public_safe(self) -> None:
        for path in ("README.md", "GOVERNANCE.md", "SECURITY.md"):
            with self.subTest(path=path):
                value = (ROOT / path).read_text(encoding="utf-8")
                self.assertNotIn("Private internal", value)
                self.assertNotIn("/Users/", value)

    def test_release_candidate_docs_preserve_version_boundaries(self) -> None:
        migration = (
            ROOT / "docs/migrations/0.5.x-to-1.0.md"
        ).read_text(encoding="utf-8")
        decision = (
            ROOT / "docs/architecture/0024-release-and-policy-versioning.md"
        ).read_text(encoding="utf-8")
        release = (ROOT / "docs/releases/1.0.0.md").read_text(
            encoding="utf-8"
        )

        for value in (migration, decision):
            self.assertIn("repository release version", value.lower())
            self.assertIn("standards policy version", value.lower())
            self.assertIn("0.4.0", value)
        self.assertIn("NOT RELEASED", release)
        self.assertIn("release assurance", release.lower())
        self.assertIn("NOT_VERIFIED", release)

    def test_repository_index_routes_current_and_candidate_docs(self) -> None:
        index = json.loads(
            (ROOT / "REPOSITORY_INDEX.json").read_text(encoding="utf-8")
        )
        human = index["entrypoints"]["human"]

        self.assertIn("docs/releases/0.5.0.md", human)
        self.assertIn("docs/releases/1.0.0.md", human)
        self.assertIn("docs/migrations/0.5.x-to-1.0.md", human)
        self.assertIn(
            "docs/operations/command-verification.json",
            index["canonical_sources"].values(),
        )

    def test_documented_command_smoke_is_executable_and_closed(self) -> None:
        manifest_path = ROOT / "docs/operations/command-verification.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

        self.assertEqual(
            set(manifest),
            {"schema_version", "contract_version", "commands"},
        )
        self.assertEqual(manifest["schema_version"], 1)
        self.assertEqual(manifest["contract_version"], "1.0")
        self.assertGreaterEqual(len(manifest["commands"]), 7)
        for command in manifest["commands"]:
            self.assertEqual(
                set(command),
                {"id", "argv", "status", "verification"},
            )
            self.assertIn(command["status"], {"PASS", "NOT_VERIFIED"})
            self.assertTrue(command["argv"])
            if command["status"] == "PASS":
                evidence = ROOT / command["verification"]
                self.assertTrue(evidence.is_file())

        if os.environ.get("GRIMOIRE_DOC_SMOKE_ACTIVE") == "1":
            self.skipTest("nested documented-command smoke is suppressed")
        completed = subprocess.run(
            [
                sys.executable,
                "scripts/verify_documented_commands.py",
                "--json",
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        result = json.loads(completed.stdout)
        self.assertEqual(result["status"], "PASS")
        self.assertTrue(result["commands"])
        self.assertTrue(
            all(item["status"] == "PASS" for item in result["commands"])
        )
        expected = {
            item["id"]
            for item in manifest["commands"]
            if item["status"] == "PASS"
        }
        observed = {item["id"] for item in result["commands"]}
        self.assertEqual(observed, expected)

    def test_release_runbook_builds_every_required_input_in_order(self) -> None:
        runbook = (
            ROOT / "docs/operations/release-evidence-and-rollback.md"
        ).read_text(encoding="utf-8")
        check = "artifacts/release-inputs/grimoire-check.json"
        benchmark = (
            "artifacts/release-inputs/benchmark/BENCHMARK_RESULTS.json"
        )

        self.assertGreaterEqual(runbook.count(check), 2)
        self.assertGreaterEqual(runbook.count(benchmark), 1)
        self.assertLess(
            runbook.index("scripts/grimoire.py check"),
            runbook.index("scripts/release_evidence.py generate"),
        )
        self.assertLess(
            runbook.index("scripts/benchmark_runner.py run"),
            runbook.index("scripts/release_evidence.py generate"),
        )

    def test_migration_docs_use_fifteen_file_pack_and_legacy_tests(self) -> None:
        for path in (
            "docs/migrations/0.5.x-manifest-validation.md",
            "docs/migrations/0.5.x-status-model.md",
            "docs/migrations/0.5.x-to-1.0.md",
        ):
            with self.subTest(path=path):
                value = (ROOT / path).read_text(encoding="utf-8")
                self.assertNotIn("twelve generated", value)
                self.assertIn("fifteen", value.lower())

        identity_tests = (
            ROOT / "tests/test_grimoire_identity.py"
        ).read_text(encoding="utf-8")
        self.assertIn("legacy_cli_alias", identity_tests)


if __name__ == "__main__":
    unittest.main()
