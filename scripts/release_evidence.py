#!/usr/bin/env python3
"""Generate, verify, or dry-run rollback for release evidence."""

from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from grimoire.release import (  # noqa: E402
    ReleaseEvidenceError,
    build_release_evidence,
    rollback_dry_run,
    verify_release_evidence,
)


def _load(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ReleaseEvidenceError("release_evidence_not_object")
    return value


def _write(path: Path, value: dict) -> None:
    artifacts_root = (ROOT / "artifacts").resolve()
    candidate = path if path.is_absolute() else ROOT / path
    resolved = candidate.resolve(strict=False)
    try:
        resolved.relative_to(artifacts_root)
    except ValueError as exc:
        raise ReleaseEvidenceError(
            "unsafe_release_evidence_output"
        ) from exc
    cursor = candidate
    while cursor != ROOT and cursor != cursor.parent:
        if cursor.is_symlink():
            raise ReleaseEvidenceError("unsafe_release_evidence_output")
        cursor = cursor.parent
    if cursor != ROOT:
        raise ReleaseEvidenceError("unsafe_release_evidence_output")
    resolved.parent.mkdir(parents=True, exist_ok=True)
    temporary_name = ""
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=resolved.parent,
            prefix=f".{resolved.name}.",
            suffix=".tmp",
            delete=False,
        ) as temporary:
            json.dump(value, temporary, indent=2, sort_keys=True)
            temporary.write("\n")
            temporary.flush()
            os.fsync(temporary.fileno())
            temporary_name = temporary.name
        os.replace(temporary_name, resolved)
    finally:
        if temporary_name:
            Path(temporary_name).unlink(missing_ok=True)


def parser() -> argparse.ArgumentParser:
    value = argparse.ArgumentParser(description=__doc__)
    subparsers = value.add_subparsers(dest="action", required=True)
    generate = subparsers.add_parser("generate")
    generate.add_argument("--artifact", action="append", required=True)
    generate.add_argument("--benchmark", action="append", required=True)
    generate.add_argument("--expected-sha", required=True)
    generate.add_argument("--timestamp")
    generate.add_argument("--output", required=True)
    verify = subparsers.add_parser("verify")
    verify.add_argument("--evidence", required=True)
    verify.add_argument("--expected-sha", required=True)
    rollback = subparsers.add_parser("rollback-dry-run")
    rollback.add_argument("--evidence", required=True)
    rollback.add_argument("--expected-sha", required=True)
    return value


def main() -> int:
    args = parser().parse_args()
    try:
        if args.action == "generate":
            result = build_release_evidence(
                ROOT,
                artifacts=[ROOT / item for item in args.artifact],
                benchmarks=[ROOT / item for item in args.benchmark],
                expected_commit=args.expected_sha,
                timestamp=(
                    args.timestamp
                    or datetime.now(timezone.utc).isoformat()
                ),
            )
            _write(Path(args.output), result)
            status = 0
        else:
            evidence = _load(Path(args.evidence))
            if args.action == "verify":
                result = verify_release_evidence(
                    evidence,
                    root=ROOT,
                    expected_commit=args.expected_sha,
                )
                status = (
                    0 if result["verification_status"] == "PASS" else 1
                )
            else:
                result = rollback_dry_run(
                    evidence,
                    root=ROOT,
                    expected_commit=args.expected_sha,
                )
                status = 0 if result["status"] == "PASS" else 1
    except (
        OSError,
        KeyError,
        TypeError,
        json.JSONDecodeError,
        ReleaseEvidenceError,
    ) as exc:
        print(
            json.dumps(
                {"status": "FAIL", "error": str(exc)},
                sort_keys=True,
            ),
            file=sys.stderr,
        )
        return 2
    print(json.dumps(result, indent=2, sort_keys=True))
    return status


if __name__ == "__main__":
    raise SystemExit(main())
