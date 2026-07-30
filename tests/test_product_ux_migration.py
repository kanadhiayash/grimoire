from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from grimoire.registry import load_standard_registry


DOCUMENTS = {
    "standards/product-ux/design-development-handoff.md",
    "standards/product-ux/heuristic-and-interface-quality.md",
    "standards/product-ux/product-design-operations.md",
    "standards/product-ux/ux-evidence.md",
}
CONTRACT_FIELDS = {
    "expected_outcomes", "required_actions", "expected_documents", "acceptance",
    "verification", "evidence", "failure_conditions", "exceptions",
}


class ProductUxMigrationTests(unittest.TestCase):
    def test_product_ux_documents_are_source_linked_normative_records(self):
        inventory = json.loads((ROOT / "inventory/standards-classification.json").read_text("utf-8"))
        classifications = {item["path"]: item for item in inventory["documents"]}
        records = load_standard_registry(ROOT / "registry" / "standards", root=ROOT)
        by_document = {record.human_document: record for record in records.values()}
        self.assertTrue(all(classifications[path]["classification"] == "NORMATIVE" for path in DOCUMENTS))
        for path in DOCUMENTS:
            record = by_document[path]
            self.assertEqual(record.domain, "product-ux")
            self.assertTrue(record.provenance["source_id"].startswith("SRC-PUX-"))
            self.assertEqual(set(record.contract), CONTRACT_FIELDS)


if __name__ == "__main__":
    unittest.main()
