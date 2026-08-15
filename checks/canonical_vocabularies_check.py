#!/usr/bin/env python3
"""Dependency-free conformance check for canonical Grimoire vocabularies."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CANONICAL = ROOT / "policies" / "canonical-vocabularies.json"
SCHEMA = ROOT / "policies" / "schemas" / "canonical-vocabularies.schema.json"
AI_POLICY = ROOT / "policies" / "ai-operations.json"
ORCHESTRATOR = ROOT / "policies" / "standards-orchestrator.json"
PRIORITY_STANDARD = ROOT / "standards" / "universal" / "priority-severity-risk.md"
SOURCE_STANDARD = ROOT / "standards" / "universal" / "source-discipline.md"
AGENTS = ROOT / "AGENTS.md"

ROOT_FIELDS = {
    "$schema",
    "schema_version",
    "policy_id",
    "evidence_confidence",
    "source_precedence",
    "same_level_conflict",
    "approval_action_classes",
    "approval_action_groups",
    "approval_action_aliases",
    "external_authority_classes",
}
EXPECTED_EVIDENCE = ["VERIFIED", "SUPPORTED", "ASSUMPTION", "UNKNOWN", "CONFLICTED"]
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


def _load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path.relative_to(ROOT)} must contain a JSON object")
    return value


def _markdown_evidence_labels(path: Path, heading: str, next_heading: str | None = None) -> list[str]:
    text = path.read_text(encoding="utf-8")
    if heading not in text:
        return []
    section = text.split(heading, 1)[1]
    if next_heading and next_heading in section:
        section = section.split(next_heading, 1)[0]
    return re.findall(r"`([A-Z_]+)`", section)


def _agents_precedence_ids() -> list[str]:
    text = AGENTS.read_text(encoding="utf-8")
    marker = "## Source-of-truth order"
    if marker not in text:
        return []
    section = text.split(marker, 1)[1]
    if "\n## " in section:
        section = section.split("\n## ", 1)[0]
    return re.findall(r"^\d+\.\s+`([a-z0-9_]+)`:", section, flags=re.MULTILINE)


def validate() -> list[str]:
    failures: list[str] = []
    for path in (CANONICAL, SCHEMA, AI_POLICY, ORCHESTRATOR, PRIORITY_STANDARD, SOURCE_STANDARD, AGENTS):
        if not path.is_file():
            failures.append(f"missing required canonical vocabulary surface: {path.relative_to(ROOT)}")
    if failures:
        return failures

    try:
        policy = _load_json(CANONICAL)
        ai_policy = _load_json(AI_POLICY)
        orchestrator = _load_json(ORCHESTRATOR)
        schema = _load_json(SCHEMA)
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
        return [f"canonical vocabulary setup failed: {exc}"]

    if set(policy) != ROOT_FIELDS:
        failures.append("canonical vocabulary root fields do not match the locked set")
    if policy.get("$schema") != "schemas/canonical-vocabularies.schema.json":
        failures.append("canonical vocabulary schema reference is invalid")
    if policy.get("schema_version") != 1 or policy.get("policy_id") != "canonical-vocabularies":
        failures.append("canonical vocabulary identity is invalid")
    if schema.get("$schema") != "https://json-schema.org/draft/2020-12/schema":
        failures.append("canonical vocabulary schema must declare Draft 2020-12")
    if schema.get("additionalProperties") is not False:
        failures.append("canonical vocabulary root schema must be closed")

    evidence = policy.get("evidence_confidence")
    if evidence != EXPECTED_EVIDENCE:
        failures.append("canonical evidence confidence does not match the locked vocabulary")

    precedence = policy.get("source_precedence")
    if not isinstance(precedence, list):
        failures.append("canonical source precedence must be a list")
    else:
        ranks = [item.get("rank") for item in precedence if isinstance(item, dict)]
        ids = [item.get("id") for item in precedence if isinstance(item, dict)]
        if ranks != list(range(1, 11)) or ids != EXPECTED_PRECEDENCE_IDS or len(precedence) != 10:
            failures.append("canonical source precedence does not match the locked ten-level order")
        if ai_policy.get("source_precedence") != precedence:
            failures.append("AI Operations source precedence diverges from the canonical policy")

    conflict = policy.get("same_level_conflict")
    if conflict != {
        "status": "CONFLICTED",
        "behavior": "halt_and_arbitrate",
        "silent_resolution": "forbidden",
    }:
        failures.append("canonical same-level conflict contract is invalid")
    ai_conflict = ai_policy.get("conflict_policy")
    if not isinstance(ai_conflict, dict) or ai_conflict.get("same_level") != "halt_and_arbitrate" or ai_conflict.get("silent_resolution") != "forbidden":
        failures.append("AI Operations conflict behavior diverges from canonical conflict handling")

    classes = policy.get("approval_action_classes")
    if classes != EXPECTED_APPROVAL_CLASSES:
        failures.append("canonical approval action classes do not match the locked detailed gate")
    ai_gate = ai_policy.get("external_action_gate")
    ai_classes = ai_gate.get("approval_required") if isinstance(ai_gate, dict) else None
    if ai_classes != classes:
        failures.append("AI Operations approval-required actions diverge from canonical classes")

    groups = policy.get("approval_action_groups")
    if not isinstance(groups, dict) or list(groups) != EXPECTED_GROUPS:
        failures.append("canonical approval action groups do not match the locked group order")
    else:
        mapped = [action for group_actions in groups.values() for action in group_actions]
        if set(mapped) != set(EXPECTED_APPROVAL_CLASSES) or len(mapped) != len(set(mapped)):
            failures.append("canonical approval action groups must cover every detailed action exactly once")
        if orchestrator.get("external_action_approval") != EXPECTED_GROUPS:
            failures.append("Standards Orchestrator approval groups diverge from canonical groups")

    aliases = policy.get("approval_action_aliases")
    if aliases != {"destructive_migration": "migration"}:
        failures.append("canonical approval aliases do not match the locked compatibility alias")
    approval = ai_policy.get("approval")
    never_implicit = approval.get("never_implicit") if isinstance(approval, dict) else None
    if not isinstance(never_implicit, list):
        failures.append("AI Operations approval.never_implicit must be a list")
    else:
        class_set = set(EXPECTED_APPROVAL_CLASSES)
        alias_map = aliases if isinstance(aliases, dict) else {}
        unresolved = [name for name in never_implicit if alias_map.get(name, name) not in class_set]
        if unresolved:
            failures.append("AI Operations never_implicit contains actions outside canonical approval classes")

    authority_classes = policy.get("external_authority_classes")
    if orchestrator.get("authority_classes") != authority_classes:
        failures.append("Standards Orchestrator authority classes diverge from canonical authority classes")

    priority_labels = _markdown_evidence_labels(
        PRIORITY_STANDARD,
        "## Evidence confidence",
        "## Gate effect",
    )
    source_labels = _markdown_evidence_labels(SOURCE_STANDARD, "## Evidence grades")
    if priority_labels != EXPECTED_EVIDENCE:
        failures.append("priority/severity standard does not render canonical evidence confidence")
    if source_labels != EXPECTED_EVIDENCE:
        failures.append("source-discipline standard does not render canonical evidence confidence")

    agents_text = AGENTS.read_text(encoding="utf-8")
    if "policies/canonical-vocabularies.json" not in agents_text:
        failures.append("AGENTS.md does not identify the canonical machine precedence policy")
    if _agents_precedence_ids() != EXPECTED_PRECEDENCE_IDS:
        failures.append("AGENTS.md source-of-truth rendering diverges from canonical precedence IDs")

    return failures


def main() -> int:
    try:
        failures = validate()
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError, TypeError, KeyError) as exc:
        print(f"FAIL  canonical vocabulary setup: {exc}")
        return 1
    if failures:
        for failure in failures:
            print(f"FAIL  {failure}")
        return 1
    print("PASS  canonical Grimoire vocabularies and active renderings")
    return 0


if __name__ == "__main__":
    sys.exit(main())
