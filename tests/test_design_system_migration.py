from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))
from grimoire.registry import load_standard_registry


class DesignSystemMigrationTests(unittest.TestCase):
    def test_design_system_records_are_normative_source_linked_contracts(self):
        records = load_standard_registry(ROOT / "registry" / "standards", root=ROOT)
        selected = [r for r in records.values() if r.domain == "design-systems"]
        self.assertEqual(len(selected), 2)
        self.assertTrue(all(r.provenance["source_id"].startswith("SRC-DS-") for r in selected))
        self.assertTrue(all(r.contract for r in selected))


if __name__ == "__main__":
    unittest.main()
