"""Offline verifier for Zeref execution receipt v1."""

from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Mapping, Sequence

COMPLETION_STATUSES = {"PASS", "PARTIAL", "BLOCKED", "NOT_VERIFIED"}


def _canonical_bytes(value: Any) -> bytes:
    return (
        json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        )
        + "\n"
    ).encode("utf-8")


def zeref_profile_hash(profile: Mapping[str, Any]) -> str:
    """Return the canonical profile digest used by receipt v1."""

    return hashlib.sha256(_canonical_bytes(profile)).hexdigest()


def receipt_integrity_hash(receipt: Mapping[str, Any]) -> str:
    """Hash a receipt excluding its non-recursive integrity envelope."""

    value = json.loads(json.dumps(receipt))
    value.pop("integrity", None)
    return hashlib.sha256(_canonical_bytes(value)).hexdigest()


@dataclass(frozen=True)
class ZerefReceiptVerification:
    verification_status: str
    zeref_execution_status: str
    receipt_completion_status: str
    reason_codes: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "verification_status": self.verification_status,
            "zeref_execution_status": self.zeref_execution_status,
            "receipt_completion_status": self.receipt_completion_status,
            "reason_codes": list(self.reason_codes),
            "transport_status": "OFFLINE_ONLY",
            "assurance_ceiling": {
                "CONTROL_VERIFICATION_STATUS": "NOT_VERIFIED",
                "PROJECT_READINESS_STATUS": "NOT_VERIFIED",
                "RELEASE_ASSURANCE_STATUS": "NOT_VERIFIED",
                "LEGAL_REVIEW_STATUS": "NOT_VERIFIED",
            },
        }


def _parse_time(value: Any) -> datetime | None:
    if not isinstance(value, str):
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _objects(value: Any) -> list[Mapping[str, Any]] | None:
    if not isinstance(value, list) or any(not isinstance(item, Mapping) for item in value):
        return None
    return list(value)


def _strings(value: Any) -> list[str] | None:
    if (
        not isinstance(value, list)
        or any(not isinstance(item, str) or not item for item in value)
        or len(set(value)) != len(value)
    ):
        return None
    return list(value)


def _path_is_allowed(path: str, scopes: Sequence[str]) -> bool:
    return any(
        path == scope
        or (
            not scope.rsplit("/", 1)[-1].count(".")
            and path.startswith(scope.rstrip("/") + "/")
        )
        for scope in scopes
    )


def _safe_repo_path(value: str) -> bool:
    if (
        value.startswith("/")
        or value.endswith("/")
        or "\\" in value
        or any(ord(character) < 32 for character in value)
    ):
        return False
    parts = value.split("/")
    return bool(parts) and all(
        part not in {"", ".", ".."} and not part.endswith(":")
        for part in parts
    )


def verify_zeref_receipt(
    receipt: Any,
    profile: Any,
    *,
    now: datetime | None = None,
) -> ZerefReceiptVerification:
    """Verify a receipt locally without inventing transport or signer identity."""

    reasons: set[str] = set()
    if not isinstance(profile, Mapping):
        return _result({"invalid_profile"}, "NOT_VERIFIED")
    if not isinstance(receipt, Mapping):
        return _result({"invalid_receipt"}, "NOT_VERIFIED")
    if profile.get("schema_id") != "grimoire.zeref.profile.v2":
        reasons.add("unsupported_profile_schema")
    if receipt.get("schema_id") != "grimoire.zeref.receipt.v1":
        reasons.add("unsupported_receipt_schema")
    if receipt.get("schema_version") != "1.0":
        reasons.add("unsupported_receipt_version")

    roles = _objects(receipt.get("roles"))
    if (
        roles is None
        or not 1 <= len(roles) <= 4
        or sum(item.get("kind") == "lead" for item in roles) != 1
        or any(
            not isinstance(item.get("name"), str)
            or item.get("kind") not in {"lead", "support", "quality_gate"}
            for item in roles
        )
    ):
        reasons.add("invalid_role_record")
    models = _objects(receipt.get("models"))
    if (
        models is None
        or not models
        or any(
            not isinstance(item.get("requested"), str)
            or not item.get("requested")
            or not isinstance(item.get("actual"), str)
            or not item.get("actual")
            for item in models
        )
    ):
        reasons.add("invalid_model_record")
    commands = _strings(receipt.get("commands"))
    if not commands:
        reasons.add("invalid_command_record")
    if _objects(receipt.get("stop_events")) is None:
        reasons.add("invalid_stop_event_record")

    expected_profile_hash = zeref_profile_hash(profile)
    if receipt.get("profile_hash") != expected_profile_hash:
        reasons.add("profile_hash_mismatch")
    if receipt.get("pack_hash") != profile.get("pack_hash"):
        reasons.add("pack_hash_mismatch")

    receipt_plan = receipt.get("plan")
    profile_plan = profile.get("plan")
    if not isinstance(receipt_plan, Mapping) or not isinstance(profile_plan, Mapping):
        reasons.add("invalid_plan_binding")
    else:
        if receipt_plan.get("id") != profile_plan.get("id"):
            reasons.add("plan_mismatch")
        if receipt_plan.get("revision") != profile_plan.get("revision"):
            reasons.add("revision_mismatch")

    receipt_project = receipt.get("project")
    profile_project = profile.get("project")
    if not isinstance(receipt_project, Mapping) or not isinstance(
        profile_project, Mapping
    ):
        reasons.add("invalid_project_binding")
    else:
        if receipt_project.get("repository") != profile_project.get("repository"):
            reasons.add("project_repository_mismatch")
        if receipt_project.get("commit_before") != profile_project.get("commit"):
            reasons.add("project_commit_mismatch")
        if not isinstance(receipt_project.get("commit_after"), str):
            reasons.add("invalid_project_commit_after")
        if not isinstance(receipt_project.get("branch"), str):
            reasons.add("invalid_project_branch")

    scope = profile.get("scope")
    files = _strings(receipt.get("files_changed"))
    approved_scope = (
        _strings(scope.get("approved")) if isinstance(scope, Mapping) else None
    )
    if (
        not files
        or not approved_scope
        or any(not _safe_repo_path(path) for path in files)
        or any(not _safe_repo_path(path) for path in approved_scope)
    ):
        reasons.add("invalid_file_scope")
    elif any(not _path_is_allowed(path, approved_scope) for path in files):
        reasons.add("file_scope_unauthorized")

    tool_contract = profile.get("tools")
    used_tools = _strings(receipt.get("tools"))
    permitted = (
        _strings(tool_contract.get("permitted"))
        if isinstance(tool_contract, Mapping)
        else None
    )
    prohibited = (
        _strings(tool_contract.get("prohibited"))
        if isinstance(tool_contract, Mapping)
        else None
    )
    if not used_tools or not permitted or not prohibited:
        reasons.add("invalid_tool_record")
    elif not set(used_tools).issubset(permitted) or set(used_tools) & set(prohibited):
        reasons.add("tool_unauthorized")

    commit_after = (
        receipt_project.get("commit_after")
        if isinstance(receipt_project, Mapping)
        else None
    )
    evidence = _objects(receipt.get("evidence"))
    required_controls = _strings(profile.get("required_controls"))
    if evidence is None or not required_controls:
        reasons.add("invalid_evidence_record")
    else:
        passing_controls: set[str] = set()
        for item in evidence:
            evidence_time = _parse_time(item.get("timestamp"))
            if (
                not isinstance(item.get("id"), str)
                or not item.get("id")
                or not isinstance(item.get("control_id"), str)
                or not item.get("control_id")
                or not isinstance(item.get("subject_commit"), str)
                or not isinstance(item.get("command"), str)
                or not item.get("command")
                or item.get("result") not in {"PASS", "FAIL", "NOT_VERIFIED"}
                or evidence_time is None
                or not isinstance(item.get("reviewer"), str)
                or not item.get("reviewer")
            ):
                reasons.add("invalid_evidence_record")
                continue
            if (
                item.get("result") == "PASS"
                and item.get("subject_commit") == commit_after
            ):
                passing_controls.add(item["control_id"])
        if not set(required_controls).issubset(passing_controls):
            reasons.add("required_control_evidence_missing")

    tests = _objects(receipt.get("tests"))
    evidence_ids = {
        item.get("id")
        for item in (evidence or [])
        if isinstance(item.get("id"), str)
    }
    if (
        tests is None
        or not tests
        or any(
            item.get("result") != "PASS"
            or not isinstance(item.get("name"), str)
            or not isinstance(item.get("evidence_id"), str)
            or item.get("evidence_id") not in evidence_ids
            for item in tests
        )
    ):
        reasons.add("required_test_evidence_missing")

    execution = profile.get("execution")
    retries = receipt.get("retries")
    retry_ceiling = (
        execution.get("retry_ceiling") if isinstance(execution, Mapping) else None
    )
    if (
        not isinstance(retries, int)
        or isinstance(retries, bool)
        or not isinstance(retry_ceiling, int)
    ):
        reasons.add("invalid_retry_record")
    elif retries > retry_ceiling:
        reasons.add("retry_ceiling_exceeded")

    cost = receipt.get("cost")
    cost_limit = (
        execution.get("cost_limit") if isinstance(execution, Mapping) else None
    )
    if (
        not isinstance(cost, Mapping)
        or not isinstance(cost_limit, Mapping)
        or not isinstance(cost_limit.get("amount"), (int, float))
        or isinstance(cost_limit.get("amount"), bool)
        or cost_limit.get("amount", -1) < 0
        or not isinstance(cost_limit.get("currency"), str)
    ):
        reasons.add("invalid_cost_record")
    elif (
        not isinstance(cost.get("amount"), (int, float))
        or isinstance(cost.get("amount"), bool)
        or cost.get("amount", -1) < 0
        or not math.isfinite(cost.get("amount", float("nan")))
        or not isinstance(cost.get("currency"), str)
    ):
        reasons.add("invalid_cost_record")
    elif (
        cost.get("currency") != cost_limit.get("currency")
        or cost.get("amount", 0) > cost_limit.get("amount", -1)
        or cost.get("ceiling_status") != "WITHIN_CEILING"
    ):
        reasons.add("cost_ceiling_exceeded")

    approvals = _objects(receipt.get("approvals"))
    external_actions = _objects(receipt.get("external_actions"))
    approval_contract = profile.get("approvals")
    required_approvals = (
        _strings(approval_contract.get("required_for"))
        if isinstance(approval_contract, Mapping)
        else None
    )
    if approvals is None or external_actions is None or required_approvals is None:
        reasons.add("invalid_approval_record")
    else:
        approved_actions = {
            item.get("action"): item.get("id")
            for item in approvals
            if isinstance(item.get("id"), str)
            and item.get("id")
            and isinstance(receipt_plan, Mapping)
            and item.get("plan_id") == receipt_plan.get("id")
            and item.get("revision") == receipt_plan.get("revision")
        }
        for action in external_actions:
            name = action.get("action")
            if action.get("status") not in {"PERFORMED", "NOT_PERFORMED"}:
                reasons.add("invalid_external_action_record")
            elif action.get("status") == "PERFORMED" and (
                name not in required_approvals
                or name not in approved_actions
            ):
                reasons.add("external_action_unauthorized")

        proposals = _objects(receipt.get("memory_proposals"))
        if proposals is None:
            reasons.add("invalid_memory_proposal")
        elif any(
            item.get("target") == "canonical_memory"
            and (
                item.get("approved") is not True
                or "canonical_memory_write" not in approved_actions
                or not isinstance(item.get("approval_id"), str)
                or item.get("approval_id")
                != approved_actions.get("canonical_memory_write")
            )
            for item in proposals
        ):
            reasons.add("memory_promotion_unauthorized")

    timestamp = _parse_time(receipt.get("timestamp"))
    expires_at = _parse_time(receipt.get("expires_at"))
    current = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    expected_receipt = profile.get("expected_receipt")
    expiry_limit = (
        expected_receipt.get("expiry_seconds")
        if isinstance(expected_receipt, Mapping)
        else None
    )
    if timestamp is None or expires_at is None or not isinstance(expiry_limit, int):
        reasons.add("invalid_receipt_time")
    else:
        if timestamp > current:
            reasons.add("future_receipt")
        if expires_at <= current:
            reasons.add("receipt_expired")
        if expires_at <= timestamp or (expires_at - timestamp).total_seconds() > expiry_limit:
            reasons.add("receipt_expiry_exceeds_profile")

    integrity = receipt.get("integrity")
    if (
        not isinstance(integrity, Mapping)
        or integrity.get("algorithm") != "sha256-canonical-json-v1"
        or integrity.get("digest") != receipt_integrity_hash(receipt)
    ):
        reasons.add("receipt_integrity_mismatch")

    runtime = receipt.get("runtime")
    if (
        not isinstance(runtime, Mapping)
        or not isinstance(runtime.get("harness"), str)
        or not runtime.get("harness")
        or not isinstance(runtime.get("zeref_layer"), str)
        or not runtime.get("zeref_layer")
    ):
        reasons.add("invalid_runtime_record")
    elif runtime.get("capability") not in {
        "LOCAL_HARNESS_EXECUTION",
        "PARTIAL_LOCAL_RUNTIME",
        "INERT_LOCAL_FIXTURE",
        "BROWSER_SIMULATION",
        "NOT_OBSERVABLE",
    }:
        reasons.add("invalid_runtime_record")
    elif runtime.get("capability") != "LOCAL_HARNESS_EXECUTION":
        reasons.add("runtime_capability_not_verified")

    completion = receipt.get("completion_status")
    if completion not in COMPLETION_STATUSES:
        reasons.add("unsupported_completion_status")
        completion = "NOT_VERIFIED"
    return _result(reasons, completion)


def _result(
    reasons: set[str],
    completion: str,
) -> ZerefReceiptVerification:
    failures = tuple(sorted(reasons))
    if failures:
        return ZerefReceiptVerification(
            "FAIL",
            "BLOCKED",
            completion,
            failures,
        )
    return ZerefReceiptVerification(
        "PASS",
        "NOT_VERIFIED",
        completion,
        ("execution_trust_anchor_missing",),
    )
