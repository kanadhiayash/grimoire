"""Strict dependency-free project manifest validation."""

from __future__ import annotations

import json
import re
import unicodedata
from pathlib import Path
from typing import Any, Collection

from grimoire.errors import ManifestIssue, ManifestValidationError
from grimoire.models.manifest import (
    AIConfig,
    DataConfig,
    ProjectConfig,
    RiskConfig,
    StackConfig,
    StandardsConfig,
    ValidatedManifest,
    ZerefConfig,
)


ROOT = Path(__file__).resolve().parents[3]
MAX_DOCUMENT_BYTES = 1_048_576
MAX_PROJECT_NAME = 200
MAX_TAXONOMY_ITEM = 128
MAX_UNKNOWN = 2_048
MAX_SCHEMA_URI = 2_048
MAX_COLLECTION_ITEMS = 64
SEMVER = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+$")
SAFE_PROPERTY_NAME = re.compile(r"^[A-Za-z_][A-Za-z0-9_-]{0,63}$")
LIFECYCLE_STAGES = (
    "DISCOVER",
    "DEFINE",
    "DESIGN",
    "VALIDATE",
    "DECISION_LOCKED",
    "BUILD_READY",
    "BUILDING",
    "VERIFYING",
    "RELEASE_READY",
    "SHIPPED",
    "OPERATING",
    "RETIRED",
)
RISK_LEVELS = ("low", "moderate", "high", "critical")
ZEREF_MODES = ("advisory", "standard", "strict", "off")
ROOT_KEYS = {
    "$schema",
    "schema_version",
    "project",
    "users",
    "markets",
    "platforms",
    "stack",
    "data",
    "ai",
    "risk",
    "standards",
    "zeref",
    "unknowns",
}


def _load_json_object(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"{path.name} must contain a JSON object")
    return value


def supported_standards_versions(root: Path = ROOT) -> tuple[str, ...]:
    policy = _load_json_object(root / "policies" / "standards-orchestrator.json")
    baseline = _load_json_object(root / "policies" / "baseline.json")
    module_version = policy.get("module_version")
    declared_version = (
        baseline.get("standards_orchestrator", {}).get("policy_version")
    )
    if (
        not isinstance(module_version, str)
        or module_version != declared_version
        or not SEMVER.fullmatch(module_version)
    ):
        raise RuntimeError("standards policy version sources disagree")
    return (module_version,)


def _actual_type(value: Any) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, int):
        return "integer"
    if isinstance(value, float):
        return "number"
    if isinstance(value, str):
        return "string"
    if isinstance(value, list):
        return "array"
    if isinstance(value, dict):
        return "object"
    return type(value).__name__


def _issue(
    issues: list[ManifestIssue],
    code: str,
    path: str,
    expected: str,
    actual: str,
) -> None:
    issues.append(
        ManifestIssue(
            code=code,
            path=path,
            expected=expected,
            actual=actual,
        )
    )


def _has_control_character(value: str) -> bool:
    return any(unicodedata.category(character) == "Cc" for character in value)


def _string(
    value: Any,
    *,
    path: str,
    issues: list[ManifestIssue],
    minimum: int = 1,
    maximum: int = MAX_TAXONOMY_ITEM,
) -> str:
    if not isinstance(value, str):
        _issue(issues, "type_mismatch", path, "string", _actual_type(value))
        return ""
    if len(value) < minimum:
        _issue(issues, "string_too_short", path, f"minimum_length_{minimum}", "string")
    if len(value) > maximum:
        _issue(issues, "string_too_long", path, f"maximum_length_{maximum}", "string")
    if _has_control_character(value):
        _issue(
            issues,
            "control_character",
            path,
            "text_without_control_characters",
            "string",
        )
    return value


def _string_array(
    value: Any,
    *,
    path: str,
    issues: list[ManifestIssue],
    required_nonempty: bool = False,
    item_maximum: int = MAX_TAXONOMY_ITEM,
) -> tuple[str, ...]:
    if not isinstance(value, list):
        _issue(issues, "type_mismatch", path, "array", _actual_type(value))
        return ()
    if required_nonempty and not value:
        _issue(issues, "empty_collection", path, "non_empty_array", "array")
    if len(value) > MAX_COLLECTION_ITEMS:
        _issue(
            issues,
            "collection_too_large",
            path,
            f"maximum_items_{MAX_COLLECTION_ITEMS}",
            "array",
        )
    result: list[str] = []
    for index, item in enumerate(value):
        result.append(
            _string(
                item,
                path=f"{path}[{index}]",
                issues=issues,
                maximum=item_maximum,
            )
        )
    return tuple(result)


def _object(
    value: Any,
    *,
    path: str,
    issues: list[ManifestIssue],
) -> dict[str, Any] | None:
    if not isinstance(value, dict):
        _issue(issues, "type_mismatch", path, "object", _actual_type(value))
        return None
    return value


def _unknown_properties(
    value: dict[str, Any],
    allowed: set[str],
    *,
    path: str,
    issues: list[ManifestIssue],
) -> None:
    child_paths: set[str] = set()
    for key in value:
        if key in allowed:
            continue
        if isinstance(key, str) and SAFE_PROPERTY_NAME.fullmatch(key):
            child_path = f"$.{key}" if path == "$" else f"{path}.{key}"
        else:
            child_path = f"$.*" if path == "$" else f"{path}.*"
        child_paths.add(child_path)
    for child_path in sorted(child_paths):
        _issue(issues, "unknown_property", child_path, "known_property", "property")


def _required(
    value: dict[str, Any],
    names: tuple[str, ...],
    *,
    path: str,
    issues: list[ManifestIssue],
) -> None:
    for name in names:
        if name not in value:
            child_path = f"$.{name}" if path == "$" else f"{path}.{name}"
            _issue(issues, "missing_required", child_path, "required", "missing")


def _boolean(
    value: Any,
    *,
    path: str,
    issues: list[ManifestIssue],
    default: bool,
) -> bool:
    if not isinstance(value, bool):
        _issue(issues, "type_mismatch", path, "boolean", _actual_type(value))
        return default
    return value


def _enum(
    value: Any,
    allowed: tuple[str, ...],
    *,
    path: str,
    issues: list[ManifestIssue],
) -> str:
    parsed = _string(value, path=path, issues=issues)
    if isinstance(value, str) and value not in allowed:
        _issue(
            issues,
            "unsupported_value",
            path,
            "one_of_" + "_".join(allowed),
            "string",
        )
    return parsed


def validate_manifest(
    value: Any,
    supported_versions: Collection[str],
) -> ValidatedManifest:
    issues: list[ManifestIssue] = []
    supported = tuple(sorted(set(supported_versions)))
    if not supported:
        raise RuntimeError("at least one supported standards version is required")
    if not isinstance(value, dict):
        raise ManifestValidationError(
            [
                ManifestIssue(
                    code="type_mismatch",
                    path="$",
                    expected="object",
                    actual=_actual_type(value),
                )
            ]
        )

    _unknown_properties(value, ROOT_KEYS, path="$", issues=issues)
    _required(
        value,
        ("schema_version", "project", "risk", "standards", "zeref"),
        path="$",
        issues=issues,
    )

    schema_uri: str | None = None
    if "$schema" in value:
        schema_uri = _string(
            value["$schema"],
            path="$.$schema",
            issues=issues,
            maximum=MAX_SCHEMA_URI,
        )

    schema_version_value = value.get("schema_version", 0)
    integral_schema_version = (
        isinstance(schema_version_value, int)
        and not isinstance(schema_version_value, bool)
    ) or (
        isinstance(schema_version_value, float)
        and schema_version_value.is_integer()
    )
    if not integral_schema_version:
        _issue(
            issues,
            "type_mismatch",
            "$.schema_version",
            "integer",
            _actual_type(schema_version_value),
        )
        schema_version = 0
    else:
        schema_version = int(schema_version_value)
        if schema_version != 1:
            _issue(
                issues,
                "unsupported_value",
                "$.schema_version",
                "1",
                "integer",
            )

    project_value = _object(
        value.get("project"),
        path="$.project",
        issues=issues,
    )
    project = ProjectConfig("", "", ())
    if project_value is not None:
        _unknown_properties(
            project_value,
            {"name", "lifecycle_stage", "product_types"},
            path="$.project",
            issues=issues,
        )
        _required(
            project_value,
            ("name", "lifecycle_stage", "product_types"),
            path="$.project",
            issues=issues,
        )
        project = ProjectConfig(
            name=_string(
                project_value.get("name"),
                path="$.project.name",
                issues=issues,
                maximum=MAX_PROJECT_NAME,
            ),
            lifecycle_stage=_enum(
                project_value.get("lifecycle_stage"),
                LIFECYCLE_STAGES,
                path="$.project.lifecycle_stage",
                issues=issues,
            ),
            product_types=_string_array(
                project_value.get("product_types"),
                path="$.project.product_types",
                issues=issues,
                required_nonempty=True,
            ),
        )

    users = _string_array(
        value.get("users", []),
        path="$.users",
        issues=issues,
    )
    markets = _string_array(
        value.get("markets", []),
        path="$.markets",
        issues=issues,
    )
    platforms = _string_array(
        value.get("platforms", []),
        path="$.platforms",
        issues=issues,
    )
    unknowns = _string_array(
        value.get("unknowns", []),
        path="$.unknowns",
        issues=issues,
        item_maximum=MAX_UNKNOWN,
    )

    stack_value = _object(
        value.get("stack", {}),
        path="$.stack",
        issues=issues,
    )
    stack = StackConfig()
    if stack_value is not None:
        _unknown_properties(
            stack_value,
            {"languages", "frameworks", "services"},
            path="$.stack",
            issues=issues,
        )
        stack = StackConfig(
            languages=_string_array(
                stack_value.get("languages", []),
                path="$.stack.languages",
                issues=issues,
            ),
            frameworks=_string_array(
                stack_value.get("frameworks", []),
                path="$.stack.frameworks",
                issues=issues,
            ),
            services=_string_array(
                stack_value.get("services", []),
                path="$.stack.services",
                issues=issues,
            ),
        )

    data_value = _object(
        value.get("data", {}),
        path="$.data",
        issues=issues,
    )
    data = DataConfig()
    if data_value is not None:
        _unknown_properties(
            data_value,
            {"personal_data", "sensitive"},
            path="$.data",
            issues=issues,
        )
        data = DataConfig(
            personal_data=_boolean(
                data_value.get("personal_data", False),
                path="$.data.personal_data",
                issues=issues,
                default=False,
            ),
            sensitive=_string_array(
                data_value.get("sensitive", []),
                path="$.data.sensitive",
                issues=issues,
            ),
        )

    ai_value = _object(value.get("ai", {}), path="$.ai", issues=issues)
    ai = AIConfig()
    if ai_value is not None:
        _unknown_properties(
            ai_value,
            {"user_facing", "automated_decisions", "external_models"},
            path="$.ai",
            issues=issues,
        )
        ai = AIConfig(
            user_facing=_boolean(
                ai_value.get("user_facing", False),
                path="$.ai.user_facing",
                issues=issues,
                default=False,
            ),
            automated_decisions=_boolean(
                ai_value.get("automated_decisions", False),
                path="$.ai.automated_decisions",
                issues=issues,
                default=False,
            ),
            external_models=_boolean(
                ai_value.get("external_models", False),
                path="$.ai.external_models",
                issues=issues,
                default=False,
            ),
        )

    risk_value = _object(value.get("risk"), path="$.risk", issues=issues)
    risk = RiskConfig()
    if risk_value is not None:
        _unknown_properties(
            risk_value,
            {"level"},
            path="$.risk",
            issues=issues,
        )
        _required(risk_value, ("level",), path="$.risk", issues=issues)
        risk = RiskConfig(
            level=_enum(
                risk_value.get("level"),
                RISK_LEVELS,
                path="$.risk.level",
                issues=issues,
            )
        )

    standards_value = _object(
        value.get("standards"),
        path="$.standards",
        issues=issues,
    )
    standards = StandardsConfig()
    if standards_value is not None:
        _unknown_properties(
            standards_value,
            {"version"},
            path="$.standards",
            issues=issues,
        )
        _required(
            standards_value,
            ("version",),
            path="$.standards",
            issues=issues,
        )
        version = _string(
            standards_value.get("version"),
            path="$.standards.version",
            issues=issues,
            maximum=32,
        )
        if isinstance(standards_value.get("version"), str):
            if not SEMVER.fullmatch(version):
                _issue(
                    issues,
                    "constraint_violation",
                    "$.standards.version",
                    "semantic_version",
                    "string",
                )
            elif version not in supported:
                _issue(
                    issues,
                    "unsupported_version",
                    "$.standards.version",
                    "supported_standards_version",
                    "string",
                )
        standards = StandardsConfig(version=version)

    zeref_value = _object(value.get("zeref"), path="$.zeref", issues=issues)
    zeref = ZerefConfig()
    if zeref_value is not None:
        _unknown_properties(
            zeref_value,
            {"mode", "cost_ceiling"},
            path="$.zeref",
            issues=issues,
        )
        _required(zeref_value, ("mode",), path="$.zeref", issues=issues)
        zeref = ZerefConfig(
            mode=_enum(
                zeref_value.get("mode"),
                ZEREF_MODES,
                path="$.zeref.mode",
                issues=issues,
            ),
            cost_ceiling=_string(
                zeref_value.get("cost_ceiling", "bounded"),
                path="$.zeref.cost_ceiling",
                issues=issues,
            ),
        )

    if issues:
        raise ManifestValidationError(issues)
    return ValidatedManifest(
        schema_uri=schema_uri,
        schema_version=schema_version,
        project=project,
        users=users,
        markets=markets,
        platforms=platforms,
        stack=stack,
        data=data,
        ai=ai,
        risk=risk,
        standards=standards,
        zeref=zeref,
        unknowns=unknowns,
    )


def load_and_validate_manifest(
    path: Path,
    supported_versions: Collection[str],
) -> ValidatedManifest:
    try:
        if path.stat().st_size > MAX_DOCUMENT_BYTES:
            raise ManifestValidationError(
                [
                    ManifestIssue(
                        "document_too_large",
                        "$",
                        f"maximum_bytes_{MAX_DOCUMENT_BYTES}",
                        "file",
                    )
                ]
            )
        text = path.read_text(encoding="utf-8")
    except ManifestValidationError:
        raise
    except (OSError, UnicodeError):
        raise ManifestValidationError(
            [
                ManifestIssue(
                    "manifest_read_error",
                    "$",
                    "readable_utf8_json",
                    "io_error",
                )
            ]
        ) from None
    try:
        value = json.loads(text)
    except (json.JSONDecodeError, RecursionError, ValueError):
        raise ManifestValidationError(
            [
                ManifestIssue(
                    "malformed_json",
                    "$",
                    "valid_json",
                    "malformed_json",
                )
            ]
        ) from None
    return validate_manifest(value, supported_versions)
