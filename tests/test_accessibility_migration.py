from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from grimoire.registry import load_standard_registry


class AccessibilityMigrationTests(unittest.TestCase):
    def test_accessibility_record_has_reviewed_source_and_full_contract(self):
        record = load_standard_registry(ROOT / "registry" / "standards", root=ROOT)["GRIM-STD-0003"]
        self.assertEqual(record.domain, "accessibility")
        self.assertEqual(record.provenance["source_id"], "SRC-A11Y-REQUIREMENTS")
        self.assertEqual(set(record.contract), {"expected_outcomes", "required_actions", "expected_documents", "acceptance", "verification", "evidence", "failure_conditions", "exceptions"})


if __name__ == "__main__":
    unittest.main()
