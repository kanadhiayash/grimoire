#!/usr/bin/env python3
"""Cross-surface activation policy checks."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATUSES = {
    "RUNTIME_FULL",
    "RUNTIME_PARTIAL",
    "PROJECT_SIMULATION",
    "CHAT_SIMULATION",
    "INSTRUCTION_ONLY",
    "UNAVAILABLE",
    "NOT_VERIFIED",
}


@dataclass(frozen=True)
class SurfaceEvidence:
    surface: str
    inspection_available: bool = True
    runtime_capability: bool = False
    project_contract: bool = False
    source_pack_complete: bool = False
    some_instructions: bool = False


def classify(evidence: SurfaceEvidence) -> str:
    if not evidence.inspection_available:
        return "NOT_VERIFIED"
    if evidence.surface == "local_harness":
        if evidence.runtime_capability and evidence.project_contract:
            return "RUNTIME_FULL"
        if evidence.runtime_capability or evidence.project_contract:
            return "RUNTIME_PARTIAL"
        if evidence.some_instructions:
            return "INSTRUCTION_ONLY"
        return "UNAVAILABLE"
    if evidence.surface == "browser_project":
        return (
            "PROJECT_SIMULATION"
            if evidence.source_pack_complete
            else ("INSTRUCTION_ONLY" if evidence.some_instructions else "UNAVAILABLE")
        )
    if evidence.surface == "browser_chat":
        return (
            "CHAT_SIMULATION"
            if evidence.source_pack_complete
            else ("INSTRUCTION_ONLY" if evidence.some_instructions else "UNAVAILABLE")
        )
    return "NOT_VERIFIED"


def validate_policy() -> list[str]:
    path = ROOT / "policies" / "surface-activation.json"
    policy = json.loads(path.read_text(encoding="utf-8"))
    errors: list[str] = []
    if policy.get("policy") != "surface-activation":
        errors.append("policy id mismatch")
    if set(policy.get("activation_statuses", {})) != STATUSES:
        errors.append("activation statuses do not match canonical set")
    rules = policy.get("rules", {})
    for key in (
        "modify_zeref_repository",
        "duplicate_zeref_boot_contract",
        "duplicate_zeref_command_registry",
        "duplicate_zeref_memory_internals",
        "false_runtime_claims",
    ):
        if rules.get(key) is not False:
            errors.append(f"rules.{key} must be false")
    if policy.get("browser_memory", {}).get("canonical_promotion_forbidden") is not True:
        errors.append("browser canonical memory promotion must be forbidden")
    return errors


def main() -> int:
    errors = validate_policy()
    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        return 1
    print("Surface activation policy: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
