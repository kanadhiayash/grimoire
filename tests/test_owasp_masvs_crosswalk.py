from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from grimoire.registry import load_crosswalk_registry


class OwaspMasvsCrosswalkTests(unittest.TestCase):
    def setUp(self):
        self.crosswalk = load_crosswalk_registry(
            ROOT / "registry" / "crosswalks",
            standards_dir=ROOT / "registry" / "standards",
            root=ROOT,
        )["owasp-masvs"]

    def test_only_mobile_platforms_activate_masvs(self):
        mobile = {
            "project": {"product_types": ["consumer-mobile"]},
            "platforms": ["ios"],
        }
        web = {
            "project": {"product_types": ["authenticated-saas"]},
            "platforms": ["web"],
        }
        self.assertTrue(self.crosswalk.applies_to(mobile))
        self.assertFalse(self.crosswalk.applies_to(web))

    def test_version_and_evidence_classes_remain_distinct(self):
        self.assertEqual(self.crosswalk.version, "2.1.0")
        self.assertEqual(
            self.crosswalk.evidence_for("MASVS-PLATFORM-1"),
            ("manual", "platform"),
        )
        self.assertNotEqual(
            self.crosswalk.evidence_for("MASVS-PLATFORM-1"),
            ("automated",),
        )
        self.assertEqual(self.crosswalk.assurance_boundary, "mapping_only")


if __name__ == "__main__":
    unittest.main()
