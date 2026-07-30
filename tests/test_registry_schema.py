from __future__ import annotations

import sys
import unittest
from pathlib import Path

try:
    from jsonschema import Draft202012Validator
except ImportError:
    Draft202012Validator = None  # type: ignore[assignment]

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

class RegistrySchemaTests(unittest.TestCase):
    @unittest.skipUnless(
        Draft202012Validator is not None,
        "jsonschema is installed only for schema validation",
    )
    def test_nested_registry_records_and_sources_validate(self):
        from checks.json_schema_check import validate

        self.assertEqual(validate(), [])


if __name__ == "__main__":
    unittest.main()
