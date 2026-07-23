from __future__ import annotations

import importlib.util
import tempfile
import unittest
from argparse import Namespace
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


compiler = load(
    "compile_surface_pack", ROOT / "scripts" / "compile_surface_pack.py"
)
verifier = load("verify_surface_pack", ROOT / "scripts" / "verify_surface_pack.py")


class BrowserSourcePackTests(unittest.TestCase):
    def args(self, output):
        return Namespace(
            surface="chatgpt-project",
            project_name="Example Project",
            output=str(output),
            engineering_standards_commit="5b637c471dd36af8b7c680352885804b649908eb",
            zeref_commit="833afca7392e268fcaf72ee4ae36ce9aa303eae5",
            pack_version="1.0.0",
            generated_at="2026-07-23T12:00:00+00:00",
            overwrite=False,
        )

    def test_compile_and_verify(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "pack"
            compiler.compile_pack(self.args(output))
            self.assertEqual(verifier.verify_pack(output), [])

    def test_tamper_is_detected(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "pack"
            compiler.compile_pack(self.args(output))
            (output / "AGENTS.md").write_text("tampered", encoding="utf-8")
            errors = verifier.verify_pack(output)
            self.assertIn("hash mismatch for AGENTS.md", errors)

    def test_unpinned_commit_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "pack"
            args = self.args(output)
            args.engineering_standards_commit = "main"
            with self.assertRaises(ValueError):
                compiler.compile_pack(args)


if __name__ == "__main__":
    unittest.main()
