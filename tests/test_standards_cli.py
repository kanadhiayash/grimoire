import json
import tempfile
import unittest
from pathlib import Path

from scripts.standards import (
    build_harness_command,
    build_pack_command,
    build_status,
    load_index,
)


class StandardsCliTests(unittest.TestCase):
    def make_repo(self) -> Path:
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        root = Path(temp.name)
        (root / "VERSION").write_text("0.2.0\n", encoding="utf-8")
        index = {
            "schema_version": 1,
            "standard_version": "0.2.0",
            "repository": "example/standards",
            "canonical_sources": {"repository_contract": "AGENTS.md"},
            "entrypoints": {
                "human": ["README.md"],
                "agent": ["AGENTS.md"],
            },
            "commands": {},
            "surfaces": {},
            "verification": {"commands": []},
        }
        (root / "REPOSITORY_INDEX.json").write_text(
            json.dumps(index), encoding="utf-8"
        )
        (root / "AGENTS.md").write_text("# agents\n", encoding="utf-8")
        (root / "README.md").write_text("# readme\n", encoding="utf-8")
        return root

    def test_load_index_returns_object(self):
        root = self.make_repo()
        self.assertEqual(load_index(root)["repository"], "example/standards")

    def test_build_status_is_machine_readable(self):
        root = self.make_repo()
        status = build_status(root)
        self.assertEqual(status["standard_version"], "0.2.0")
        self.assertEqual(status["index_version"], "0.2.0")
        self.assertTrue(status["index_matches_version"])
        self.assertEqual(status["missing_entrypoints"], [])
        self.assertEqual(status["health"], "PASS")

    def test_build_status_reports_missing_entrypoints(self):
        root = self.make_repo()
        (root / "README.md").unlink()
        status = build_status(root)
        self.assertEqual(status["health"], "PARTIAL")
        self.assertIn("README.md", status["missing_entrypoints"])

    def test_build_pack_command_uses_existing_compiler(self):
        command = build_pack_command(
            surface="chatgpt-project",
            project_name="Example",
            output="dist/example",
            grimoire_commit="a" * 40,
            zeref_commit="b" * 40,
        )
        self.assertIn("scripts/compile_surface_pack.py", command)
        self.assertIn("chatgpt-project", command)

    def test_build_harness_command_uses_existing_installer(self):
        command = build_harness_command("detect", home="/tmp/home")
        self.assertIn("scripts/install_ai_harness_standards.py", command)
        self.assertEqual(command[-2:], ["--home", "/tmp/home"])


if __name__ == "__main__":
    unittest.main()
