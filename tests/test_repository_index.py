import json
import tempfile
import unittest
from pathlib import Path

from checks.repository_index_check import validate_index


class RepositoryIndexTests(unittest.TestCase):
    def make_repo(self) -> Path:
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        root = Path(temp.name)
        (root / "VERSION").write_text("0.2.0\n", encoding="utf-8")
        for relative in (
            "AGENTS.md",
            "README.md",
            "policies/baseline.json",
            "policies/ai-operations.json",
            "policies/surface-activation.json",
            "scripts/grimoire.py",
            "docs/operations/quickstart.md",
            "docs/operations/agent-entrypoint.md",
            "adapters/claude/ZEREF_ACTIVATION.global.md",
        ):
            path = root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(
                "{}\n" if path.suffix == ".json" else "# file\n",
                encoding="utf-8",
            )
        return root

    def index(self) -> dict:
        return {
            "schema_version": 1,
            "standard_version": "0.2.0",
            "repository": "kanadhiayash/grimoire",
            "canonical_sources": {
                "repository_contract": "AGENTS.md",
                "baseline_policy": "policies/baseline.json",
                "ai_operations_policy": "policies/ai-operations.json",
                "surface_activation_policy": "policies/surface-activation.json",
            },
            "entrypoints": {
                "human": ["README.md", "docs/operations/quickstart.md"],
                "agent": ["AGENTS.md", "docs/operations/agent-entrypoint.md"],
            },
            "commands": {
                "status": {
                    "entrypoint": "scripts/grimoire.py",
                    "argv": [
                        "python3",
                        "scripts/grimoire.py",
                        "status",
                        "--json",
                    ],
                    "purpose": "Report repository state",
                }
            },
            "surfaces": {
                "claude-code": {
                    "mode": "local_harness",
                    "adapter": "adapters/claude/ZEREF_ACTIVATION.global.md",
                }
            },
            "verification": {
                "commands": ["python3 scripts/grimoire.py check"]
            },
        }

    def test_valid_index_passes(self):
        root = self.make_repo()
        (root / "REPOSITORY_INDEX.json").write_text(
            json.dumps(self.index()), encoding="utf-8"
        )
        self.assertEqual(validate_index(root), [])

    def test_missing_agent_entrypoint_fails(self):
        root = self.make_repo()
        index = self.index()
        index["entrypoints"]["agent"].append("docs/operations/missing.md")
        (root / "REPOSITORY_INDEX.json").write_text(
            json.dumps(index), encoding="utf-8"
        )
        errors = validate_index(root)
        self.assertTrue(any("missing path" in error for error in errors))

    def test_path_escape_is_rejected(self):
        root = self.make_repo()
        index = self.index()
        index["canonical_sources"]["escape"] = "../secret.txt"
        (root / "REPOSITORY_INDEX.json").write_text(
            json.dumps(index), encoding="utf-8"
        )
        errors = validate_index(root)
        self.assertTrue(any("unsafe path" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
