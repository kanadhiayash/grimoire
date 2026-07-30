"""Dependency-free validation and lookup for authoritative crosswalks."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from types import MappingProxyType
from typing import Any, Mapping

from grimoire.registry.standards import load_standard_registry

EVIDENCE_CLASSES = {
    "automated",
    "manual",
    "assistive_technology",
    "platform",
    "review",
    "artifact",
}
FRAMEWORK_FIELDS = {
    "id",
    "title",
    "version",
    "version_lock",
    "official_url",
    "source_license",
    "license_review",
    "review_date",
    "expires_on",
    "assurance_boundary",
}
ROOT_FIELDS = {
    "schema_version",
    "framework",
    "applicability",
    "known_external_ids",
    "mappings",
}
MAPPING_FIELDS = {
    "external_id",
    "grimoire_control_ids",
    "rationale",
    "evidence_classes",
}
APPLICABILITY_FIELDS = {"product_types", "platforms", "ai_required"}


class CrosswalkValidationError(ValueError):
    """Raised when an external-framework mapping cannot be trusted."""

    def __init__(self, reason_codes: set[str]):
        self.reason_codes = tuple(sorted(reason_codes))
        super().__init__(", ".join(self.reason_codes))


@dataclass(frozen=True)
class Crosswalk:
    id: str
    title: str
    version: str
    official_url: str
    source_license: str
    review_date: str
    expires_on: str
    assurance_boundary: str
    applicability: Mapping[str, Any]
    mappings: Mapping[str, tuple[str, ...]]
    reverse_mappings: Mapping[str, tuple[str, ...]]

    def controls_for(self, external_id: str) -> tuple[str, ...]:
        return self.mappings.get(external_id, ())

    def external_ids_for(self, control_id: str) -> tuple[str, ...]:
        return self.reverse_mappings.get(control_id, ())

    def applies_to(self, manifest: Mapping[str, Any]) -> bool:
        product_types = set(
            manifest.get("project", {}).get("product_types", [])
            if isinstance(manifest.get("project"), dict)
            else []
        )
        platforms = set(manifest.get("platforms", []))
        required_products = set(self.applicability.get("product_types", []))
        required_platforms = set(self.applicability.get("platforms", []))
        if required_products and not product_types.intersection(required_products):
            return False
        if required_platforms and not platforms.intersection(required_platforms):
            return False
        if self.applicability.get("ai_required"):
            ai = manifest.get("ai")
            if not isinstance(ai, dict) or not any(
                ai.get(field) is True
                for field in ("user_facing", "automated_decisions", "external_models")
            ):
                return False
        return True


def _non_empty_strings(value: Any) -> bool:
    return (
        isinstance(value, list)
        and bool(value)
        and all(isinstance(item, str) and bool(item) for item in value)
    )


def _valid_date(value: Any) -> date | None:
    if not isinstance(value, str):
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


def _validate_applicability(value: Any, reasons: set[str]) -> Mapping[str, Any]:
    if not isinstance(value, dict) or set(value) - APPLICABILITY_FIELDS:
        reasons.add("invalid_applicability")
        return MappingProxyType({})
    for field in ("product_types", "platforms"):
        configured = value.get(field, [])
        if not isinstance(configured, list) or not all(
            isinstance(item, str) and item for item in configured
        ):
            reasons.add("invalid_applicability")
    if "ai_required" in value and not isinstance(value["ai_required"], bool):
        reasons.add("invalid_applicability")
    return MappingProxyType(dict(value))


def _load_crosswalk(
    path: Path,
    *,
    valid_control_ids: set[str],
) -> Crosswalk:
    reasons: set[str] = set()
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        raise CrosswalkValidationError({"invalid_json"})
    if not isinstance(value, dict):
        raise CrosswalkValidationError({"type_mismatch"})
    if set(value) != ROOT_FIELDS or value.get("schema_version") != 1:
        reasons.add("invalid_crosswalk_shape")

    framework = value.get("framework")
    if not isinstance(framework, dict) or set(framework) != FRAMEWORK_FIELDS:
        reasons.add("invalid_framework")
        framework = {}
    framework_id = framework.get("id")
    if not isinstance(framework_id, str) or not framework_id:
        reasons.add("invalid_framework")
    for field in ("title", "version", "official_url", "source_license", "license_review"):
        if not isinstance(framework.get(field), str) or not framework.get(field):
            reasons.add("invalid_framework")
    if framework.get("version") != framework.get("version_lock"):
        reasons.add("version_review_required")
    if not str(framework.get("official_url", "")).startswith("https://"):
        reasons.add("invalid_official_source")
    if framework.get("assurance_boundary") != "mapping_only":
        reasons.add("invalid_assurance_boundary")
    review_date = _valid_date(framework.get("review_date"))
    expires_on = _valid_date(framework.get("expires_on"))
    if review_date is None or expires_on is None or expires_on < review_date:
        reasons.add("invalid_source_review")

    applicability = _validate_applicability(value.get("applicability"), reasons)
    known = value.get("known_external_ids")
    known_ids = set(known) if _non_empty_strings(known) else set()
    if not known_ids or len(known_ids) != len(known or []):
        reasons.add("invalid_external_id_catalog")

    mappings = value.get("mappings")
    if not isinstance(mappings, list) or not mappings:
        reasons.add("missing_mappings")
        mappings = []
    forward: dict[str, tuple[str, ...]] = {}
    reverse: dict[str, list[str]] = {}
    seen_pairs: set[tuple[str, str]] = set()
    for mapping in mappings:
        if not isinstance(mapping, dict) or set(mapping) != MAPPING_FIELDS:
            reasons.add("invalid_mapping")
            continue
        external_id = mapping.get("external_id")
        control_ids = mapping.get("grimoire_control_ids")
        evidence = mapping.get("evidence_classes")
        if external_id not in known_ids:
            reasons.add("unknown_external_id")
        if not _non_empty_strings(control_ids):
            reasons.add("invalid_mapping")
            continue
        if not isinstance(mapping.get("rationale"), str) or not mapping["rationale"]:
            reasons.add("invalid_mapping")
        if (
            not _non_empty_strings(evidence)
            or not set(evidence).issubset(EVIDENCE_CLASSES)
        ):
            reasons.add("invalid_evidence_class")
        for control_id in control_ids:
            if control_id not in valid_control_ids:
                reasons.add("unknown_grimoire_control")
            pair = (str(external_id), control_id)
            if pair in seen_pairs:
                reasons.add("duplicate_mapping")
            seen_pairs.add(pair)
            reverse.setdefault(control_id, []).append(str(external_id))
        if isinstance(external_id, str):
            forward[external_id] = tuple(control_ids)

    if reasons:
        raise CrosswalkValidationError(reasons)
    return Crosswalk(
        id=str(framework_id),
        title=str(framework["title"]),
        version=str(framework["version"]),
        official_url=str(framework["official_url"]),
        source_license=str(framework["source_license"]),
        review_date=str(framework["review_date"]),
        expires_on=str(framework["expires_on"]),
        assurance_boundary="mapping_only",
        applicability=applicability,
        mappings=MappingProxyType(forward),
        reverse_mappings=MappingProxyType(
            {key: tuple(sorted(items)) for key, items in reverse.items()}
        ),
    )


def load_crosswalk_registry(
    registry_dir: Path,
    *,
    standards_dir: Path,
    root: Path,
) -> Mapping[str, Crosswalk]:
    if not registry_dir.is_dir():
        raise CrosswalkValidationError({"registry_directory_missing"})
    standards = load_standard_registry(standards_dir, root=root)
    result: dict[str, Crosswalk] = {}
    reasons: set[str] = set()
    for file_path in sorted(registry_dir.rglob("*.json")):
        try:
            crosswalk = _load_crosswalk(
                file_path, valid_control_ids=set(standards)
            )
        except CrosswalkValidationError as exc:
            reasons.update(exc.reason_codes)
            continue
        if crosswalk.id in result:
            reasons.add("duplicate_framework")
        result[crosswalk.id] = crosswalk
    if reasons:
        raise CrosswalkValidationError(reasons)
    return MappingProxyType(result)
