from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "surface_activation_check", ROOT / "checks" / "surface_activation_check.py"
)
module = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = module
assert SPEC.loader is not None
SPEC.loader.exec_module(module)


class SurfaceActivationTests(unittest.TestCase):
    def test_policy_is_valid(self):
        self.assertEqual(module.validate_policy(), [])

    def test_full_local_runtime(self):
        evidence = module.SurfaceEvidence(
            "local_harness", runtime_capability=True, project_contract=True
        )
        self.assertEqual(module.classify(evidence), "RUNTIME_FULL")

    def test_partial_local_runtime(self):
        evidence = module.SurfaceEvidence("local_harness", project_contract=True)
        self.assertEqual(module.classify(evidence), "RUNTIME_PARTIAL")

    def test_browser_project_pack(self):
        evidence = module.SurfaceEvidence(
            "browser_project", source_pack_complete=True
        )
        self.assertEqual(module.classify(evidence), "PROJECT_SIMULATION")

    def test_browser_chat_pack(self):
        evidence = module.SurfaceEvidence("browser_chat", source_pack_complete=True)
        self.assertEqual(module.classify(evidence), "CHAT_SIMULATION")

    def test_instruction_only(self):
        evidence = module.SurfaceEvidence("browser_project", some_instructions=True)
        self.assertEqual(module.classify(evidence), "INSTRUCTION_ONLY")

    def test_unknown_surface(self):
        evidence = module.SurfaceEvidence("unknown")
        self.assertEqual(module.classify(evidence), "NOT_VERIFIED")

    def test_uninspectable_surface(self):
        evidence = module.SurfaceEvidence(
            "local_harness", inspection_available=False
        )
        self.assertEqual(module.classify(evidence), "NOT_VERIFIED")


if __name__ == "__main__":
    unittest.main()
