import json
import subprocess
import sys
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from grimoire.errors import ManifestValidationError  # noqa: E402
from grimoire.models.manifest import RiskConfig, ValidatedManifest  # noqa: E402
from scripts.project_orchestrator import OUTPUT_FILES, compile_project, validate_manifest


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

    def test_valid_manifest_returns_immutable_normalized_model(self):
        manifest = validate_manifest(self.valid_manifest())
        self.assertIsInstance(manifest, ValidatedManifest)
        self.assertEqual(manifest.project.name, "Example Product")
        self.assertEqual(manifest.project.product_types, ("consumer-mobile", "ai-assistant"))

    def test_compile_writes_complete_one_read_pack(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            receipt = compile_project(self.valid_manifest(), output)
            expected = set(OUTPUT_FILES)
            self.assertEqual({path.name for path in output.iterdir()}, expected)
            self.assertEqual(receipt["pack_generation_status"], "PASS")
            self.assertEqual(receipt["status"], "NOT_VERIFIED")
            self.assertEqual(
                receipt["status_report"]["dimensions"][
                    "MANIFEST_VALIDATION_STATUS"
                ],
                {
                    "status": "PASS",
                    "reason_codes": ["strict_manifest_validated"],
                },
            )
            self.assertEqual(
                receipt["status_report"]["dimensions"][
                    "PROJECT_READINESS_STATUS"
                ]["status"],
                "NOT_VERIFIED",
            )
            self.assertEqual(
                receipt["status_report"]["dimensions"][
                    "RELEASE_ASSURANCE_STATUS"
                ]["status"],
                "NOT_VERIFIED",
            )
            context = (output / "AI_CONTEXT.md").read_text(encoding="utf-8")
            self.assertIn("Example Product", context)
            self.assertIn("Minimum Correct Change", context)

    def test_unknowns_do_not_raise_unverified_aggregate(self):
        manifest = self.valid_manifest()
        manifest["unknowns"] = ["Data residency is not confirmed"]
        with tempfile.TemporaryDirectory() as directory:
            receipt = compile_project(manifest, Path(directory))
            self.assertEqual(receipt["status"], "NOT_VERIFIED")
            self.assertIn(
                "declared_unknowns_present",
                receipt["status_report"]["dimensions"][
                    "PROJECT_READINESS_STATUS"
                ]["reason_codes"],
            )

    def test_invalid_lifecycle_is_rejected(self):
        manifest = self.valid_manifest()
        manifest["project"]["lifecycle_stage"] = "DONE"
        with self.assertRaises(ManifestValidationError) as raised:
            validate_manifest(manifest)
        self.assertTrue(
            any(
                issue.code == "unsupported_value"
                and issue.path == "$.project.lifecycle_stage"
                for issue in raised.exception.issues
            )
        )

    def test_compile_revalidates_manually_constructed_models(self):
        manifest = validate_manifest(self.valid_manifest())
        invalid = replace(manifest, risk=RiskConfig(level="impossible"))
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "compiled"
            with self.assertRaises(ManifestValidationError):
                compile_project(invalid, output)
            self.assertFalse(output.exists())

    def test_audited_false_pass_fixture_is_now_not_verified(self):
        root = Path(__file__).resolve().parents[1]
        fixture = (
            root
            / "benchmarks"
            / "audit"
            / "2026-07-27"
            / "fixtures"
            / "false-project-readiness.json"
        )
        manifest = json.loads(fixture.read_text(encoding="utf-8"))
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            receipt = compile_project(manifest, output)
            project_status = json.loads(
                (output / "PROJECT_STATUS.json").read_text(encoding="utf-8")
            )

        self.assertEqual(receipt["pack_generation_status"], "PASS")
        self.assertEqual(receipt["status"], "NOT_VERIFIED")
        self.assertEqual(project_status["status"], "NOT_VERIFIED")
        self.assertEqual(
            project_status["status_report"]["dimensions"][
                "PROJECT_READINESS_STATUS"
            ]["status"],
            "NOT_VERIFIED",
        )

    def test_direct_cli_entrypoint_remains_available(self):
        root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "compiled"
            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/project_orchestrator.py",
                    "--manifest",
                    "templates/project/project.json",
                    "--output",
                    str(output),
                ],
                cwd=root,
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(
                completed.returncode,
                0,
                msg=f"stdout:\n{completed.stdout}\nstderr:\n{completed.stderr}",
            )
            self.assertEqual(len(list(output.iterdir())), len(OUTPUT_FILES))


if __name__ == "__main__":
    unittest.main()
