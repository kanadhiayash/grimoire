from __future__ import annotations

import filecmp
import tempfile
import unittest
from pathlib import Path

from scripts.project_orchestrator import compile_project


class DeterministicCompilerTests(unittest.TestCase):
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

    def test_deterministic_compiles_are_byte_identical(self):
        with tempfile.TemporaryDirectory() as directory:
            first = Path(directory) / "first"
            second = Path(directory) / "second"

            first_receipt = compile_project(
                self.valid_manifest(),
                first,
                deterministic=True,
            )
            second_receipt = compile_project(
                self.valid_manifest(),
                second,
                deterministic=True,
            )

            self.assertEqual(first_receipt["sha256"], second_receipt["sha256"])
            for name in first_receipt["output_files"]:
                self.assertTrue(
                    filecmp.cmp(first / name, second / name, shallow=False),
                    msg=name,
                )

    def test_deterministic_generated_at_can_be_explicitly_pinned(self):
        timestamp = "2026-07-27T00:00:00+00:00"
        with tempfile.TemporaryDirectory() as directory:
            receipt = compile_project(
                self.valid_manifest(),
                Path(directory),
                deterministic=True,
                generated_at=timestamp,
            )

            self.assertEqual(receipt["generated_at"], timestamp)


if __name__ == "__main__":
    unittest.main()
