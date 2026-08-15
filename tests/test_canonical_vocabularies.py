from __future__ import annotations

import importlib.util
import json
import re
import unittest
from pathlib import Path

try:
    from jsonschema import Draft202012Validator
except ImportError:  # Runtime remains dependency-free; CI installs the validator.
    Draft202012Validator = None


ROOT = Path(__file__).resolve().parents[1]
CANONICAL = ROOT / "policies" / "canonical-vocabularies.json"
SCHEMA = ROOT / "policies" / "schemas" / "canonical-vocabularies.schema.json"
CHECK = ROOT / "checks" / "canonical_vocabularies_check.py"
PRIORITY_STANDARD = ROOT / "standards" / "universal" / "priority-severity-risk.md"
SOURCE_STANDARD = ROOT / "standards" / "universal" / "source-discipline.md"
AGENTS = ROOT / "AGENTS.md"
AI_POLICY = ROOT / "policies" / "ai-operations.json"
ORCHESTRATOR_POLICY = ROOT / "policies" / "standards-orchestrator.json"

EXPECTED_EVIDENCE = [
    "VERIFIED",
    "SUPPORTED",
    "ASSUMPTION",
    "UNKNOWN",
    "CONFLICTED",
]
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
EXPECTED_APPROVAL_CLASSES = [
    "commit",
    "push",
    "issue_write",
    "pull_request_write",
    "merge",
    "deploy",
    "release",
    "publish",
    "send",
    "schedule",
    "delete",
    "archive",
    "rename",
    "overwrite",
    "migration",
    "credential_change",
    "infrastructure_change",
    "canonical_memory_promotion",
    "public_metric",
]
EXPECTED_GROUPS = [
    "repository_write",
    "merge",
    "deploy",
    "publish",
    "external_send",
    "destructive_change",
    "credential_change",
    "canonical_memory_write",
]


def load_json(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise AssertionError(f"{path.relative_to(ROOT)} must contain a JSON object")
    return value


def priority_evidence_labels() -> list[str]:
    text = PRIORITY_STANDARD.read_text(encoding="utf-8")
    section = text.split("## Evidence confidence", 1)[1].split("## Gate effect", 1)[0]
    return re.findall(r"`([A-Z_]+)`", section)


def source_evidence_labels() -> list[str]:
    text = SOURCE_STANDARD.read_text(encoding="utf-8")
    section = text.split("## Evidence grades", 1)[1]
    return re.findall(r"^- `([A-Z_]+)`:", section, flags=re.MULTILINE)


def agents_precedence_ids() -> list[str]:
    text = AGENTS.read_text(encoding="utf-8")
    section = text.split("## Source-of-truth order", 1)[1].split("\n## ", 1)[0]
    return re.findall(r"^\d+\.\s+`([a-z0-9_]+)`:", section, flags=re.MULTILINE)


class CanonicalVocabularyTests(unittest.TestCase):
    def test_evidence_surfaces_render_one_canonical_vocabulary(self):
        policy = load_json(CANONICAL)
        self.assertEqual(policy["evidence_confidence"], EXPECTED_EVIDENCE)
        self.assertEqual(priority_evidence_labels(), EXPECTED_EVIDENCE)
        self.assertEqual(source_evidence_labels(), EXPECTED_EVIDENCE)

    def test_detailed_approval_gate_is_preserved_and_grouped_exactly_once(self):
        policy = load_json(CANONICAL)
        ai_policy = load_json(AI_POLICY)
        orchestrator = load_json(ORCHESTRATOR_POLICY)

        detailed = ai_policy["external_action_gate"]["approval_required"]
        self.assertEqual(detailed, EXPECTED_APPROVAL_CLASSES)
        self.assertEqual(policy["approval_action_classes"], EXPECTED_APPROVAL_CLASSES)
        self.assertEqual(list(policy["approval_action_groups"]), EXPECTED_GROUPS)
        self.assertEqual(orchestrator["external_action_approval"], EXPECTED_GROUPS)

        mapped = [
            action
            for group_actions in policy["approval_action_groups"].values()
            for action in group_actions
        ]
        self.assertEqual(set(mapped), set(EXPECTED_APPROVAL_CLASSES))
        self.assertEqual(len(mapped), len(set(mapped)))
        self.assertEqual(len(mapped), 19)

    def test_never_implicit_actions_resolve_to_canonical_gate_classes(self):
        policy = load_json(CANONICAL)
        ai_policy = load_json(AI_POLICY)
        classes = set(policy["approval_action_classes"])
        aliases = policy["approval_action_aliases"]

        unresolved = [
            name
            for name in ai_policy["approval"]["never_implicit"]
            if aliases.get(name, name) not in classes
        ]
        self.assertEqual(unresolved, [])
        self.assertEqual(aliases["destructive_migration"], "migration")

    def test_source_precedence_has_one_machine_owner_and_agents_rendering(self):
        policy = load_json(CANONICAL)
        ai_policy = load_json(AI_POLICY)
        agents = AGENTS.read_text(encoding="utf-8")

        self.assertEqual(ai_policy["source_precedence"], policy["source_precedence"])
        self.assertEqual(
            [item["id"] for item in policy["source_precedence"]],
            EXPECTED_PRECEDENCE_IDS,
        )
        self.assertIn("policies/canonical-vocabularies.json", agents)
        self.assertEqual(agents_precedence_ids(), EXPECTED_PRECEDENCE_IDS)

    def test_same_level_conflict_remains_fail_closed(self):
        policy = load_json(CANONICAL)
        ai_policy = load_json(AI_POLICY)
        self.assertEqual(policy["same_level_conflict"]["status"], "CONFLICTED")
        self.assertEqual(policy["same_level_conflict"]["behavior"], "halt_and_arbitrate")
        self.assertEqual(policy["same_level_conflict"]["silent_resolution"], "forbidden")
        self.assertEqual(ai_policy["conflict_policy"]["same_level"], "halt_and_arbitrate")
        self.assertEqual(ai_policy["conflict_policy"]["silent_resolution"], "forbidden")

    def test_external_authority_classes_render_canonical_policy(self):
        policy = load_json(CANONICAL)
        orchestrator = load_json(ORCHESTRATOR_POLICY)
        self.assertEqual(orchestrator["authority_classes"], policy["external_authority_classes"])

    def test_canonical_vocabulary_policy_schema_and_checker_exist(self):
        self.assertTrue(CANONICAL.is_file())
        self.assertTrue(SCHEMA.is_file())
        self.assertTrue(CHECK.is_file())

    def test_canonical_checker_passes_active_surfaces(self):
        spec = importlib.util.spec_from_file_location("canonical_vocabularies_check", CHECK)
        self.assertIsNotNone(spec)
        self.assertIsNotNone(spec.loader if spec else None)
        module = importlib.util.module_from_spec(spec)
        assert spec is not None and spec.loader is not None
        spec.loader.exec_module(module)
        self.assertEqual(module.validate(), [])

    @unittest.skipIf(Draft202012Validator is None, "jsonschema is installed only for schema validation")
    def test_canonical_policy_validates_under_closed_draft_2020_12_schema(self):
        schema = load_json(SCHEMA)
        policy = load_json(CANONICAL)
        Draft202012Validator.check_schema(schema)
        errors = list(Draft202012Validator(schema).iter_errors(policy))
        self.assertEqual(errors, [])
        self.assertFalse(schema.get("additionalProperties"))
        self.assertFalse(schema["properties"]["same_level_conflict"].get("additionalProperties"))
        self.assertFalse(schema["properties"]["approval_action_groups"].get("additionalProperties"))
        self.assertFalse(schema["properties"]["approval_action_aliases"].get("additionalProperties"))


if __name__ == "__main__":
    unittest.main()
