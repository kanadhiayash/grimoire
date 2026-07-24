from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "instructions"
MANIFEST = json.loads(
    (PACK / "instructions-manifest.json").read_text(encoding="utf-8")
)
ES = MANIFEST["canonical_sources"]["engineering_standards"]
ZEREF = MANIFEST["canonical_sources"]["zeref_memory_engine"]
STATUSES = set(MANIFEST["completion_statuses"])


class PersonalInstructionPackTests(unittest.TestCase):
    def test_all_files_exist_and_fit_budgets(self) -> None:
        for name, config in MANIFEST["files"].items():
            path = PACK / name
            self.assertTrue(path.is_file(), name)
            self.assertLessEqual(
                len(path.read_text(encoding="utf-8")),
                config["max_characters"],
                name,
            )

    def test_all_files_preserve_provenance_and_completion_statuses(self) -> None:
        for name in MANIFEST["files"]:
            text = (PACK / name).read_text(encoding="utf-8")
            self.assertIn(ES, text, name)
            self.assertIn(ZEREF, text, name)
            for status in STATUSES:
                self.assertIn(status, text, name)

    def test_all_files_preserve_cost_and_approval_guards(self) -> None:
        for name in MANIFEST["files"]:
            text = (PACK / name).read_text(encoding="utf-8").lower()
            self.assertIn("lowest-cost sufficient", text, name)
            self.assertIn("explicit approval", text, name)
            self.assertTrue(
                "do not claim" in text or "never claim" in text,
                name,
            )

    def test_chatgpt_project_is_self_contained(self) -> None:
        text = (
            PACK / "06_ChatGPT_Project_Folder_Instructions.md"
        ).read_text(encoding="utf-8")
        self.assertIn("override global custom instructions", text)
        for required in (
            "SURFACE_BOOT.md",
            "SOURCES_MANIFEST.json",
            "PROJECT_STATE.md",
            "MEMORY_STATE.md",
        ):
            self.assertIn(required, text)

    def test_local_surfaces_defer_to_repository_contracts(self) -> None:
        codex = (
            PACK / "07_Codex_Global_Instructions_Customization.md"
        ).read_text(encoding="utf-8")
        cowork = (
            PACK / "04_Claude_Cowork_Project_Folder_Instructions.md"
        ).read_text(encoding="utf-8")
        self.assertIn("nearest repository `AGENTS.md`", codex)
        self.assertIn("Read the nearest `AGENTS.md`", cowork)
        self.assertIn("`CLAUDE.md`", cowork)

    def test_no_em_dash_or_inflated_banned_phrases(self) -> None:
        banned = (
            "—",
            "revolutionize",
            "seamlessly",
            "delve into",
            "game-changer",
            "cutting-edge",
            "groundbreaking",
            "paradigm shift",
            "synergy",
        )
        for name in MANIFEST["files"]:
            text = (PACK / name).read_text(encoding="utf-8").lower()
            for term in banned:
                self.assertNotIn(term.lower(), text, name)


if __name__ == "__main__":
    unittest.main()
