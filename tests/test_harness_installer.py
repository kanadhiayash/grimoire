from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "installer", ROOT / "scripts" / "install_ai_harness_standards.py"
)
installer = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(installer)


class HarnessInstallerTests(unittest.TestCase):
    def test_apply_and_uninstall_preserve_user_content(self):
        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory)
            target = home / ".claude" / "CLAUDE.md"
            target.parent.mkdir(parents=True)
            target.write_text("# User content\n", encoding="utf-8")
            installer.apply(home, dry_run=False)
            merged = target.read_text(encoding="utf-8")
            self.assertIn("# User content", merged)
            self.assertIn(installer.START, merged)
            installer.uninstall(home, dry_run=False)
            cleaned = target.read_text(encoding="utf-8")
            self.assertIn("# User content", cleaned)
            self.assertNotIn(installer.START, cleaned)

    def test_apply_is_idempotent(self):
        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory)
            installer.apply(home, dry_run=False)
            installer.apply(home, dry_run=False)
            target = home / ".codex" / "AGENTS.md"
            self.assertEqual(
                target.read_text(encoding="utf-8").count(installer.START), 1
            )


if __name__ == "__main__":
    unittest.main()
