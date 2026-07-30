from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from checks.corpus_classification_check import (  # noqa: E402
    CLASSIFICATIONS,
    validate_classification,
)


class CorpusClassificationTests(unittest.TestCase):
    def test_repository_inventory_is_complete_and_normative_matches_registry(self):
        self.assertEqual(validate_classification(ROOT), [])

        inventory = json.loads(
            (ROOT / "inventory" / "standards-classification.json").read_text("utf-8")
        )
        paths = [entry["path"] for entry in inventory["documents"]]
        discovered = sorted(
            path.relative_to(ROOT).as_posix()
            for path in (ROOT / "standards").rglob("*.md")
        )
        self.assertEqual(paths, discovered)
        self.assertTrue({entry["classification"] for entry in inventory["documents"]} <= CLASSIFICATIONS)

    def test_unclassified_unknown_and_contradictory_entries_fail(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "standards" / "universal").mkdir(parents=True)
            (root / "registry" / "standards").mkdir(parents=True)
            (root / "standards" / "universal" / "one.md").write_text("# One\n", encoding="utf-8")
            (root / "standards" / "universal" / "two.md").write_text("# Two\n", encoding="utf-8")
            (root / "registry" / "standards" / "GRIM-STD-0001.json").write_text(
                json.dumps({"id": "GRIM-STD-0001", "human_document": "standards/universal/one.md"}),
                encoding="utf-8",
            )
            (root / "inventory").mkdir()
            (root / "inventory" / "standards-classification.json").write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "documents": [
                            {
                                "path": "standards/universal/one.md",
                                "classification": "NORMATIVE",
                                "domain": "universal",
                                "owner": "owner",
                                "review_status": "CURRENT",
                                "migration_target": "GRIM-STD-0001",
                            },
                            {
                                "path": "standards/universal/one.md",
                                "classification": "UNKNOWN",
                                "domain": "universal",
                                "owner": "owner",
                                "review_status": "CURRENT",
                                "migration_target": "none",
                            },
                        ],
                    }
                ),
                encoding="utf-8",
            )

            errors = validate_classification(root)

        self.assertIn("duplicate_path:standards/universal/one.md", errors)
        self.assertIn("unknown_classification:standards/universal/one.md", errors)
        self.assertIn("unclassified_document:standards/universal/two.md", errors)

    def test_only_normative_documents_with_registry_records_are_eligible(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "standards" / "universal").mkdir(parents=True)
            (root / "registry" / "standards").mkdir(parents=True)
            document = root / "standards" / "universal" / "legacy.md"
            document.write_text("# Legacy\n", encoding="utf-8")
            (root / "inventory").mkdir()
            (root / "inventory" / "standards-classification.json").write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "documents": [
                            {
                                "path": "standards/universal/legacy.md",
                                "classification": "NORMATIVE",
                                "domain": "universal",
                                "owner": "owner",
                                "review_status": "CURRENT",
                                "migration_target": "GRIM-STD-0001",
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )

            errors = validate_classification(root)

        self.assertIn("normative_record_missing:standards/universal/legacy.md", errors)


if __name__ == "__main__":
    unittest.main()
