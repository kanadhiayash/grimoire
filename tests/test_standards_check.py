from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from checks import standards_check  # noqa: E402


class StandardsCheckTests(unittest.TestCase):
    def test_all_repository_checks_pass(self) -> None:
        failures = [
            result
            for result in standards_check.run_checks()
            if not result.passed
        ]
        self.assertEqual([], failures)

    def test_baseline_version_matches_version_file(self) -> None:
        version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
        baseline = json.loads(
            (ROOT / "policies/baseline.json").read_text(encoding="utf-8")
        )
        ai_operations = json.loads(
            (ROOT / "policies/ai-operations.json").read_text(encoding="utf-8")
        )

        self.assertEqual(version, baseline["standard_version"])
        self.assertEqual(version, ai_operations["standard_version"])

    def test_profiles_have_resolvable_inheritance(self) -> None:
        for path in (ROOT / "profiles").glob("*.json"):
            profile = json.loads(path.read_text(encoding="utf-8"))
            self.assertTrue((ROOT / profile["inherits"]).is_file(), path.name)

    def test_ai_operations_commands_are_exact(self) -> None:
        policy = json.loads(
            (ROOT / "policies/ai-operations.json").read_text(encoding="utf-8")
        )
        self.assertEqual(
            standards_check.AI_COMMANDS,
            set(policy["commands"]),
        )

    def test_ai_operations_commands_cannot_silently_escalate(self) -> None:
        policy = json.loads(
            (ROOT / "policies/ai-operations.json").read_text(encoding="utf-8")
        )
        for name, config in policy["commands"].items():
            self.assertIsNot(config.get("may_escalate"), True, name)

    def test_ai_operations_autonomy_levels_are_complete(self) -> None:
        policy = json.loads(
            (ROOT / "policies/ai-operations.json").read_text(encoding="utf-8")
        )
        self.assertEqual(
            standards_check.AI_AUTONOMY_LEVELS,
            set(policy["autonomy_levels"]),
        )

    def test_approval_is_bound_to_plan_and_revision(self) -> None:
        policy = json.loads(
            (ROOT / "policies/ai-operations.json").read_text(encoding="utf-8")
        )
        approval = policy["approval"]

        self.assertTrue(approval["plan_id_required"])
        self.assertTrue(approval["revision_required"])
        self.assertTrue(approval["approved_scope_required"])
        self.assertTrue(approval["material_revision_invalidates_approval"])

    def test_memory_promotion_is_single_writer_and_staged(self) -> None:
        policy = json.loads(
            (ROOT / "policies/ai-operations.json").read_text(encoding="utf-8")
        )
        memory = policy["memory"]

        self.assertTrue(memory["single_writer_required"])
        self.assertEqual(
            standards_check.AI_MEMORY_LIFECYCLE,
            memory["lifecycle"],
        )
        self.assertTrue(memory["two_strikes_for_permanent_rules"])


if __name__ == "__main__":
    unittest.main()
