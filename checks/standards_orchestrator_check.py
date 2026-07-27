#!/usr/bin/env python3
"""Validate Standards Orchestrator files, contracts, and instruction boundaries."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED_FILES = [
    "policies/standards-orchestrator.json",
    "policies/schemas/project-manifest.schema.json",
    "policies/schemas/project-status.schema.json",
    "policies/schemas/execution-receipt.schema.json",
    "policies/schemas/standard-record.schema.json",
    "policies/schemas/document-requirement.schema.json",
    "policies/schemas/zeref-execution-profile.schema.json",
    "scripts/project_orchestrator.py",
    "src/grimoire/__init__.py",
    "src/grimoire/status.py",
    "standards/universal/standard-authoring.md",
    "standards/universal/naming-and-placement.md",
    "standards/universal/priority-severity-risk.md",
    "standards/product-ux/product-design-operations.md",
    "standards/product-ux/heuristic-and-interface-quality.md",
    "standards/product-ux/design-token-and-figma-conventions.md",
    "standards/legal-compliance/global-legal-control-plane.md",
    "standards/engineering/minimum-correct-change.md",
    "standards/engineering/system-layering.md",
    "standards/engineering/frontend-client.md",
    "standards/engineering/api-integration.md",
    "standards/engineering/backend-data.md",
    "standards/engineering/security-red-team.md",
    "standards/engineering/cloud-reliability-cost.md",
    "standards/ai-development/zeref-orchestrator-integration.md",
    "standards/ai-development/ai-agent-product-engineering.md",
    "standards/github/git-delivery-operations.md",
    "templates/standards/STANDARD.md",
    "templates/orchestrator/DOCUMENT_REQUIREMENT.md",
    "templates/project/project.json",
    "templates/records/ASSUMPTION.md",
    "templates/records/DECISION.md",
    "templates/records/RISK.md",
    "instructions/global/manifest.json",
    "instructions/personal/yash/manifest.json",
    "skills/standards-orchestrator/README.md",
    "services/standards-orchestrator/README.md",
    "sources/legal/registry.json",
    "docs/operations/standards-orchestrator-capability-map.md",
    "benchmarks/standards-orchestrator/README.md",
    "docs/architecture/0009-multidimensional-status-model.md",
    "docs/migrations/0.5.x-status-model.md",
]
PERSONAL_TERMS = ("Yash", "Kanadhia", "Mavis", "Toronto")
REQUIRED_STANDARD_HEADINGS = (
    "Purpose", "Expected outcome", "Applicability", "Required inputs",
    "Acceptance criteria", "Verification method", "Evidence required",
    "Guards and limits", "Cost considerations", "Source provenance",
    "Zeref execution behavior",
)
COMPLETION_STATUSES = {"PASS", "PARTIAL", "BLOCKED", "NOT_VERIFIED"}
STATUS_DIMENSIONS = {
    "PACK_GENERATION_STATUS",
    "MANIFEST_VALIDATION_STATUS",
    "APPLICABILITY_STATUS",
    "CONTROL_VERIFICATION_STATUS",
    "PROJECT_READINESS_STATUS",
    "RELEASE_ASSURANCE_STATUS",
    "LEGAL_REVIEW_STATUS",
    "ZEREF_EXECUTION_STATUS",
}


def main() -> int:
    failures: list[str] = []
    for name in REQUIRED_FILES:
        if not (ROOT / name).is_file():
            failures.append(f"missing required file: {name}")

    json_paths = [
        ROOT / "policies/standards-orchestrator.json",
        *sorted((ROOT / "policies/schemas").glob("*.json")),
        ROOT / "instructions/global/manifest.json",
        ROOT / "instructions/personal/yash/manifest.json",
        ROOT / "sources/legal/registry.json",
    ]
    for path in json_paths:
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
            if not isinstance(value, dict):
                failures.append(f"JSON root must be object: {path.relative_to(ROOT)}")
        except Exception as exc:
            failures.append(f"invalid JSON {path.relative_to(ROOT)}: {exc}")

    for path in sorted((ROOT / "instructions/global").glob("*.md")):
        text = path.read_text(encoding="utf-8")
        for term in PERSONAL_TERMS:
            if term in text:
                failures.append(f"personal term {term!r} found in neutral instruction {path.relative_to(ROOT)}")

    template = (ROOT / "templates/standards/STANDARD.md").read_text(encoding="utf-8")
    for heading in REQUIRED_STANDARD_HEADINGS:
        if f"## {heading}" not in template:
            failures.append(f"standard template missing heading: {heading}")

    policy = json.loads((ROOT / "policies/standards-orchestrator.json").read_text(encoding="utf-8"))
    if "COMPLIANT" in policy.get("applicability_statuses", []):
        failures.append("automated legal COMPLIANT status is forbidden")
    for name in ("project-status.schema.json", "execution-receipt.schema.json"):
        schema = json.loads(
            (ROOT / "policies" / "schemas" / name).read_text(encoding="utf-8")
        )
        definitions = schema.get("$defs", {})
        declared_statuses = set(
            definitions.get("completionStatus", {}).get("enum", [])
        )
        dimensions = (
            definitions.get("statusReport", {})
            .get("properties", {})
            .get("dimensions", {})
        )
        declared_dimensions = set(dimensions.get("required", []))
        if declared_statuses != COMPLETION_STATUSES:
            failures.append(
                f"{name} must declare the exact completion status vocabulary"
            )
        if declared_dimensions != STATUS_DIMENSIONS:
            failures.append(
                f"{name} must require the exact Phase 1 status dimensions"
            )
        if dimensions.get("additionalProperties") is not False:
            failures.append(f"{name} must reject unknown status dimensions")
    baseline = json.loads((ROOT / "policies/baseline.json").read_text(encoding="utf-8"))
    declared = baseline.get("standards_orchestrator", {}).get("policy_version")
    if declared != policy.get("module_version"):
        failures.append(f"baseline orchestrator version {declared!r} does not match policy {policy.get('module_version')!r}")

    registry = json.loads((ROOT / "sources/legal/registry.json").read_text(encoding="utf-8"))
    if registry.get("coverage_status") == "EXHAUSTIVE":
        failures.append("legal registry may not claim exhaustive coverage")
    if registry.get("legal_advice") is not False:
        failures.append("legal registry must state legal_advice=false")

    if failures:
        for failure in failures:
            print(f"FAIL  {failure}")
        return 1
    print("PASS  standards orchestrator")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
