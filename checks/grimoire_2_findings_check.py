#!/usr/bin/env python3
"""Dependency-free validation for the Grimoire 2.0 baseline finding register."""

from __future__ import annotations

import json
import re
import sys
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
FINDINGS_PATH = ROOT / "docs" / "audits" / "2026-08-15" / "FINDINGS.json"
SCHEMA_PATH = ROOT / "policies" / "schemas" / "audit-finding.schema.json"
EXPECTED_BASELINE_COMMIT = "dcc1017757d53615b29921967e6a9afd08fee38a"
EXPECTED_AUDIT_DATE = "2026-08-15"
EXPECTED_VISIBILITY = "public"

ROOT_FIELDS = {
    "schema_version",
    "audit_date",
    "baseline_commit",
    "observed_repository_visibility",
    "findings",
}
REQUIRED_FINDING_FIELDS = {
    "id",
    "severity",
    "affected_gate",
    "status",
    "title",
    "evidence",
    "owner",
    "remediation_phase",
    "close_condition",
}
OPTIONAL_FINDING_FIELDS = {"dependencies", "notes"}
EVIDENCE_FIELDS = {"type", "reference", "observation"}
SEVERITIES = {"P0", "P1", "P2", "P3"}
STATUSES = {"OPEN", "CLOSED", "ACCEPTED_RISK", "NOT_APPLICABLE"}
EVIDENCE_TYPES = {
    "repository",
    "test",
    "external_verification",
    "issue",
    "workflow",
}
FINDING_ID = re.compile(r"^GRM2-P10-[0-9]{3}$")
GATE_ID = re.compile(r"^[a-z0-9_]+$")
COMMIT_SHA = re.compile(r"^[0-9a-f]{40}$")


def _load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path.relative_to(ROOT)} must contain a JSON object")
    return value


def _nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def validate_findings() -> list[str]:
    failures: list[str] = []

    if not SCHEMA_PATH.is_file():
        failures.append("audit finding schema is missing")
        return failures
    if not FINDINGS_PATH.is_file():
        failures.append("Grimoire 2.0 finding register is missing")
        return failures

    try:
        schema = _load_json(SCHEMA_PATH)
        document = _load_json(FINDINGS_PATH)
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
        failures.append(f"finding register setup failed: {exc}")
        return failures

    if schema.get("$schema") != "https://json-schema.org/draft/2020-12/schema":
        failures.append("audit finding schema must declare Draft 2020-12")
    if schema.get("additionalProperties") is not False:
        failures.append("audit finding root schema must be closed")
    finding_schema = schema.get("$defs", {}).get("finding")
    if not isinstance(finding_schema, dict) or finding_schema.get("additionalProperties") is not False:
        failures.append("audit finding item schema must be closed")
    evidence_schema = schema.get("$defs", {}).get("evidence")
    if not isinstance(evidence_schema, dict) or evidence_schema.get("additionalProperties") is not False:
        failures.append("audit evidence item schema must be closed")

    if set(document) != ROOT_FIELDS:
        failures.append("finding register root fields do not match the canonical set")
    if document.get("schema_version") != 1:
        failures.append("finding register schema_version must be 1")
    if document.get("audit_date") != EXPECTED_AUDIT_DATE:
        failures.append("finding register audit_date does not match the Phase 10 baseline")
    else:
        try:
            date.fromisoformat(str(document["audit_date"]))
        except ValueError:
            failures.append("finding register audit_date is not ISO-8601 date format")
    baseline_commit = document.get("baseline_commit")
    if baseline_commit != EXPECTED_BASELINE_COMMIT or not isinstance(baseline_commit, str) or not COMMIT_SHA.fullmatch(baseline_commit):
        failures.append("finding register baseline_commit does not match the locked baseline")
    if document.get("observed_repository_visibility") != EXPECTED_VISIBILITY:
        failures.append("finding register repository visibility must match observed public state")

    findings = document.get("findings")
    if not isinstance(findings, list) or not findings:
        failures.append("finding register must contain at least one finding")
        return failures

    seen: set[str] = set()
    for index, finding in enumerate(findings):
        prefix = f"finding[{index}]"
        if not isinstance(finding, dict):
            failures.append(f"{prefix} must be an object")
            continue

        fields = set(finding)
        missing = REQUIRED_FINDING_FIELDS - fields
        extra = fields - REQUIRED_FINDING_FIELDS - OPTIONAL_FINDING_FIELDS
        if missing:
            failures.append(f"{prefix} missing required fields: {','.join(sorted(missing))}")
        if extra:
            failures.append(f"{prefix} has unknown fields: {','.join(sorted(extra))}")

        finding_id = finding.get("id")
        if not isinstance(finding_id, str) or not FINDING_ID.fullmatch(finding_id):
            failures.append(f"{prefix} has invalid id")
        elif finding_id in seen:
            failures.append(f"{prefix} duplicates finding id {finding_id}")
        else:
            seen.add(finding_id)

        if finding.get("severity") not in SEVERITIES:
            failures.append(f"{prefix} has invalid severity")
        if finding.get("status") not in STATUSES:
            failures.append(f"{prefix} has invalid status")

        gate = finding.get("affected_gate")
        if not isinstance(gate, str) or not GATE_ID.fullmatch(gate):
            failures.append(f"{prefix} has invalid affected_gate")

        for key in ("title", "owner", "close_condition"):
            if not _nonempty_string(finding.get(key)):
                failures.append(f"{prefix}.{key} must be a non-empty string")

        phase = finding.get("remediation_phase")
        if not isinstance(phase, int) or isinstance(phase, bool) or not 10 <= phase <= 18:
            failures.append(f"{prefix}.remediation_phase must be an integer from 10 through 18")

        dependencies = finding.get("dependencies")
        if dependencies is not None:
            if not isinstance(dependencies, list) or any(not _nonempty_string(item) for item in dependencies):
                failures.append(f"{prefix}.dependencies must be a list of non-empty strings")
            elif len(dependencies) != len(set(dependencies)):
                failures.append(f"{prefix}.dependencies must be unique")

        notes = finding.get("notes")
        if notes is not None and not isinstance(notes, str):
            failures.append(f"{prefix}.notes must be a string")

        evidence = finding.get("evidence")
        if not isinstance(evidence, list) or not evidence:
            failures.append(f"{prefix}.evidence must contain at least one item")
            continue
        for evidence_index, item in enumerate(evidence):
            evidence_prefix = f"{prefix}.evidence[{evidence_index}]"
            if not isinstance(item, dict):
                failures.append(f"{evidence_prefix} must be an object")
                continue
            if set(item) != EVIDENCE_FIELDS:
                failures.append(f"{evidence_prefix} fields do not match the canonical set")
            if item.get("type") not in EVIDENCE_TYPES:
                failures.append(f"{evidence_prefix}.type is invalid")
            if not _nonempty_string(item.get("reference")):
                failures.append(f"{evidence_prefix}.reference must be non-empty")
            if not _nonempty_string(item.get("observation")):
                failures.append(f"{evidence_prefix}.observation must be non-empty")

    return failures


def main() -> int:
    failures = validate_findings()
    if failures:
        for failure in failures:
            print(f"FAIL  {failure}")
        return 1
    print("PASS  Grimoire 2.0 audit finding register")
    return 0


if __name__ == "__main__":
    sys.exit(main())
