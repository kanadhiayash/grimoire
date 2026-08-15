from __future__ import annotations

import importlib.util
import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CANONICAL = ROOT / "policies" / "canonical-vocabularies.json"
SCHEMA = ROOT / "policies" / "schemas" / "canonical-vocabularies.schema.json"
CHECK = ROOT / "checks" / "canonical_vocabularies_check.py"
PRIORITY_STANDARD = ROOT / "standards" / "universal" / "priority-severity-risk.md"
SOURCE_STANDARD = ROOT / "standards" / "universal" / "source-discipline.md"
AGENTS = ROOT / "AGENTS.md"
AI_POLICY = ROOT / "policies" / "ai-operations.json"
ORCHESTRATOR_POLICY = ROOT / "policies" / "standards-orchestrator.json"

EXPECTED_EVIDENCE = {
    "VERIFIED",
    "SUPPORTED",
    "ASSUMPTION",
    "UNKNOWN",
    "CONFLICTED",
}
EXPECTED_PRECEDENCE_IDS = [
    "platform_system",
    "current_user_instruction",
    "approved_task_plan",
    "repository_contract",
    "project_instructions",
    "global_instructions",
    "canonical_memory",
    "historical_handoff",
    "external_reference",
    "general_knowledge",
]


def load_json(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise AssertionError(f"{path.relative_to(ROOT)} must contain a JSON object")
    return value


def priority_evidence_labels() -> set[str]:
    text = PRIORITY_STANDARD.read_text(encoding="utf-8")
    section = text.split("## Evidence confidence", 1)[1].split("## Gate effect", 1)[0]
    return set(re.findall(r"`([A-Z_]+)`", section))


def source_evidence_labels() -> set[str]:
    text = SOURCE_STANDARD.read_text(encoding="utf-8")
    section = text.split("## Evidence grades", 1)[1]
    return set(re.findall(r"^- \*\*([^:*]+):\*\*", section, flags=re.MULTILINE))


class CanonicalVocabularyTests(unittest.TestCase):
    def test_current_evidence_vocabulary_divergence_is_reproducible(self):
        priority = priority_evidence_labels()
        source = source_evidence_labels()

        self.assertEqual(priority, EXPECTED_EVIDENCE)
        self.assertEqual(source, {"Verified", "Supported", "Assumed", "Unknown", "Risk"})
        self.assertNotEqual(priority, source)

    def test_current_approval_surfaces_diverge_without_canonical_mapping(self):
        ai_policy = load_json(AI_POLICY)
        orchestrator = load_json(ORCHESTRATOR_POLICY)
        detailed = set(ai_policy["external_action_gate"]["approval_required"])
        groups = set(orchestrator["external_action_approval"])

        self.assertNotEqual(detailed, groups)
        self.assertIn("commit", detailed)
        self.assertNotIn("commit", groups)
        self.assertIn("external_send", groups)
        self.assertNotIn("external_send", detailed)

    def test_current_precedence_is_rendered_independently(self):
        ai_policy = load_json(AI_POLICY)
        ids = [item["id"] for item in ai_policy["source_precedence"]]
        agents = AGENTS.read_text(encoding="utf-8")

        self.assertEqual(ids, EXPECTED_PRECEDENCE_IDS)
        self.assertIn("## Source-of-truth order", agents)
        self.assertNotIn("policies/canonical-vocabularies.json", agents)

    def test_canonical_vocabulary_policy_and_schema_exist(self):
        self.assertTrue(CANONICAL.is_file(), "canonical vocabulary policy is missing")
        self.assertTrue(SCHEMA.is_file(), "canonical vocabulary schema is missing")

    def test_canonical_checker_passes_active_surfaces(self):
        self.assertTrue(CHECK.is_file(), "canonical vocabulary checker is missing")
        spec = importlib.util.spec_from_file_location("canonical_vocabularies_check", CHECK)
        self.assertIsNotNone(spec)
        self.assertIsNotNone(spec.loader if spec else None)
        module = importlib.util.module_from_spec(spec)
        assert spec is not None and spec.loader is not None
        spec.loader.exec_module(module)
        self.assertEqual(module.validate(), [])

    def test_canonical_policy_locks_required_vocabularies(self):
        policy = load_json(CANONICAL)
        self.assertEqual(set(policy["evidence_confidence"]), EXPECTED_EVIDENCE)
        self.assertEqual(
            [item["id"] for item in policy["source_precedence"]],
            EXPECTED_PRECEDENCE_IDS,
        )
        self.assertEqual(policy["same_level_conflict"]["status"], "CONFLICTED")
        self.assertEqual(policy["same_level_conflict"]["behavior"], "halt_and_arbitrate")
        self.assertEqual(policy["same_level_conflict"]["silent_resolution"], "forbidden")

    def test_all_detailed_approval_actions_map_to_exactly_one_group(self):
        policy = load_json(CANONICAL)
        detailed = policy["approval_action_classes"]
        mapped = [
            action
            for group_actions in policy["approval_action_groups"].values()
            for action in group_actions
        ]
        self.assertEqual(set(mapped), set(detailed))
        self.assertEqual(len(mapped), len(set(mapped)))


if __name__ == "__main__":
    unittest.main()
