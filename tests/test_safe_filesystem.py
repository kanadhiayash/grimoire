from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from grimoire.filesystem import SafeOutputError, atomic_write_directory, resolve_child


class SafeFilesystemTests(unittest.TestCase):
    def test_symlinked_final_output_is_rejected_before_write(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            outside = root / "outside"
            outside.mkdir()
            output = root / "pack"
            output.symlink_to(outside, target_is_directory=True)

            with self.assertRaises(SafeOutputError) as raised:
                atomic_write_directory(output, {"AI_CONTEXT.md"}, lambda build: None)

            self.assertEqual(raised.exception.code, "symlink_path_rejected")
            self.assertEqual(list(outside.iterdir()), [])

    def test_parent_traversal_cannot_escape_root(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "workspace"
            root.mkdir()

            with self.assertRaises(SafeOutputError) as raised:
                resolve_child(root, "../escape")

            self.assertEqual(raised.exception.code, "path_escape_rejected")
            self.assertFalse((Path(directory) / "escape").exists())

    def test_promotion_removes_stale_files(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "pack"
            output.mkdir()
            (output / "stale.txt").write_text("stale", encoding="utf-8")

            atomic_write_directory(
                output,
                {"AI_CONTEXT.md"},
                lambda build: (build / "AI_CONTEXT.md").write_text(
                    "fresh", encoding="utf-8"
                ),
            )

            self.assertEqual(
                {path.name for path in output.iterdir()},
                {"AI_CONTEXT.md"},
            )
            self.assertEqual(
                (output / "AI_CONTEXT.md").read_text(encoding="utf-8"),
                "fresh",
            )

    def test_failed_build_leaves_prior_pack_unchanged(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "pack"
            output.mkdir()
            (output / "AI_CONTEXT.md").write_text("prior", encoding="utf-8")

            def fail(build: Path) -> None:
                (build / "AI_CONTEXT.md").write_text("partial", encoding="utf-8")
                raise RuntimeError("build failed")

            with self.assertRaises(RuntimeError):
                atomic_write_directory(output, {"AI_CONTEXT.md"}, fail)

            self.assertEqual(
                {path.name for path in output.iterdir()},
                {"AI_CONTEXT.md"},
            )
            self.assertEqual(
                (output / "AI_CONTEXT.md").read_text(encoding="utf-8"),
                "prior",
            )


if __name__ == "__main__":
    unittest.main()
