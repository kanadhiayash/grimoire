from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from grimoire.registry import load_standard_registry


class LegalPrivacyMigrationTests(unittest.TestCase):
    def test_legal_privacy_record_has_full_conservative_contract(self):
        records = load_standard_registry(ROOT / "registry" / "standards", root=ROOT)
        selected = [record for record in records.values() if record.domain == "legal-privacy"]
        self.assertEqual(len(selected), 1)
        self.assertEqual(selected[0].id, "GRIM-STD-0005")
        self.assertTrue(selected[0].contract)
        self.assertTrue(
            any("COMPLIANT" in item for item in selected[0].contract["failure_conditions"])
        )


if __name__ == "__main__":
    unittest.main()
