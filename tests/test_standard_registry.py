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

from grimoire.registry import RegistryValidationError, load_standard_registry


class StandardRegistryTests(unittest.TestCase):
    def write_registry(self, root: Path, records: list[dict[str, object]]) -> Path:
        registry = root / "registry" / "standards"
        registry.mkdir(parents=True)
        for index, record in enumerate(records):
            (registry / f"record-{index}.json").write_text(
                json.dumps(record, indent=2) + "\n",
                encoding="utf-8",
            )
        return registry

    def valid_record(self, root: Path, *, standard_id: str = "GRIM-STD-0001"):
        doc = root / "standards" / "universal" / "verification.md"
        doc.parent.mkdir(parents=True, exist_ok=True)
        doc.write_text("# Verification\n", encoding="utf-8")
        return {
            "id": standard_id,
            "version": "1.0.0",
            "status": "normative",
            "domain": "universal",
            "requirement_level": "must",
            "title": "Verification",
            "owner": "Standards Orchestrator",
            "review_date": "2026-07-27",
            "human_document": "standards/universal/verification.md",
            "provenance": {
                "source_type": "local_policy",
                "source_id": "AGENTS.md",
            },
            "applicability": {"all": []},
        }

    def test_valid_registry_loads_records_by_id(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            registry = self.write_registry(root, [self.valid_record(root)])

            records = load_standard_registry(registry, root=root)

            self.assertEqual(tuple(records), ("GRIM-STD-0001",))

    def test_duplicate_ids_missing_owner_and_missing_provenance_fail(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            first = self.valid_record(root)
            second = self.valid_record(root)
            del second["owner"]
            del second["provenance"]
            registry = self.write_registry(root, [first, second])

            with self.assertRaises(RegistryValidationError) as raised:
                load_standard_registry(registry, root=root)

            self.assertIn("duplicate_id", raised.exception.reason_codes)
            self.assertIn("missing_required", raised.exception.reason_codes)

    def test_guidance_draft_example_and_superseded_cannot_compile_normative(self):
        for status in ("guidance", "draft", "example", "superseded"):
            with self.subTest(status=status):
                with tempfile.TemporaryDirectory() as directory:
                    root = Path(directory)
                    record = self.valid_record(root)
                    record["status"] = status
                    registry = self.write_registry(root, [record])

                    with self.assertRaises(RegistryValidationError) as raised:
                        load_standard_registry(registry, root=root)

                    self.assertIn("non_normative_record", raised.exception.reason_codes)

    def test_human_document_must_resolve_inside_repository(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            record = self.valid_record(root)
            record["human_document"] = "../outside.md"
            registry = self.write_registry(root, [record])

            with self.assertRaises(RegistryValidationError) as raised:
                load_standard_registry(registry, root=root)

            self.assertIn("path_escape", raised.exception.reason_codes)

    def test_repository_registry_validates(self):
        records = load_standard_registry(
            ROOT / "registry" / "standards",
            root=ROOT,
        )

        self.assertIn("GRIM-STD-0001", records)


if __name__ == "__main__":
    unittest.main()
