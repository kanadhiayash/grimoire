import json
import tempfile
import unittest
from pathlib import Path

from scripts.project_orchestrator import compile_project, validate_manifest


class ProjectOrchestratorTests(unittest.TestCase):
    def valid_manifest(self):
        return {
            "schema_version": 1,
            "project": {"name": "Example Product", "lifecycle_stage": "BUILD_READY", "product_types": ["consumer-mobile", "ai-assistant"]},
            "users": ["authenticated", "accessibility-needs"],
            "markets": ["Canada"],
            "platforms": ["ios", "android"],
            "stack": {"languages": ["typescript"], "frameworks": ["react-native"]},
            "data": {"personal_data": True, "sensitive": ["location"]},
            "ai": {"user_facing": True, "automated_decisions": False},
            "risk": {"level": "high"},
            "standards": {"version": "0.4.0"},
            "zeref": {"mode": "standard", "cost_ceiling": "bounded"},
            "unknowns": [],
        }

    def test_valid_manifest_has_no_errors(self):
        self.assertEqual(validate_manifest(self.valid_manifest()), [])

    def test_compile_writes_complete_one_read_pack(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            receipt = compile_project(self.valid_manifest(), output)
            expected = {"AI_CONTEXT.md", "CONTROL_PACK.json", "PROJECT_STATUS.json", "EXPECTED_OUTCOMES.md", "REQUIRED_DOCUMENTS.md", "DOCUMENT_SCHEMAS.json", "REQUIRED_GATES.md", "ACCEPTANCE_MATRIX.md", "VERIFICATION_PLAN.md", "SOURCE_MANIFEST.json", "ZEREF_EXECUTION_PROFILE.json", "EXECUTION_RECEIPT.json"}
            self.assertEqual({path.name for path in output.iterdir()}, expected)
            self.assertEqual(receipt["status"], "PASS")
            context = (output / "AI_CONTEXT.md").read_text(encoding="utf-8")
            self.assertIn("Example Product", context)
            self.assertIn("Minimum Correct Change", context)

    def test_unknowns_make_status_partial(self):
        manifest = self.valid_manifest()
        manifest["unknowns"] = ["Data residency is not confirmed"]
        with tempfile.TemporaryDirectory() as directory:
            receipt = compile_project(manifest, Path(directory))
            self.assertEqual(receipt["status"], "PARTIAL")

    def test_invalid_lifecycle_is_rejected(self):
        manifest = self.valid_manifest()
        manifest["project"]["lifecycle_stage"] = "DONE"
        errors = validate_manifest(manifest)
        self.assertTrue(any("lifecycle_stage" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
