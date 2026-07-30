from __future__ import annotations

import json
import sys
import tempfile
import unittest
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from grimoire.registry import RegistryValidationError, load_standard_registry


UNIVERSAL_GOVERNANCE_DOCUMENTS = {
    "standards/universal/change-discipline.md",
    "standards/universal/documentation.md",
    "standards/universal/naming-and-placement.md",
    "standards/universal/priority-severity-risk.md",
    "standards/universal/source-discipline.md",
    "standards/universal/standard-authoring.md",
    "standards/universal/verification.md",
    "standards/engineering/minimum-correct-change.md",
    "standards/engineering/testing.md",
}


class UniversalGovernanceMigrationTests(unittest.TestCase):
    def test_all_universal_governance_documents_are_normative_and_source_linked(self):
        classification = json.loads(
            (ROOT / "inventory/standards-classification.json").read_text(
                encoding="utf-8"
            )
        )
        records = load_standard_registry(ROOT / "registry" / "standards", root=ROOT)
        records_by_document = {record.human_document: record for record in records.values()}

        classified = {
            item["path"]: item
            for item in classification["documents"]
            if item["path"] in UNIVERSAL_GOVERNANCE_DOCUMENTS
        }
        self.assertEqual(set(classified), UNIVERSAL_GOVERNANCE_DOCUMENTS)
        self.assertTrue(
            all(item["classification"] == "NORMATIVE" for item in classified.values())
        )
        self.assertEqual(set(records_by_document) & UNIVERSAL_GOVERNANCE_DOCUMENTS, UNIVERSAL_GOVERNANCE_DOCUMENTS)
        for document in UNIVERSAL_GOVERNANCE_DOCUMENTS:
            record = records_by_document[document]
            self.assertEqual(record.provenance["source_type"], "local_policy")
            self.assertTrue(record.provenance["source_id"].startswith("SRC-UG-"))
            self.assertEqual(
                set(record.contract),
                {
                    "expected_outcomes",
                    "required_actions",
                    "expected_documents",
                    "acceptance",
                    "verification",
                    "evidence",
                    "failure_conditions",
                    "exceptions",
                },
            )

    def test_expired_source_review_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            document = root / "standards" / "universal" / "example.md"
            document.parent.mkdir(parents=True)
            document.write_text("# Example\n", encoding="utf-8")
            registry = root / "registry" / "standards"
            registry.mkdir(parents=True)
            source_dir = root / "registry" / "sources"
            source_dir.mkdir(parents=True)
            (source_dir / "universal-governance.json").write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "sources": [
                            {
                                "id": "SRC-UG-EXAMPLE",
                                "source_type": "local_policy",
                                "path": "standards/universal/example.md",
                                "review_date": (date.today() - timedelta(days=1)).isoformat(),
                                "expires_on": (date.today() - timedelta(days=1)).isoformat(),
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            (registry / "example.json").write_text(
                json.dumps(
                    {
                        "id": "GRIM-STD-0001",
                        "version": "1.0.0",
                        "status": "normative",
                        "domain": "universal-governance",
                        "requirement_level": "must",
                        "title": "Example",
                        "owner": "Standards Orchestrator",
                        "review_date": date.today().isoformat(),
                        "human_document": "standards/universal/example.md",
                        "provenance": {
                            "source_type": "local_policy",
                            "source_id": "SRC-UG-EXAMPLE",
                        },
                        "applicability": {"all": []},
                    }
                ),
                encoding="utf-8",
            )

            with self.assertRaises(RegistryValidationError) as raised:
                load_standard_registry(registry, root=root)

            self.assertIn("expired_source_review", raised.exception.reason_codes)


if __name__ == "__main__":
    unittest.main()
