"""Dependency-free standard record registry validation."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from types import MappingProxyType
from typing import Any, Mapping

from grimoire.predicates import PredicateValidationError, validate_predicate

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
SOURCE_RECORD_REQUIRED_FIELDS = {
    "id",
    "source_type",
    "path",
    "review_date",
    "expires_on",
}
UNIVERSAL_GOVERNANCE_CONTRACT_FIELDS = {
    "expected_outcomes",
    "required_actions",
    "expected_documents",
    "acceptance",
    "verification",
    "evidence",
    "failure_conditions",
    "exceptions",
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
    contract: Mapping[str, Any] = field(default_factory=dict)

    @classmethod
    def from_json(cls, value: Mapping[str, Any]) -> "StandardRecord":
        provenance = value["provenance"]
        applicability = value["applicability"]
        contract = value.get("contract", {})
        if (
            not isinstance(provenance, dict)
            or not isinstance(applicability, dict)
            or not isinstance(contract, dict)
        ):
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
            contract=MappingProxyType(dict(contract)),
        )

    def to_dict(self) -> dict[str, Any]:
        result = {
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
        if self.contract:
            result["contract"] = dict(self.contract)
        return result


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _parse_date(value: Any) -> date | None:
    if not isinstance(value, str):
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


def _load_source_records(root: Path) -> Mapping[str, Mapping[str, str]]:
    """Load reviewed source records when a registry is present.

    Source records are deliberately separate from legal sources.  They bind a
    local policy record to its human-readable canonical document without
    treating the document itself as unreviewed input.
    """

    source_dir = root / "registry" / "sources"
    if not source_dir.exists():
        return MappingProxyType({})
    if not source_dir.is_dir():
        raise RegistryValidationError({"source_registry_invalid"})

    records: dict[str, Mapping[str, str]] = {}
    reasons: set[str] = set()
    for path in sorted(source_dir.rglob("*.json")):
        try:
            document = _load_json(path)
        except (OSError, UnicodeError, json.JSONDecodeError):
            reasons.add("source_registry_invalid")
            continue
        entries = document.get("sources") if isinstance(document, dict) else None
        if document.get("schema_version") != 1 or not isinstance(entries, list):
            reasons.add("source_registry_invalid")
            continue
        for entry in entries:
            if not isinstance(entry, dict) or SOURCE_RECORD_REQUIRED_FIELDS - set(entry):
                reasons.add("source_registry_invalid")
                continue
            source_id = entry.get("id")
            source_type = entry.get("source_type")
            source_path = entry.get("path")
            review_date = _parse_date(entry.get("review_date"))
            expires_on = _parse_date(entry.get("expires_on"))
            if (
                not isinstance(source_id, str)
                or not source_id
                or source_id in records
                or source_type not in SOURCE_TYPES
                or not isinstance(source_path, str)
                or not _path_inside(root, source_path)
                or not (root / source_path).is_file()
                or review_date is None
                or expires_on is None
                or expires_on < review_date
            ):
                reasons.add("source_registry_invalid")
                continue
            records[source_id] = MappingProxyType(
                {
                    "source_type": source_type,
                    "path": source_path,
                    "review_date": review_date.isoformat(),
                    "expires_on": expires_on.isoformat(),
                }
            )
    if reasons:
        raise RegistryValidationError(reasons)
    return MappingProxyType(records)


def _path_inside(root: Path, relative: str) -> bool:
    try:
        resolved = (root / relative).resolve()
        root_resolved = root.resolve()
    except OSError:
        return False
    return resolved == root_resolved or root_resolved in resolved.parents


def _validate_record(
    value: Any,
    *,
    root: Path,
    seen: set[str],
    source_records: Mapping[str, Mapping[str, str]],
) -> StandardRecord:
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
    else:
        source = source_records.get(provenance["source_id"])
        if source is None and source_records:
            reasons.add("missing_source_record")
        elif source is not None and (
            source["source_type"] != provenance["source_type"]
            or source["path"] != value.get("human_document")
        ):
            reasons.add("source_provenance_mismatch")
        elif source is not None and date.fromisoformat(source["expires_on"]) < date.today():
            reasons.add("expired_source_review")

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
    else:
        try:
            validate_predicate(value["applicability"])
        except PredicateValidationError:
            reasons.add("invalid_applicability")

    contract = value.get("contract")
    if value.get("domain") == "universal-governance":
        if not isinstance(contract, dict) or set(contract) != UNIVERSAL_GOVERNANCE_CONTRACT_FIELDS:
            reasons.add("invalid_contract")
        elif any(not isinstance(contract[key], list) or not contract[key] for key in UNIVERSAL_GOVERNANCE_CONTRACT_FIELDS):
            reasons.add("invalid_contract")
    elif contract is not None and not isinstance(contract, dict):
        reasons.add("invalid_contract")

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
    source_records = _load_source_records(root)
    for path in sorted(registry_dir.rglob("*.json")):
        try:
            value = _load_json(path)
            record = _validate_record(
                value,
                root=root,
                seen=seen,
                source_records=source_records,
            )
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
