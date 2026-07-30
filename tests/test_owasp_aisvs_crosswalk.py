from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from grimoire.registry import load_crosswalk_registry


class OwaspAisvsCrosswalkTests(unittest.TestCase):
    def setUp(self):
        self.crosswalk = load_crosswalk_registry(
            ROOT / "registry" / "crosswalks",
            standards_dir=ROOT / "registry" / "standards",
            root=ROOT,
        )["owasp-aisvs"]

    def test_only_declared_ai_capabilities_activate_aisvs(self):
        ai = {
            "project": {"product_types": ["agentic-automation"]},
            "ai": {"user_facing": True, "automated_decisions": False},
        }
        deterministic = {
            "project": {"product_types": ["authenticated-saas"]},
            "ai": {"user_facing": False, "automated_decisions": False},
        }
        self.assertTrue(self.crosswalk.applies_to(ai))
        self.assertFalse(self.crosswalk.applies_to(deterministic))

    def test_versioned_ids_preserve_human_review_and_mapping_boundary(self):
        self.assertEqual(self.crosswalk.version, "1.0")
        self.assertIn(
            "GRIM-STD-0027",
            self.crosswalk.controls_for("v1.0-C9.2.1"),
        )
        self.assertIn(
            "manual",
            self.crosswalk.evidence_for("v1.0-C9.2.1"),
        )
        self.assertEqual(self.crosswalk.assurance_boundary, "mapping_only")
        self.assertEqual(self.crosswalk.controls_for("v1.01-C9.2.1"), ())


if __name__ == "__main__":
    unittest.main()
