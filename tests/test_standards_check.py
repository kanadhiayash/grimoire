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

    def test_repository_and_component_versions_are_compatible(self) -> None:
        version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
        baseline = json.loads(
            (ROOT / "policies/baseline.json").read_text(encoding="utf-8")
        )
        components = {
            "ai_operations": json.loads(
                (ROOT / "policies/ai-operations.json").read_text(encoding="utf-8")
            ),
            "surface_activation": json.loads(
                (ROOT / "policies/surface-activation.json").read_text(encoding="utf-8")
            ),
        }

        self.assertEqual(version, baseline["standard_version"])
        root_version = standards_check.version_tuple(version)

        for name, policy in components.items():
            actual = policy["standard_version"]
            declared = baseline[name]["policy_version"]
            self.assertEqual(declared, actual, name)
            self.assertLessEqual(
                standards_check.version_tuple(actual),
                root_version,
                name,
            )

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

    def test_openai_secret_pattern_requires_a_token_boundary(self) -> None:
        patterns = standards_check.secret_patterns()
        token = "s" + "k-" + ("A" * 24)
        for candidate in (
            token,
            f"OPENAI_API_KEY={token}",
            f'Authorization: Bearer {token}',
        ):
            self.assertTrue(any(pattern.search(candidate) for pattern in patterns))

        for public_url in (
            "https://www.nist.gov/itl/ai-risk-management-framework",
            "https://www.nist.gov/publications/artificial-intelligence-risk-management-framework-generative-artificial-intelligence",
        ):
            self.assertFalse(
                any(pattern.search(public_url) for pattern in patterns),
                public_url,
            )


if __name__ == "__main__":
    unittest.main()
