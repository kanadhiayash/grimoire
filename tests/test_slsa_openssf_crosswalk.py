from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from grimoire.registry import load_crosswalk_registry


class SlsaOpenSsfCrosswalkTests(unittest.TestCase):
    def setUp(self):
        self.crosswalks = load_crosswalk_registry(
            ROOT / "registry" / "crosswalks",
            standards_dir=ROOT / "registry" / "standards",
            root=ROOT,
        )

    def test_version_locked_release_mappings_are_available(self):
        slsa = self.crosswalks["slsa"]
        scorecard = self.crosswalks["openssf-scorecard"]
        self.assertEqual(slsa.version, "1.2")
        self.assertEqual(scorecard.version, "5.5.0")
        self.assertEqual(slsa.assurance_boundary, "mapping_only")
        self.assertEqual(scorecard.assurance_boundary, "mapping_only")
        self.assertIn("GRIM-STD-0044", slsa.controls_for("SLSA-BUILD-L1"))
        self.assertIn(
            "GRIM-STD-0039",
            scorecard.controls_for("Pinned-Dependencies"),
        )

    def test_missing_release_artifact_never_completes_evidence(self):
        slsa = self.crosswalks["slsa"]
        self.assertFalse(
            slsa.evidence_complete_for(
                "SLSA-BUILD-L1",
                {"automated", "review"},
            )
        )
        self.assertTrue(
            slsa.evidence_complete_for(
                "SLSA-BUILD-L1",
                {"automated", "review", "artifact"},
            )
        )
        self.assertFalse(
            slsa.evidence_complete_for("UNKNOWN", {"artifact", "review"})
        )

    def test_scorecard_heuristics_require_review_not_aggregate_scores(self):
        scorecard = self.crosswalks["openssf-scorecard"]
        for external_id in scorecard.mappings:
            self.assertIn("review", scorecard.evidence_for(external_id))
        self.assertNotIn("Aggregate-Score", scorecard.mappings)


if __name__ == "__main__":
    unittest.main()
