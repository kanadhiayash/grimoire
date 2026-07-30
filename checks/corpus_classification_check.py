#!/usr/bin/env python3
"""Verify that every standards document has one conservative classification."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
INVENTORY_PATH = "inventory/standards-classification.json"
CLASSIFICATIONS = {
    "NORMATIVE",
    "LEGACY_NORMATIVE",
    "GUIDANCE",
    "TEMPLATE",
    "EXAMPLE",
    "DRAFT",
    "SUPERSEDED",
}
REQUIRED_FIELDS = {
    "path",
    "classification",
    "domain",
    "owner",
    "review_status",
    "migration_target",
}


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _registry_documents(root: Path) -> dict[str, str]:
    records: dict[str, str] = {}
    for path in sorted((root / "registry" / "standards").rglob("*.json")):
        try:
            value = _load_json(path)
        except (OSError, UnicodeError, json.JSONDecodeError):
            continue
        if isinstance(value, dict):
            document = value.get("human_document")
            standard_id = value.get("id")
            if isinstance(document, str) and isinstance(standard_id, str):
                records[document] = standard_id
    return records


def validate_classification(root: Path = ROOT) -> list[str]:
    """Return stable errors without treating legacy content as compilable."""

    errors: list[str] = []
    try:
        inventory = _load_json(root / INVENTORY_PATH)
    except (OSError, UnicodeError, json.JSONDecodeError):
        return ["invalid_inventory"]
    if not isinstance(inventory, dict):
        return ["invalid_inventory"]
    documents = inventory.get("documents")
    if inventory.get("schema_version") != 1:
        errors.append("unsupported_inventory_schema")
    if not isinstance(documents, list):
        return sorted(errors + ["invalid_documents"])

    discovered = {
        path.relative_to(root).as_posix()
        for path in (root / "standards").rglob("*.md")
    }
    registry_documents = _registry_documents(root)
    paths: set[str] = set()
    normative: set[str] = set()
    for entry in documents:
        if not isinstance(entry, dict):
            errors.append("invalid_entry")
            continue
        path = entry.get("path")
        if not isinstance(path, str):
            errors.append("invalid_path")
            continue
        if path in paths:
            errors.append(f"duplicate_path:{path}")
        paths.add(path)
        missing = REQUIRED_FIELDS - set(entry)
        if missing:
            errors.append(f"missing_fields:{path}")
        classification = entry.get("classification")
        if classification not in CLASSIFICATIONS:
            errors.append(f"unknown_classification:{path}")
        if path not in discovered:
            errors.append(f"unknown_document:{path}")
        for field in ("domain", "owner", "review_status", "migration_target"):
            if not isinstance(entry.get(field), str) or not entry[field]:
                errors.append(f"invalid_{field}:{path}")
        if classification == "NORMATIVE":
            normative.add(path)
            if registry_documents.get(path) != entry.get("migration_target"):
                errors.append(f"normative_record_missing:{path}")

    for path in sorted(discovered - paths):
        errors.append(f"unclassified_document:{path}")
    for path in sorted(paths - discovered):
        errors.append(f"unknown_document:{path}")
    if normative != set(registry_documents):
        for path in sorted(set(registry_documents) - normative):
            errors.append(f"registry_document_not_normative:{path}")
    return sorted(set(errors))


def main() -> int:
    errors = validate_classification(ROOT)
    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        return 1
    print("Corpus classification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
