from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from grimoire.registry import load_crosswalk_registry


class OwaspAsvsCrosswalkTests(unittest.TestCase):
    def setUp(self):
        self.crosswalk = load_crosswalk_registry(
            ROOT / "registry" / "crosswalks",
            standards_dir=ROOT / "registry" / "standards",
            root=ROOT,
        )["owasp-asvs"]

    def test_versioned_ids_resolve_without_assurance_claim(self):
        self.assertEqual(self.crosswalk.version, "5.0.0")
        self.assertIn(
            "GRIM-STD-0022",
            self.crosswalk.controls_for("v5.0.0-1.2.5"),
        )
        self.assertEqual(self.crosswalk.assurance_boundary, "mapping_only")
        self.assertEqual(self.crosswalk.controls_for("v4.0.3-1.2.5"), ())

    def test_web_profile_is_selected_but_mobile_only_profile_is_not(self):
        web = {
            "project": {"product_types": ["authenticated-saas"]},
            "platforms": ["web"],
        }
        mobile = {
            "project": {"product_types": ["consumer-mobile"]},
            "platforms": ["ios"],
        }
        self.assertTrue(self.crosswalk.applies_to(web))
        self.assertFalse(self.crosswalk.applies_to(mobile))


if __name__ == "__main__":
    unittest.main()
