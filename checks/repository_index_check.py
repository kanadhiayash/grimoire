#!/usr/bin/env python3
"""Validate the machine-readable repository index."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parents[1]
INDEX_PATH = "REPOSITORY_INDEX.json"


def _safe_relative_path(value: Any) -> bool:
    if not isinstance(value, str) or not value:
        return False
    path = Path(value)
    return not path.is_absolute() and ".." not in path.parts


def _walk_paths(value: Any) -> Iterable[str]:
    if isinstance(value, str):
        yield value
    elif isinstance(value, list):
        for item in value:
            yield from _walk_paths(item)
    elif isinstance(value, dict):
        for item in value.values():
            yield from _walk_paths(item)


def load_index(root: Path = ROOT) -> dict[str, Any]:
    path = root / INDEX_PATH
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"{INDEX_PATH} must contain a JSON object")
    return value


def validate_index(root: Path = ROOT) -> list[str]:
    errors: list[str] = []
    try:
        index = load_index(root)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        return [f"invalid {INDEX_PATH}: {exc}"]

    required = {
        "schema_version",
        "standard_version",
        "repository",
        "canonical_sources",
        "entrypoints",
        "commands",
        "surfaces",
        "verification",
    }
    missing = sorted(required - set(index))
    if missing:
        errors.append("missing keys: " + ", ".join(missing))

    version_path = root / "VERSION"
    if version_path.is_file():
        version = version_path.read_text(encoding="utf-8").strip()
        if index.get("standard_version") != version:
            errors.append(
                "standard_version does not match VERSION: "
                f"{index.get('standard_version')!r} != {version!r}"
            )
    else:
        errors.append("missing path: VERSION")

    path_groups = [
        index.get("canonical_sources", {}),
        index.get("entrypoints", {}),
    ]
    commands = index.get("commands", {})
    if isinstance(commands, dict):
        path_groups.extend(
            config.get("entrypoint")
            for config in commands.values()
            if isinstance(config, dict)
        )
    else:
        errors.append("commands must be an object")

    surfaces = index.get("surfaces", {})
    if isinstance(surfaces, dict):
        path_groups.extend(
            config.get("adapter")
            for config in surfaces.values()
            if isinstance(config, dict)
        )
    else:
        errors.append("surfaces must be an object")

    for relative in _walk_paths(path_groups):
        if not _safe_relative_path(relative):
            errors.append(f"unsafe path: {relative!r}")
            continue
        if not (root / relative).exists():
            errors.append(f"missing path: {relative}")

    return sorted(set(errors))


def main() -> int:
    errors = validate_index(ROOT)
    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        return 1
    print("Repository index: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
