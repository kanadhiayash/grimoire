"""Independent verifier for generated Grimoire project packs."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REQUIRED_FILES = (
    "AI_CONTEXT.md",
    "CONTROL_PACK.json",
    "PROJECT_STATUS.json",
    "EXPECTED_OUTCOMES.md",
    "REQUIRED_DOCUMENTS.md",
    "DOCUMENT_SCHEMAS.json",
    "REQUIRED_GATES.md",
    "ACCEPTANCE_MATRIX.md",
    "VERIFICATION_PLAN.md",
    "SOURCE_MANIFEST.json",
    "ZEREF_EXECUTION_PROFILE.json",
    "CONTROL_TRACE.json",
    "CONFLICT_REPORT.json",
    "EXCLUSIONS.json",
    "EXECUTION_RECEIPT.json",
)
MODES = {"offline", "connected", "release"}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


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


def _add(reason_codes: set[str], code: str) -> None:
    reason_codes.add(code)


def verify_project_pack(
    directory: Path,
    *,
    mode: str = "offline",
    now: datetime | None = None,
) -> dict[str, Any]:
    """Verify pack integrity without using compiler success as evidence."""

    if mode not in MODES:
        raise ValueError("verification mode must be offline, connected, or release")

    root = directory.resolve()
    reason_codes: set[str] = set()
    expected = set(REQUIRED_FILES)
    if not root.is_dir():
        _add(reason_codes, "pack_directory_missing")
        return _result(reason_codes, mode)

    actual = {path.name for path in root.iterdir() if path.is_file()}
    missing = expected - actual
    unexpected = actual - expected
    if missing:
        _add(reason_codes, "missing_file")
    if unexpected:
        _add(reason_codes, "unexpected_file")

    receipt: dict[str, Any] | None = None
    source_manifest: dict[str, Any] | None = None
    if "EXECUTION_RECEIPT.json" in actual:
        try:
            loaded = _load_json(root / "EXECUTION_RECEIPT.json")
            if isinstance(loaded, dict):
                receipt = loaded
            else:
                _add(reason_codes, "invalid_receipt")
        except (OSError, UnicodeError, json.JSONDecodeError):
            _add(reason_codes, "invalid_receipt")
    if "SOURCE_MANIFEST.json" in actual:
        try:
            loaded = _load_json(root / "SOURCE_MANIFEST.json")
            if isinstance(loaded, dict):
                source_manifest = loaded
            else:
                _add(reason_codes, "invalid_source_manifest")
        except (OSError, UnicodeError, json.JSONDecodeError):
            _add(reason_codes, "invalid_source_manifest")

    if receipt is None:
        _add(reason_codes, "migration_required")
    else:
        receipt_files = receipt.get("output_files")
        if receipt_files != list(REQUIRED_FILES):
            _add(reason_codes, "file_set_mismatch")
        hashes = receipt.get("sha256")
        if not isinstance(hashes, dict):
            _add(reason_codes, "hash_manifest_missing")
        else:
            for name in REQUIRED_FILES[:-1]:
                if name not in actual:
                    continue
                if hashes.get(name) != _sha256(root / name):
                    _add(reason_codes, "hash_mismatch")
        receipt_time = _parse_time(receipt.get("generated_at"))
        if receipt_time is None:
            _add(reason_codes, "invalid_timestamp")
        elif receipt_time > (now or datetime.now(timezone.utc)):
            _add(reason_codes, "future_timestamp")

    if source_manifest is not None:
        source_time = _parse_time(source_manifest.get("generated_at"))
        if source_time is None:
            _add(reason_codes, "invalid_timestamp")
        elif source_time > (now or datetime.now(timezone.utc)):
            _add(reason_codes, "future_timestamp")
        if receipt is not None and source_manifest.get("generated_at") != receipt.get(
            "generated_at"
        ):
            _add(reason_codes, "timestamp_mismatch")

    if "CONTROL_TRACE.json" in actual:
        try:
            trace = _load_json(root / "CONTROL_TRACE.json")
            controls = trace.get("controls") if isinstance(trace, dict) else None
            completeness = trace.get("trace_completeness") if isinstance(trace, dict) else None
            if not isinstance(controls, list) or not isinstance(completeness, dict):
                _add(reason_codes, "invalid_control_trace")
            elif (
                completeness.get("status") != "PASS"
                or completeness.get("actual") != len(controls)
                or completeness.get("expected") != len(controls)
            ):
                _add(reason_codes, "incomplete_control_trace")
            elif any(
                not isinstance(control, dict)
                or not isinstance(control.get("standard_id"), str)
                or not isinstance(control.get("version"), str)
                or not isinstance(control.get("state"), str)
                or not isinstance(control.get("reason_codes"), list)
                or not isinstance(control.get("predicate_trace"), dict)
                or not isinstance(control.get("provenance"), dict)
                for control in controls
            ):
                _add(reason_codes, "invalid_control_trace")
        except (OSError, UnicodeError, json.JSONDecodeError):
            _add(reason_codes, "invalid_control_trace")

    return _result(reason_codes, mode)


def _result(reason_codes: set[str], mode: str) -> dict[str, Any]:
    if mode == "offline":
        source_authenticity_status = "NOT_VERIFIED"
        reason_codes.add("offline_remote_source_not_checked")
    else:
        source_authenticity_status = "NOT_VERIFIED"
        reason_codes.add("remote_source_verification_not_implemented")

    failures = {
        code
        for code in reason_codes
        if code
        not in {
            "offline_remote_source_not_checked",
            "remote_source_verification_not_implemented",
        }
    }
    return {
        "status": "FAIL" if failures else "PASS",
        "verification_mode": mode,
        "source_authenticity_status": source_authenticity_status,
        "reason_codes": sorted(reason_codes),
    }
