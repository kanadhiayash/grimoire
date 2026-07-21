from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class AIOperationsReconciliationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.policy = json.loads(
            (ROOT / "policies/ai-operations.json").read_text(encoding="utf-8")
        )

    def test_scope_boundaries_are_explicit(self) -> None:
        boundaries = self.policy["scope_boundaries"]
        self.assertEqual(
            {"global", "project", "repository", "global_rule_threshold"},
            set(boundaries),
        )

    def test_source_precedence_is_complete_and_ordered(self) -> None:
        precedence = self.policy["source_precedence"]
        self.assertEqual(list(range(1, 11)), [item["rank"] for item in precedence])
        self.assertEqual(10, len({item["id"] for item in precedence}))

    def test_same_level_conflicts_halt_for_arbitration(self) -> None:
        conflict = self.policy["conflict_policy"]
        self.assertEqual("halt_and_arbitrate", conflict["same_level"])
        self.assertEqual("forbidden", conflict["silent_resolution"])

    def test_aliases_map_to_existing_commands(self) -> None:
        aliases = self.policy["command_aliases"]
        commands = set(self.policy["commands"])
        self.assertTrue(set(aliases.values()).issubset(commands))
        self.assertEqual("approve", aliases["FAIRYTALE"])
        self.assertEqual("handoff", aliases["ETHERIOUS"])

    def test_every_command_has_output_and_stop_contract(self) -> None:
        self.assertEqual(
            set(self.policy["commands"]),
            set(self.policy["command_contracts"]),
        )
        for command, contract in self.policy["command_contracts"].items():
            self.assertIn("required_outputs", contract, command)
            self.assertIn("stop_conditions", contract, command)

    def test_approval_invalidation_and_separate_actions_are_explicit(self) -> None:
        approval = self.policy["approval"]
        self.assertIn("scope_expansion", approval["invalidated_by"])
        self.assertIn("hard_gate_failure", approval["invalidated_by"])
        self.assertIn("rename", approval["never_implicit"])

    def test_ambitious_language_cannot_raise_autonomy(self) -> None:
        terms = self.policy["external_action_gate"]["never_inferred_from"]
        self.assertEqual(
            {"full_access", "autopilot", "do_everything", "ambitious_language"},
            set(terms),
        )

    def test_memory_promotion_has_review_and_approval_fields(self) -> None:
        fields = self.policy["memory"]["promotion_fields"]
        self.assertIn("review_date", fields)
        self.assertIn("approved_by", fields)

    def test_completion_status_keeps_machine_key_and_human_label(self) -> None:
        self.assertIn("NOT_VERIFIED", self.policy["completion_statuses"])
        self.assertEqual(
            "NOT VERIFIED",
            self.policy["completion_display_labels"]["NOT_VERIFIED"],
        )

    def test_currentness_and_behavior_cases_are_explicit(self) -> None:
        always_verify = set(self.policy["currentness"]["always_verify"])
        self.assertTrue(
            {"model_version", "repository_state", "ci", "security_advisory"}.issubset(
                always_verify
            )
        )
        self.assertGreaterEqual(len(self.policy["validation_cases"]), 6)


if __name__ == "__main__":
    unittest.main()
