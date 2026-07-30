from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from grimoire.registry import load_crosswalk_registry


class Wcag22CrosswalkTests(unittest.TestCase):
    def setUp(self):
        self.crosswalk = load_crosswalk_registry(
            ROOT / "registry" / "crosswalks",
            standards_dir=ROOT / "registry" / "standards",
            root=ROOT,
        )["wcag-2.2"]

    def test_all_level_a_and_aa_criteria_are_versioned_and_mapped(self):
        self.assertEqual(self.crosswalk.version, "2.2")
        self.assertEqual(len(self.crosswalk.mappings), 55)
        self.assertEqual(
            set(self.crosswalk.external_levels.values()),
            {"A", "AA"},
        )
        self.assertTrue(
            all(
                "GRIM-STD-0003" in controls
                for controls in self.crosswalk.mappings.values()
            )
        )

    def test_automated_evidence_never_stands_alone(self):
        for criterion in self.crosswalk.mappings:
            evidence = self.crosswalk.evidence_for(criterion)
            self.assertIn("manual", evidence)
            self.assertIn("assistive_technology", evidence)
            self.assertNotEqual(evidence, ("automated",))
        self.assertEqual(self.crosswalk.assurance_boundary, "mapping_only")


if __name__ == "__main__":
    unittest.main()
