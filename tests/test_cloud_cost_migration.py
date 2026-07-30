from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from grimoire.registry import load_standard_registry


class CloudCostMigrationTests(unittest.TestCase):
    def test_cloud_cost_records_are_source_linked_contracts(self):
        records = load_standard_registry(ROOT / "registry" / "standards", root=ROOT)
        selected = [record for record in records.values() if record.domain == "cloud-cost"]
        self.assertEqual(len(selected), 3)
        self.assertTrue(
            all(record.provenance["source_id"].startswith("SRC-CLOUD-") for record in selected)
        )
        self.assertTrue(all(record.contract for record in selected))


if __name__ == "__main__":
    unittest.main()
