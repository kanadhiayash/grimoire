#!/usr/bin/env python3
"""Verify browser source-pack integrity and truthfulness."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path

SHA = re.compile(r"^[0-9a-f]{40}$")
REQUIRED = [
    "SURFACE_BOOT.md",
    "SOURCES_MANIFEST.json",
    "AGENTS.md",
    "PROVIDER_ADAPTER.md",
    "ZEREF_OPERATIONS_BRIDGE.md",
    "PROJECT_STATE.md",
    "MEMORY_STATE.md",
]
ALLOWED_MODES = {"PROJECT_SIMULATION", "CHAT_SIMULATION"}
RUNTIME_CLAIMS = (
    "local Zeref runtime executed",
    "canonical Zeref memory was written",
    "Zeref plugin ran successfully",
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_pack(directory: Path) -> list[str]:
    errors: list[str] = []
    for name in REQUIRED:
        if not (directory / name).is_file():
            errors.append(f"missing {name}")
    if errors:
        return errors

    try:
        manifest = json.loads(
            (directory / "SOURCES_MANIFEST.json").read_text(encoding="utf-8")
        )
    except (OSError, json.JSONDecodeError) as exc:
        return [f"invalid manifest: {exc}"]

    commits = manifest.get("canonical_sources", {})
    grimoire_record = commits.get("grimoire") or commits.get("engineering_standards")
    if not isinstance(grimoire_record, dict):
        errors.append("grimoire commit is not pinned")
    else:
        commit = grimoire_record.get("commit")
        if not isinstance(commit, str) or not SHA.fullmatch(commit):
            errors.append("grimoire commit is not pinned")
    zeref_commit = commits.get("zeref_memory_engine", {}).get("commit")
    if not isinstance(zeref_commit, str) or not SHA.fullmatch(zeref_commit):
        errors.append("zeref_memory_engine commit is not pinned")

    if manifest.get("activation_mode") not in ALLOWED_MODES:
        errors.append("browser pack must use PROJECT_SIMULATION or CHAT_SIMULATION")

    if manifest.get("required_read_order") != REQUIRED:
        errors.append("required read order does not match canonical order")

    file_records = manifest.get("files")
    if not isinstance(file_records, dict):
        errors.append("manifest files must be an object")
    else:
        for name in REQUIRED:
            if name == "SOURCES_MANIFEST.json":
                continue
            record = file_records.get(name)
            if not isinstance(record, dict):
                errors.append(f"missing hash record for {name}")
                continue
            if sha256(directory / name) != record.get("sha256"):
                errors.append(f"hash mismatch for {name}")

    combined = "\n".join(
        (directory / name).read_text(encoding="utf-8")
        for name in REQUIRED
        if name != "SOURCES_MANIFEST.json"
    )
    for claim in RUNTIME_CLAIMS:
        if claim in combined:
            errors.append(f"forbidden runtime claim: {claim}")

    disclaimer = (
        "Browser project state is a source-backed snapshot, not proof that "
        "the local Zeref canonical writer ran."
    )
    if disclaimer not in (directory / "MEMORY_STATE.md").read_text(encoding="utf-8"):
        errors.append("memory disclaimer missing")

    generated = manifest.get("generated_at")
    max_age = manifest.get("freshness_max_age_days")
    if isinstance(generated, str) and isinstance(max_age, int):
        try:
            timestamp = datetime.fromisoformat(generated.replace("Z", "+00:00"))
            age = datetime.now(timezone.utc) - timestamp.astimezone(timezone.utc)
            if age.days > max_age:
                errors.append(f"pack is stale by policy: {age.days} days old")
        except ValueError:
            errors.append("generated_at is not ISO-8601")
    else:
        errors.append("freshness metadata missing")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("directory")
    args = parser.parse_args()
    errors = verify_pack(Path(args.directory).resolve())
    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        return 1
    print("Surface pack: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
