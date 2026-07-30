from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from grimoire.registry import load_standard_registry


class AiAgentsMigrationTests(unittest.TestCase):
    def test_ai_agent_records_are_source_linked_contracts(self):
        records = load_standard_registry(ROOT / "registry" / "standards", root=ROOT)
        selected = [record for record in records.values() if record.domain == "ai-agents"]
        self.assertEqual(len(selected), 9)
        self.assertTrue(
            all(record.provenance["source_id"].startswith("SRC-AI-") for record in selected)
        )
        self.assertTrue(all(record.contract for record in selected))
        zeref = next(record for record in selected if record.id == "GRIM-STD-0034")
        self.assertTrue(
            any("Zeref" in item and "modify" in item for item in zeref.contract["exceptions"])
        )


if __name__ == "__main__":
    unittest.main()
