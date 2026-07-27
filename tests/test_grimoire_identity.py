from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEXT_SUFFIXES = {".md", ".json", ".py", ".yml", ".yaml", ".toml", ".txt", ".sh"}
OLD_SLUG = "kanadhiayash/engineering-standards"
OLD_URL = "https://github.com/kanadhiayash/engineering-standards"
NEW_SLUG = "kanadhiayash/grimoire"
NEW_URL = "https://github.com/kanadhiayash/grimoire"


def repository_text_files() -> list[Path]:
    files: list[Path] = []
    for path in ROOT.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        if any(part in {".git", "artifacts", "dist", "__pycache__"} for part in path.parts):
            continue
        files.append(path)
    return sorted(files)


class GrimoireIdentityTests(unittest.TestCase):
    def test_legacy_repository_slug_and_url_are_removed(self) -> None:
        offenders: list[str] = []
        for path in repository_text_files():
            if path == Path(__file__):
                continue
            text = path.read_text(encoding="utf-8")
            if OLD_SLUG in text or OLD_URL in text:
                offenders.append(str(path.relative_to(ROOT)))
        self.assertEqual([], offenders, f"legacy repository references remain: {offenders}")

    def test_repository_index_declares_grimoire_identity(self) -> None:
        index = json.loads((ROOT / "REPOSITORY_INDEX.json").read_text(encoding="utf-8"))
        self.assertEqual(NEW_SLUG, index["repository"])
        self.assertEqual("Grimoire", index["display_name"])
        self.assertEqual(NEW_URL, index["canonical_url"])

    def test_instruction_manifests_use_grimoire_provenance(self) -> None:
        root_manifest = json.loads(
            (ROOT / "instructions" / "instructions-manifest.json").read_text(encoding="utf-8")
        )
        personal_manifest = json.loads(
            (ROOT / "instructions" / "personal" / "yash" / "manifest.json").read_text(encoding="utf-8")
        )
        self.assertEqual(NEW_URL, root_manifest["canonical_sources"]["grimoire"])
        self.assertEqual(NEW_URL, personal_manifest["canonical_sources"]["grimoire"])
        self.assertNotIn("engineering_standards", root_manifest["canonical_sources"])
        self.assertNotIn("engineering_standards", personal_manifest["canonical_sources"])

    def test_legacy_cli_alias_is_documented_without_being_canonical(self) -> None:
        migration = (ROOT / "docs" / "migrations" / "0.5.0-grimoire.md").read_text(encoding="utf-8")
        self.assertIn("--grimoire-commit", migration)
        self.assertIn("deprecated compatibility alias", migration)


if __name__ == "__main__":
    unittest.main()
