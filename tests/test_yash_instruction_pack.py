import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "instructions/personal/yash"


class YashInstructionPackTests(unittest.TestCase):
    def test_all_manifest_files_exist_and_fit_budgets(self):
        manifest = json.loads((PACK / "manifest.json").read_text(encoding="utf-8"))
        for name, maximum in manifest["files"].items():
            path = PACK / name
            self.assertTrue(path.is_file(), name)
            self.assertLessEqual(len(path.read_text(encoding="utf-8")), maximum, name)

    def test_each_surface_uses_orchestrator_and_zeref(self):
        manifest = json.loads((PACK / "manifest.json").read_text(encoding="utf-8"))
        for name in manifest["files"]:
            text = (PACK / name).read_text(encoding="utf-8")
            self.assertIn("Standards Orchestrator", text, name)
            self.assertIn("Zeref", text, name)

    def test_personal_overlay_cannot_weaken_neutral_policy(self):
        manifest = json.loads((PACK / "manifest.json").read_text(encoding="utf-8"))
        self.assertFalse(manifest["neutral_policy_can_be_weakened"])


if __name__ == "__main__":
    unittest.main()
