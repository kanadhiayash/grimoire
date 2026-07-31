"""Build deterministic Zeref execution profiles without owning Zeref routing."""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType
from typing import Any, Iterable, Mapping, Sequence

REQUIRED_APPROVAL_ACTIONS = frozenset(
    {
        "merge",
        "deploy",
        "publish",
        "external_send",
        "destructive_change",
        "credential_change",
        "canonical_memory_write",
    }
)
PACK_BINDING_FILES = (
    "ACCEPTANCE_MATRIX.md",
    "AI_CONTEXT.md",
    "CONFLICT_REPORT.json",
    "CONTROL_PACK.json",
    "CONTROL_TRACE.json",
    "DOCUMENT_SCHEMAS.json",
    "EXCLUSIONS.json",
    "EXPECTED_OUTCOMES.md",
    "PROJECT_STATUS.json",
    "REQUIRED_DOCUMENTS.md",
    "REQUIRED_GATES.md",
    "SOURCE_MANIFEST.json",
    "VERIFICATION_PLAN.md",
)
_HEX = re.compile(r"^[0-9a-f]+$")


class ProfileValidationError(ValueError):
    """A fail-closed profile construction error with stable reason codes."""

    def __init__(self, reason_codes: Iterable[str]):
        self.reason_codes = tuple(sorted(set(reason_codes)))
        super().__init__(", ".join(self.reason_codes))


@dataclass(frozen=True)
class ZerefExecutionProfileV2:
    """Immutable machine contract that describes limits, not routing behavior."""

    value: Mapping[str, Any]

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "value",
            MappingProxyType(json.loads(json.dumps(self.value))),
        )

    def to_dict(self) -> dict[str, Any]:
        return json.loads(json.dumps(dict(self.value)))

    def canonical_bytes(self) -> bytes:
        return (
            json.dumps(
                self.to_dict(),
                sort_keys=True,
                separators=(",", ":"),
                ensure_ascii=False,
            )
            + "\n"
        ).encode("utf-8")


def canonical_pack_hash(directory: Path) -> str:
    """Hash the explicit pre-profile pack domain without recursive self-binding."""

    digest = hashlib.sha256()
    for name in PACK_BINDING_FILES:
        path = directory / name
        if not path.is_file():
            raise ProfileValidationError((f"missing_pack_artifact_{name.lower()}",))
        name_bytes = name.encode("utf-8")
        content = path.read_bytes()
        digest.update(len(name_bytes).to_bytes(4, "big"))
        digest.update(name_bytes)
        digest.update(len(content).to_bytes(8, "big"))
        digest.update(content)
    return digest.hexdigest()


def _string_list(value: Any) -> tuple[str, ...] | None:
    if (
        not isinstance(value, (list, tuple))
        or not value
        or any(not isinstance(item, str) or not item.strip() for item in value)
    ):
        return None
    normalized = tuple(sorted(set(item.strip() for item in value)))
    return normalized if len(normalized) == len(value) else None


def _source_trace(fields: Sequence[str]) -> list[dict[str, str]]:
    return [
        {
            "constraint": field,
            "source": (
                "docs/architecture/0020-zeref-profile-and-receipt-trust.md"
                if field.startswith(("pack_hash", "plan.", "project."))
                else "AGENTS.md#zeref-boundary"
            ),
        }
        for field in sorted(fields)
    ]


def build_profile_v2(
    binding: Mapping[str, Any],
    *,
    pack_hash: str,
    required_controls: Sequence[str],
    required_documents: Sequence[str],
    acceptance_criteria: Sequence[str],
    stop_conditions: Sequence[str],
    grimoire_version: str,
    mode: str,
    cost_ceiling: str,
) -> ZerefExecutionProfileV2:
    """Validate a plan binding and build a deterministic profile v2."""

    reasons: set[str] = set()
    required = (
        "plan_id",
        "plan_revision",
        "project_repository",
        "project_commit",
        "approved_scope",
        "excluded_scope",
        "permitted_tools",
        "prohibited_tools",
        "approval_required_for",
    )
    allowed = set(required) | {"retry_ceiling", "receipt_expiry_seconds"}
    if set(binding) - allowed:
        reasons.add("unknown_binding_property")
    for field in required:
        if field not in binding:
            reasons.add(f"missing_{field}")

    plan_id = binding.get("plan_id")
    if not isinstance(plan_id, str) or not plan_id.strip():
        reasons.add("invalid_plan_id")
    revision = binding.get("plan_revision")
    if not isinstance(revision, int) or isinstance(revision, bool) or revision < 1:
        reasons.add("invalid_plan_revision")
    repository = binding.get("project_repository")
    if not isinstance(repository, str) or not repository.strip():
        reasons.add("invalid_project_repository")
    commit = binding.get("project_commit")
    if (
        not isinstance(commit, str)
        or len(commit) not in {40, 64}
        or not _HEX.fullmatch(commit)
    ):
        reasons.add("invalid_project_commit")
    if len(pack_hash) != 64 or not _HEX.fullmatch(pack_hash):
        reasons.add("invalid_pack_hash")

    approved_scope = _string_list(binding.get("approved_scope"))
    if approved_scope is None:
        reasons.add("invalid_approved_scope")
    excluded_scope = _string_list(binding.get("excluded_scope"))
    if excluded_scope is None:
        reasons.add("invalid_excluded_scope")
    elif approved_scope is not None and set(approved_scope) & set(excluded_scope):
        reasons.add("scope_boundary_conflict")
    permitted_tools = _string_list(binding.get("permitted_tools"))
    prohibited_tools = _string_list(binding.get("prohibited_tools"))
    if permitted_tools is None or prohibited_tools is None:
        reasons.add("invalid_tool_boundary")
    elif set(permitted_tools) & set(prohibited_tools):
        reasons.add("tool_boundary_conflict")

    approvals = _string_list(binding.get("approval_required_for"))
    if approvals is None:
        reasons.add("invalid_approval_required_for")
    elif not REQUIRED_APPROVAL_ACTIONS.issubset(approvals):
        reasons.add("approval_boundary_weakened")

    retry_ceiling = binding.get("retry_ceiling", 0)
    if (
        not isinstance(retry_ceiling, int)
        or isinstance(retry_ceiling, bool)
        or not 0 <= retry_ceiling <= 10
    ):
        reasons.add("invalid_retry_ceiling")
    expiry = binding.get("receipt_expiry_seconds", 3600)
    if (
        not isinstance(expiry, int)
        or isinstance(expiry, bool)
        or not 60 <= expiry <= 86400
    ):
        reasons.add("invalid_receipt_expiry")
    if mode not in {"advisory", "standard", "strict", "off"}:
        reasons.add("invalid_execution_mode")
    if not isinstance(cost_ceiling, str) or not cost_ceiling.strip():
        reasons.add("invalid_cost_ceiling")

    controls = _string_list(required_controls)
    documents = _string_list(required_documents)
    criteria = _string_list(acceptance_criteria)
    stops = _string_list(stop_conditions)
    if controls is None:
        reasons.add("invalid_required_controls")
    if documents is None:
        reasons.add("invalid_required_documents")
    if criteria is None:
        reasons.add("invalid_acceptance_criteria")
    if stops is None:
        reasons.add("invalid_stop_conditions")
    if not isinstance(grimoire_version, str) or not grimoire_version.strip():
        reasons.add("invalid_grimoire_version")
    if reasons:
        raise ProfileValidationError(reasons)

    constraint_fields = (
        "pack_hash",
        "plan.id",
        "plan.revision",
        "project.repository",
        "project.commit",
        "scope.approved",
        "scope.excluded",
        "controls.required",
        "tools.permitted",
        "tools.prohibited",
        "approvals.required_for",
        "execution.stop_conditions",
        "execution.cost_ceiling",
        "execution.retry_ceiling",
        "memory.canonical_promotion",
        "expected_receipt.schema_id",
    )
    value = {
        "schema_id": "grimoire.zeref.profile.v2",
        "schema_version": "2.0",
        "grimoire_version": grimoire_version.strip(),
        "pack_hash_algorithm": "sha256-framed-pack-v1",
        "pack_hash": pack_hash,
        "project": {
            "repository": repository.strip(),
            "commit": commit,
        },
        "plan": {"id": plan_id.strip(), "revision": revision},
        "scope": {
            "approved": list(approved_scope),
            "excluded": list(excluded_scope),
        },
        "mode": mode,
        "required_controls": list(controls),
        "required_documents": list(documents),
        "acceptance_criteria": list(criteria),
        "tools": {
            "permitted": list(permitted_tools),
            "prohibited": list(prohibited_tools),
        },
        "approvals": {"required_for": list(approvals)},
        "execution": {
            "stop_conditions": list(stops),
            "cost_ceiling": cost_ceiling,
            "retry_ceiling": retry_ceiling,
            "model_routing": "zeref_owned_lowest_cost_capable",
            "lead_roles": 1,
            "support_roles_max": 3,
        },
        "memory": {
            "canonical_promotion": "approval_required_single_writer",
        },
        "expected_receipt": {
            "schema_id": "grimoire.zeref.receipt.v1",
            "expiry_seconds": expiry,
        },
        "constraint_trace": _source_trace(constraint_fields),
    }
    return ZerefExecutionProfileV2(value)
