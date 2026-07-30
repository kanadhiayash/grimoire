from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from grimoire.registry import load_standard_registry


class SecurityMigrationTests(unittest.TestCase):
    def test_security_records_are_defensive_source_linked_contracts(self):
        records = load_standard_registry(ROOT / "registry" / "standards", root=ROOT)
        selected = [record for record in records.values() if record.domain == "security"]
        self.assertEqual(len(selected), 2)
        self.assertTrue(
            all(record.provenance["source_id"].startswith("SRC-SEC-") for record in selected)
        )
        self.assertTrue(all(record.contract for record in selected))
        red_team = next(record for record in selected if record.id == "GRIM-STD-0025")
        self.assertTrue(
            any("live external testing" in item for item in red_team.contract["exceptions"])
        )


if __name__ == "__main__":
    unittest.main()
