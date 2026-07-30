from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from grimoire.registry import CrosswalkValidationError, load_crosswalk_registry


class NistSsdfCrosswalkTests(unittest.TestCase):
    def test_repository_crosswalk_resolves_in_both_directions(self):
        crosswalks = load_crosswalk_registry(
            ROOT / "registry" / "crosswalks",
            standards_dir=ROOT / "registry" / "standards",
            root=ROOT,
        )
        ssdf = crosswalks["nist-ssdf"]
        self.assertEqual(ssdf.version, "1.1")
        self.assertEqual(ssdf.assurance_boundary, "mapping_only")
        self.assertIn("GRIM-STD-0042", ssdf.controls_for("PO.3.1"))
        self.assertIn("PO.3.1", ssdf.external_ids_for("GRIM-STD-0042"))

    def test_unknown_external_id_and_control_fail(self):
        base = {
            "schema_version": 1,
            "framework": {
                "id": "nist-ssdf",
                "title": "NIST SSDF",
                "version": "1.1",
                "version_lock": "1.1",
                "official_url": "https://csrc.nist.gov/pubs/sp/800/218/final",
                "source_license": "NIST-publication-terms",
                "license_review": "summary-identifiers-only",
                "review_date": "2026-07-30",
                "expires_on": "2027-07-30",
                "assurance_boundary": "mapping_only",
            },
            "applicability": {},
            "known_external_ids": ["PO.1.1"],
            "mappings": [
                {
                    "external_id": "UNKNOWN.1",
                    "grimoire_control_ids": ["GRIM-STD-9999"],
                    "rationale": "invalid fixture",
                    "evidence_classes": ["review"],
                }
            ],
        }
        with tempfile.TemporaryDirectory() as directory:
            crosswalk_dir = Path(directory) / "crosswalks" / "nist"
            crosswalk_dir.mkdir(parents=True)
            (crosswalk_dir / "crosswalk.json").write_text(
                json.dumps(base), encoding="utf-8"
            )
            with self.assertRaises(CrosswalkValidationError) as raised:
                load_crosswalk_registry(
                    Path(directory) / "crosswalks",
                    standards_dir=ROOT / "registry" / "standards",
                    root=ROOT,
                )
        self.assertIn("unknown_external_id", raised.exception.reason_codes)
        self.assertIn("unknown_grimoire_control", raised.exception.reason_codes)

    def test_version_change_requires_an_explicit_lock_update(self):
        value = json.loads(
            (
                ROOT
                / "registry"
                / "crosswalks"
                / "nist-ssdf"
                / "crosswalk.json"
            ).read_text("utf-8")
        )
        value["framework"]["version"] = "1.2"
        with tempfile.TemporaryDirectory() as directory:
            crosswalk_dir = Path(directory) / "crosswalks" / "nist"
            crosswalk_dir.mkdir(parents=True)
            (crosswalk_dir / "crosswalk.json").write_text(
                json.dumps(value), encoding="utf-8"
            )
            with self.assertRaises(CrosswalkValidationError) as raised:
                load_crosswalk_registry(
                    Path(directory) / "crosswalks",
                    standards_dir=ROOT / "registry" / "standards",
                    root=ROOT,
                )
        self.assertIn("version_review_required", raised.exception.reason_codes)


if __name__ == "__main__":
    unittest.main()
