#!/usr/bin/env python3
"""Compile one bounded Standards Orchestrator pack from a project manifest."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

LIFECYCLE_STAGES = (
    "DISCOVER", "DEFINE", "DESIGN", "VALIDATE", "DECISION_LOCKED",
    "BUILD_READY", "BUILDING", "VERIFYING", "RELEASE_READY",
    "SHIPPED", "OPERATING", "RETIRED",
)
BUILD_STAGES = {"BUILD_READY", "BUILDING", "VERIFYING", "RELEASE_READY"}
COMPLETION_STATUSES = ("PASS", "PARTIAL", "BLOCKED", "NOT_VERIFIED")
OUTPUT_FILES = (
    "AI_CONTEXT.md", "CONTROL_PACK.json", "PROJECT_STATUS.json",
    "EXPECTED_OUTCOMES.md", "REQUIRED_DOCUMENTS.md", "DOCUMENT_SCHEMAS.json",
    "REQUIRED_GATES.md", "ACCEPTANCE_MATRIX.md", "VERIFICATION_PLAN.md",
    "SOURCE_MANIFEST.json", "ZEREF_EXECUTION_PROFILE.json", "EXECUTION_RECEIPT.json",
)


def _json(value: Any) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def _write_json(path: Path, value: Any) -> None:
    path.write_text(_json(value), encoding="utf-8")


def _bullets(values: list[str] | None) -> str:
    return "\n".join(f"- {item}" for item in (values or [])) or "- None declared"


def load_manifest(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("Project manifest must contain a JSON object")
    return value


def validate_manifest(manifest: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for key in ("schema_version", "project", "risk", "standards", "zeref"):
        if key not in manifest:
            errors.append(f"missing required field: {key}")
    project = manifest.get("project")
    if not isinstance(project, dict):
        return errors + ["project must be an object"]
    if not project.get("name"):
        errors.append("project.name is required")
    if project.get("lifecycle_stage") not in LIFECYCLE_STAGES:
        errors.append("project.lifecycle_stage must be one of: " + ", ".join(LIFECYCLE_STAGES))
    if not isinstance(project.get("product_types"), list) or not project.get("product_types"):
        errors.append("project.product_types must be a non-empty array")
    if manifest.get("risk", {}).get("level") not in {"low", "moderate", "high", "critical"}:
        errors.append("risk.level must be low, moderate, high, or critical")
    if not manifest.get("standards", {}).get("version"):
        errors.append("standards.version is required")
    if manifest.get("zeref", {}).get("mode") not in {"advisory", "standard", "strict", "off"}:
        errors.append("zeref.mode must be advisory, standard, strict, or off")
    return errors


def required_documents(stage: str, manifest: dict[str, Any]) -> list[str]:
    docs = ["Project manifest", "Product brief", "Assumption log", "Decision log", "Risk register"]
    if stage in {"DESIGN", "VALIDATE", "DECISION_LOCKED"} | BUILD_STAGES:
        docs += ["User-flow specification", "Accessibility requirements", "Design decision record"]
    if stage in BUILD_STAGES:
        docs += ["Implementation plan", "Acceptance matrix", "Verification plan", "Architecture decision records where triggered"]
    if stage in {"RELEASE_READY", "SHIPPED", "OPERATING"}:
        docs += ["Release evidence", "Rollback procedure", "Operational runbook", "Legal and privacy review status"]
    if manifest.get("data", {}).get("personal_data"):
        docs += ["Data-flow map", "Retention and deletion schedule"]
    if manifest.get("ai", {}).get("user_facing"):
        docs += ["AI risk assessment", "AI evaluation plan"]
    return sorted(set(docs))


def required_gates(stage: str, manifest: dict[str, Any]) -> list[str]:
    gates = ["Context and evidence gate", "Product integrity gate"]
    if stage in BUILD_STAGES:
        gates += ["Approved-plan revision gate", "Minimum Correct Change gate", "Security and accessibility preservation gate"]
    if manifest.get("data", {}).get("personal_data"):
        gates.append("Privacy and data-governance gate")
    if manifest.get("ai", {}).get("user_facing"):
        gates.append("AI safety, disclosure, and evaluation gate")
    if manifest.get("markets"):
        gates.append("Jurisdiction applicability and counsel-escalation gate")
    return sorted(set(gates))


def expected_outcomes(stage: str) -> list[str]:
    outcomes = [
        "Project facts, assumptions, unknowns, risks, and conflicts are separated.",
        "Only applicable standards are loaded into the execution context.",
        "Required documents have explicit owners, headings, evidence, and status.",
        "No completion, compliance, release, or runtime claim lacks fresh evidence.",
    ]
    if stage in BUILD_STAGES:
        outcomes += [
            "Implementation remains bound to the approved plan revision.",
            "The smallest complete change is used without weakening safeguards.",
            "Tests and verification prove the acceptance criteria.",
        ]
    return outcomes


def compile_project(manifest: dict[str, Any], output: Path) -> dict[str, Any]:
    errors = validate_manifest(manifest)
    if errors:
        raise ValueError("; ".join(errors))
    output.mkdir(parents=True, exist_ok=True)
    project = manifest["project"]
    stage = project["lifecycle_stage"]
    unknowns = manifest.get("unknowns", [])
    docs = required_documents(stage, manifest)
    gates = required_gates(stage, manifest)
    outcomes = expected_outcomes(stage)
    status = "PARTIAL" if unknowns else "PASS"
    generated_at = datetime.now(timezone.utc).isoformat()

    control = {
        "schema_version": 1,
        "project": project,
        "standards_version": manifest["standards"]["version"],
        "lifecycle_stage": stage,
        "profiles": {key: manifest.get(key, []) for key in ("users", "markets", "platforms")},
        "stack": manifest.get("stack", {}),
        "risk": manifest.get("risk", {}),
        "data": manifest.get("data", {}),
        "ai": manifest.get("ai", {}),
        "principles": [
            "read before editing", "evidence before assertion", "minimum correct change",
            "human and AI changes receive the same review standard",
            "external and destructive actions require explicit approval",
            "legal applicability must not be guessed",
        ],
        "required_documents": docs,
        "required_gates": gates,
        "expected_outcomes": outcomes,
        "unknowns": unknowns,
    }
    status_doc = {
        "project": project["name"], "lifecycle_stage": stage, "status": status,
        "risk_level": manifest["risk"]["level"],
        "standards_version": manifest["standards"]["version"],
        "unknown_count": len(unknowns),
        "blocking_gates": [] if not unknowns else ["Resolve declared unknowns"],
        "next_safe_action": "Execute the next approved gate" if not unknowns else "Resolve or explicitly accept declared unknowns",
    }
    zeref = {
        "schema_version": 1,
        "mode": manifest["zeref"]["mode"],
        "cost_ceiling": manifest["zeref"].get("cost_ceiling", "bounded"),
        "team": {"lead_roles": 1, "support_roles_max": 3, "quality_gate": "required only when material risk exists"},
        "execution": {
            "bind_to_approved_plan_revision": True,
            "minimum_correct_change": stage in BUILD_STAGES,
            "approval_required_for": ["merge", "deploy", "publish", "external_send", "destructive_change", "credential_change", "canonical_memory_write"],
            "completion_statuses": list(COMPLETION_STATUSES),
            "stop_on": ["missing evidence", "source conflict", "scope contradiction", "security or privacy risk", "unsupported tool capability"],
        },
    }
    schemas = {
        "product_brief": ["Objective", "Problem", "Evidence", "Users", "User needs", "Business need", "Constraints", "Scope", "Non-goals", "Assumptions", "Unknowns", "Risks", "Success metrics", "Guardrail metrics", "Legal and accessibility considerations", "Decision owners", "Next gate"],
        "implementation_plan": ["Objective", "Approved plan revision", "Context used", "Applicable standards", "Scope", "Non-goals", "Dependencies", "Files expected to change", "Architecture boundaries", "Implementation sequence", "Acceptance criteria", "Test plan", "Security checks", "Accessibility checks", "Cost limits", "Rollback plan", "Evidence requirements", "Approval boundaries", "Risks", "Stop conditions"],
    }
    context = f"""# Standards Orchestrator Context

## Project

- Name: {project['name']}
- Lifecycle stage: {stage}
- Risk: {manifest['risk']['level']}
- Standards version: {manifest['standards']['version']}
- Zeref mode: {manifest['zeref']['mode']}

## Product types

{_bullets(project.get('product_types'))}

## Users

{_bullets(manifest.get('users'))}

## Markets

{_bullets(manifest.get('markets'))}

## Expected outcomes

{_bullets(outcomes)}

## Required documents

{_bullets(docs)}

## Required gates

{_bullets(gates)}

## Unknowns

{_bullets(unknowns)}

## Execution contract

Read before editing. Remain bound to the approved plan and revision. During coding, apply Minimum Correct Change. Reuse before creating, change the correct ownership layer, avoid unnecessary dependencies and files, preserve security, privacy, accessibility, data integrity, and tests, then stop when acceptance criteria pass. Zeref routes execution. The Standards Orchestrator defines required outcomes, documents, gates, evidence, and limits.
"""
    (output / "AI_CONTEXT.md").write_text(context, encoding="utf-8")
    _write_json(output / "CONTROL_PACK.json", control)
    _write_json(output / "PROJECT_STATUS.json", status_doc)
    (output / "EXPECTED_OUTCOMES.md").write_text("# Expected Outcomes\n\n" + _bullets(outcomes) + "\n", encoding="utf-8")
    (output / "REQUIRED_DOCUMENTS.md").write_text("# Required Documents\n\n" + _bullets(docs) + "\n", encoding="utf-8")
    _write_json(output / "DOCUMENT_SCHEMAS.json", schemas)
    (output / "REQUIRED_GATES.md").write_text("# Required Gates\n\n" + _bullets(gates) + "\n", encoding="utf-8")
    (output / "ACCEPTANCE_MATRIX.md").write_text("# Acceptance Matrix\n\n| Outcome | Evidence | Status |\n|---|---|---|\n" + "\n".join(f"| {item} | Required | NOT_VERIFIED |" for item in outcomes) + "\n", encoding="utf-8")
    (output / "VERIFICATION_PLAN.md").write_text("# Verification Plan\n\n- Validate the manifest.\n- Verify every required document.\n- Run project tests and applicable quality gates.\n- Record exact commands and results.\n- Report PASS, PARTIAL, BLOCKED, or NOT_VERIFIED.\n", encoding="utf-8")
    _write_json(output / "SOURCE_MANIFEST.json", {"generated_at": generated_at, "standards_version": manifest["standards"]["version"], "source_status": "PROJECT_DECLARED", "legal_compliance_claim": "FORBIDDEN_WITHOUT_QUALIFIED_REVIEW"})
    _write_json(output / "ZEREF_EXECUTION_PROFILE.json", zeref)

    hashes = {name: hashlib.sha256((output / name).read_bytes()).hexdigest() for name in OUTPUT_FILES[:-1]}
    receipt = {"status": status, "generated_at": generated_at, "project": project["name"], "output_files": list(OUTPUT_FILES), "sha256": hashes}
    _write_json(output / "EXECUTION_RECEIPT.json", receipt)
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    receipt = compile_project(load_manifest(Path(args.manifest)), Path(args.output))
    print(_json(receipt), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
