from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from grimoire.registry import load_standard_registry


class ApiMigrationTests(unittest.TestCase):
    def test_api_record_is_normative_source_linked_contract(self):
        records = load_standard_registry(ROOT / "registry" / "standards", root=ROOT)
        selected = [r for r in records.values() if r.domain == "api"]
        self.assertEqual(len(selected), 1)
        self.assertEqual(selected[0].provenance["source_id"], "SRC-API-INTEGRATION")
        self.assertTrue(selected[0].contract)


if __name__ == "__main__":
    unittest.main()
