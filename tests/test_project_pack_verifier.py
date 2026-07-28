from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from grimoire.verifier.project_pack import verify_project_pack
from scripts.project_orchestrator import compile_project


class ProjectPackVerifierTests(unittest.TestCase):
    def valid_manifest(self):
        return {
            "schema_version": 1,
            "project": {
                "name": "Example Product",
                "lifecycle_stage": "BUILD_READY",
                "product_types": ["consumer-mobile"],
            },
            "users": ["authenticated"],
            "markets": ["Canada"],
            "platforms": ["web"],
            "stack": {"languages": ["python"], "frameworks": []},
            "data": {"personal_data": False, "sensitive": []},
            "ai": {"user_facing": False, "automated_decisions": False},
            "risk": {"level": "moderate"},
            "standards": {"version": "0.4.0"},
            "zeref": {"mode": "standard", "cost_ceiling": "bounded"},
            "unknowns": [],
        }

    def make_pack(self, directory: Path, *, generated_at: str | None = None) -> None:
        compile_project(
            self.valid_manifest(),
            directory,
            deterministic=True,
            generated_at=generated_at,
        )

    def test_valid_pack_passes_with_offline_authenticity_not_verified(self):
        with tempfile.TemporaryDirectory() as directory:
            self.make_pack(Path(directory))

            result = verify_project_pack(Path(directory), mode="offline")

            self.assertEqual(result["status"], "PASS")
            self.assertEqual(result["source_authenticity_status"], "NOT_VERIFIED")
            self.assertIn("offline_remote_source_not_checked", result["reason_codes"])

    def test_hash_mismatch_is_rejected_for_correct_reason(self):
        with tempfile.TemporaryDirectory() as directory:
            pack = Path(directory)
            self.make_pack(pack)
            (pack / "AI_CONTEXT.md").write_text("tampered", encoding="utf-8")

            result = verify_project_pack(pack, mode="offline")

            self.assertEqual(result["status"], "FAIL")
            self.assertIn("hash_mismatch", result["reason_codes"])

    def test_unexpected_file_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            pack = Path(directory)
            self.make_pack(pack)
            (pack / "unexpected.txt").write_text("extra", encoding="utf-8")

            result = verify_project_pack(pack, mode="offline")

            self.assertEqual(result["status"], "FAIL")
            self.assertIn("unexpected_file", result["reason_codes"])

    def test_future_timestamp_is_rejected(self):
        future = "2999-01-01T00:00:00+00:00"
        now = datetime(2026, 7, 27, tzinfo=timezone.utc)
        with tempfile.TemporaryDirectory() as directory:
            pack = Path(directory)
            self.make_pack(pack, generated_at=future)

            result = verify_project_pack(pack, mode="offline", now=now)

            self.assertEqual(result["status"], "FAIL")
            self.assertIn("future_timestamp", result["reason_codes"])

    def test_cli_returns_machine_readable_result(self):
        with tempfile.TemporaryDirectory() as directory:
            self.make_pack(Path(directory))
            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/grimoire.py",
                    "project",
                    "verify",
                    "--directory",
                    directory,
                    "--mode",
                    "offline",
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(completed.returncode, 0, completed.stderr)
            self.assertEqual(json.loads(completed.stdout)["status"], "PASS")


if __name__ == "__main__":
    unittest.main()
