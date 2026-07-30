"""Dependency-free standard record registry validation."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from types import MappingProxyType
from typing import Any, Mapping

STANDARD_ID = re.compile(r"^GRIM-STD-[0-9]{4}$")
SEMVER = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+$")
NORMATIVE_STATUS = "normative"
NON_NORMATIVE_STATUSES = {"guidance", "draft", "example", "superseded"}
REQUIREMENT_LEVELS = {"must", "should", "may", "must_not"}
SOURCE_TYPES = {"local_policy", "official_source", "approved_crosswalk"}
REQUIRED_FIELDS = {
    "id",
    "version",
    "status",
    "domain",
    "requirement_level",
    "title",
    "owner",
    "review_date",
    "human_document",
    "provenance",
    "applicability",
}


class RegistryValidationError(ValueError):
    """Raised when a registry cannot be accepted for compilation."""

    def __init__(self, reason_codes: set[str]):
        if not reason_codes:
            raise ValueError("registry validation error requires a reason")
        self.reason_codes = tuple(sorted(reason_codes))
        super().__init__(", ".join(self.reason_codes))


@dataclass(frozen=True)
class StandardRecord:
    id: str
    version: str
    status: str
    domain: str
    requirement_level: str
    title: str
    owner: str
    review_date: str
    human_document: str
    provenance: Mapping[str, str]
    applicability: Mapping[str, Any]

    @classmethod
    def from_json(cls, value: Mapping[str, Any]) -> "StandardRecord":
        provenance = value["provenance"]
        applicability = value["applicability"]
        if not isinstance(provenance, dict) or not isinstance(applicability, dict):
            raise RegistryValidationError({"type_mismatch"})
        return cls(
            id=str(value["id"]),
            version=str(value["version"]),
            status=str(value["status"]),
            domain=str(value["domain"]),
            requirement_level=str(value["requirement_level"]),
            title=str(value["title"]),
            owner=str(value["owner"]),
            review_date=str(value["review_date"]),
            human_document=str(value["human_document"]),
            provenance=MappingProxyType(
                {str(key): str(item) for key, item in provenance.items()}
            ),
            applicability=MappingProxyType(dict(applicability)),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "version": self.version,
            "status": self.status,
            "domain": self.domain,
            "requirement_level": self.requirement_level,
            "title": self.title,
            "owner": self.owner,
            "review_date": self.review_date,
            "human_document": self.human_document,
            "provenance": dict(self.provenance),
            "applicability": dict(self.applicability),
        }


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _path_inside(root: Path, relative: str) -> bool:
    try:
        resolved = (root / relative).resolve()
        root_resolved = root.resolve()
    except OSError:
        return False
    return resolved == root_resolved or root_resolved in resolved.parents


def _validate_record(value: Any, *, root: Path, seen: set[str]) -> StandardRecord:
    reasons: set[str] = set()
    if not isinstance(value, dict):
        raise RegistryValidationError({"type_mismatch"})

    missing = REQUIRED_FIELDS - set(value)
    if missing:
        reasons.add("missing_required")

    record_id = value.get("id")
    if not isinstance(record_id, str) or not STANDARD_ID.fullmatch(record_id):
        reasons.add("invalid_id")
    elif record_id in seen:
        reasons.add("duplicate_id")

    version = value.get("version")
    if not isinstance(version, str) or not SEMVER.fullmatch(version):
        reasons.add("invalid_version")

    status = value.get("status")
    if status != NORMATIVE_STATUS:
        if status in NON_NORMATIVE_STATUSES:
            reasons.add("non_normative_record")
        else:
            reasons.add("invalid_status")

    if value.get("requirement_level") not in REQUIREMENT_LEVELS:
        reasons.add("invalid_requirement_level")

    review_date = value.get("review_date")
    if not isinstance(review_date, str):
        reasons.add("invalid_review_date")
    else:
        try:
            date.fromisoformat(review_date)
        except ValueError:
            reasons.add("invalid_review_date")

    provenance = value.get("provenance")
    if not isinstance(provenance, dict):
        reasons.add("missing_provenance")
    elif provenance.get("source_type") not in SOURCE_TYPES or not provenance.get(
        "source_id"
    ):
        reasons.add("missing_provenance")

    human_document = value.get("human_document")
    if not isinstance(human_document, str):
        reasons.add("invalid_human_document")
    elif not _path_inside(root, human_document):
        reasons.add("path_escape")
    elif not (root / human_document).is_file():
        reasons.add("missing_human_document")

    for string_field in ("domain", "title", "owner"):
        if not isinstance(value.get(string_field), str) or not value.get(string_field):
            reasons.add("missing_required")

    if not isinstance(value.get("applicability"), dict):
        reasons.add("type_mismatch")

    if reasons:
        raise RegistryValidationError(reasons)

    seen.add(str(record_id))
    return StandardRecord.from_json(value)


def load_standard_registry(
    registry_dir: Path,
    *,
    root: Path,
) -> Mapping[str, StandardRecord]:
    """Load normative records keyed by stable ID."""

    if not registry_dir.is_dir():
        raise RegistryValidationError({"registry_directory_missing"})

    records: dict[str, StandardRecord] = {}
    seen: set[str] = set()
    reason_codes: set[str] = set()
    for path in sorted(registry_dir.glob("*.json")):
        try:
            value = _load_json(path)
            record = _validate_record(value, root=root, seen=seen)
        except (OSError, UnicodeError, json.JSONDecodeError):
            reason_codes.add("invalid_json")
            continue
        except RegistryValidationError as exc:
            reason_codes.update(exc.reason_codes)
            continue
        records[record.id] = record

    if reason_codes:
        raise RegistryValidationError(reason_codes)
    return MappingProxyType(records)
