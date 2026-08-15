"""Dependency-free Grimoire 2.0 release eligibility rubric."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Mapping


DIMENSION_ID = re.compile(r"^[a-z0-9_]+$")
FINDING_ID = re.compile(r"^GRM2-P10-[0-9]{3}$")
COMPLETION_STATUSES = ["PASS", "PARTIAL", "BLOCKED", "NOT_VERIFIED"]
ROOT_FIELDS = {
    "schema_version",
    "policy_id",
    "target_release",
    "completion_statuses",
    "eligibility",
    "dimensions",
}
ELIGIBILITY_FIELDS = {
    "required_status",
    "missing_required_status",
    "required_non_pass_blocks",
    "owner_approval_separate",
    "owner_approval_scope",
    "release_action_permitted",
}
DIMENSION_FIELDS = {
    "id",
    "required",
    "implementation_phase",
    "finding_ids",
    "evidence_requirement",
    "owner",
}


class ReleaseGatePolicyError(ValueError):
    """Raised when the Grimoire 2.0 release rubric is invalid."""


def _nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def validate_release_gate_policy(policy: Mapping[str, Any]) -> None:
    if not isinstance(policy, Mapping):
        raise ReleaseGatePolicyError("policy_type_invalid")
    if set(policy) != ROOT_FIELDS:
        raise ReleaseGatePolicyError("policy_fields_invalid")
    if policy.get("schema_version") != 1:
        raise ReleaseGatePolicyError("schema_version_invalid")
    if policy.get("policy_id") != "grimoire-2-release-gates":
        raise ReleaseGatePolicyError("policy_id_invalid")
    if policy.get("target_release") != "2.0.0":
        raise ReleaseGatePolicyError("target_release_invalid")
    if policy.get("completion_statuses") != COMPLETION_STATUSES:
        raise ReleaseGatePolicyError("completion_statuses_invalid")

    eligibility = policy.get("eligibility")
    if not isinstance(eligibility, Mapping) or set(eligibility) != ELIGIBILITY_FIELDS:
        raise ReleaseGatePolicyError("eligibility_contract_invalid")
    expected_eligibility = {
        "required_status": "PASS",
        "missing_required_status": "NOT_VERIFIED",
        "required_non_pass_blocks": True,
        "owner_approval_separate": True,
        "owner_approval_scope": "exact-commit-release",
        "release_action_permitted": False,
    }
    if dict(eligibility) != expected_eligibility:
        raise ReleaseGatePolicyError("eligibility_contract_invalid")

    dimensions = policy.get("dimensions")
    if not isinstance(dimensions, list) or not dimensions:
        raise ReleaseGatePolicyError("dimensions_invalid")

    seen_dimensions: set[str] = set()
    seen_findings: set[str] = set()
    for dimension in dimensions:
        if not isinstance(dimension, Mapping) or set(dimension) != DIMENSION_FIELDS:
            raise ReleaseGatePolicyError("dimension_contract_invalid")
        dimension_id = dimension.get("id")
        if (
            not isinstance(dimension_id, str)
            or not DIMENSION_ID.fullmatch(dimension_id)
            or dimension_id in seen_dimensions
        ):
            raise ReleaseGatePolicyError("dimension_id_invalid")
        seen_dimensions.add(dimension_id)

        if not isinstance(dimension.get("required"), bool):
            raise ReleaseGatePolicyError("dimension_required_invalid")
        phase = dimension.get("implementation_phase")
        if not isinstance(phase, int) or isinstance(phase, bool) or not 10 <= phase <= 18:
            raise ReleaseGatePolicyError("dimension_phase_invalid")
        if not _nonempty_string(dimension.get("evidence_requirement")):
            raise ReleaseGatePolicyError("dimension_evidence_invalid")
        if not _nonempty_string(dimension.get("owner")):
            raise ReleaseGatePolicyError("dimension_owner_invalid")

        finding_ids = dimension.get("finding_ids")
        if not isinstance(finding_ids, list):
            raise ReleaseGatePolicyError("dimension_findings_invalid")
        local_findings: set[str] = set()
        for finding_id in finding_ids:
            if (
                not isinstance(finding_id, str)
                or not FINDING_ID.fullmatch(finding_id)
                or finding_id in local_findings
                or finding_id in seen_findings
            ):
                raise ReleaseGatePolicyError("dimension_findings_invalid")
            local_findings.add(finding_id)
            seen_findings.add(finding_id)


def load_release_gate_policy(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ReleaseGatePolicyError("policy_load_failed") from exc
    if not isinstance(value, dict):
        raise ReleaseGatePolicyError("policy_type_invalid")
    validate_release_gate_policy(value)
    return value


def evaluate_release_gate_results(
    policy: Mapping[str, Any],
    results: Mapping[str, str],
) -> dict[str, Any]:
    validate_release_gate_policy(policy)
    if not isinstance(results, Mapping):
        raise ReleaseGatePolicyError("results_type_invalid")

    dimensions = policy["dimensions"]
    known_ids = {dimension["id"] for dimension in dimensions}
    unknown_ids = set(results) - known_ids
    if unknown_ids:
        raise ReleaseGatePolicyError("unknown_dimension_result")

    allowed_statuses = set(COMPLETION_STATUSES)
    for dimension_id, status in results.items():
        if not isinstance(dimension_id, str) or status not in allowed_statuses:
            raise ReleaseGatePolicyError("dimension_result_invalid")

    missing_status = policy["eligibility"]["missing_required_status"]
    required_status = policy["eligibility"]["required_status"]
    blocking: list[str] = []
    dimension_results: list[dict[str, Any]] = []

    for dimension in dimensions:
        dimension_id = dimension["id"]
        status = results.get(dimension_id, missing_status)
        required = dimension["required"]
        if required and status != required_status:
            blocking.append(dimension_id)
        dimension_results.append(
            {
                "id": dimension_id,
                "required": required,
                "status": status,
            }
        )

    eligible = not blocking
    return {
        "schema_version": 1,
        "decision_contract": "GRIMOIRE_2_RELEASE_ELIGIBILITY_V1",
        "eligibility_status": "PASS" if eligible else "BLOCKED",
        "eligible_for_owner_approval": eligible,
        "owner_approval_required": True,
        "owner_approval_scope": policy["eligibility"]["owner_approval_scope"],
        "release_authorized": False,
        "blocking_dimensions": blocking,
        "dimension_results": dimension_results,
    }
