#!/usr/bin/env python3
"""Write exact-commit CI environment evidence using only the standard library."""

from __future__ import annotations

import argparse
import json
import os
import platform
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _git_head() -> str:
    completed = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode != 0:
        raise ValueError("unable to resolve checked-out commit")
    return completed.stdout.strip()


def _path_is_within(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
    except ValueError:
        return False
    return True


def _reject_symlink_components(path: Path) -> None:
    if ".." in path.parts:
        raise ValueError("environment evidence path contains parent traversal")
    absolute = Path(os.path.abspath(path))
    trusted_candidates = (
        Path(os.path.abspath(ROOT)),
        Path(os.path.abspath(tempfile.gettempdir())),
    )
    roots = [
        candidate
        for candidate in trusted_candidates
        if _path_is_within(absolute, candidate)
    ]
    boundary = (
        max(roots, key=lambda candidate: len(candidate.parts))
        if roots
        else Path(absolute.anchor)
    )
    candidate = boundary
    for part in absolute.relative_to(boundary).parts:
        candidate /= part
        if candidate.is_symlink():
            raise ValueError("environment evidence path contains a symlink")


def write_environment(output: Path, expected_sha: str) -> dict[str, object]:
    commit = _git_head()
    if not expected_sha or commit != expected_sha:
        raise ValueError("checked-out commit does not match expected commit")
    _reject_symlink_components(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    evidence: dict[str, object] = {
        "schema_version": 1,
        "commit": commit,
        "commit_exact": True,
        "python_version": platform.python_version(),
        "python_implementation": platform.python_implementation(),
        "os": platform.system(),
        "platform": platform.platform(),
        "architecture": platform.machine(),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "github": {
            "workflow": os.environ.get("GITHUB_WORKFLOW", "NOT_AVAILABLE"),
            "run_id": os.environ.get("GITHUB_RUN_ID", "NOT_AVAILABLE"),
            "job": os.environ.get("GITHUB_JOB", "NOT_AVAILABLE"),
            "runner_os": os.environ.get("RUNNER_OS", "NOT_AVAILABLE"),
            "runner_arch": os.environ.get("RUNNER_ARCH", "NOT_AVAILABLE"),
        },
    }
    encoded = json.dumps(evidence, indent=2, sort_keys=True) + "\n"
    temporary_name = ""
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=output.parent,
            prefix=f".{output.name}.",
            suffix=".tmp",
            delete=False,
        ) as temporary:
            temporary.write(encoded)
            temporary.flush()
            os.fsync(temporary.fileno())
            temporary_name = temporary.name
        os.replace(temporary_name, output)
    finally:
        if temporary_name:
            Path(temporary_name).unlink(missing_ok=True)
    return evidence


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True)
    parser.add_argument("--expected-sha", required=True)
    args = parser.parse_args()
    try:
        evidence = write_environment(
            Path(args.output),
            args.expected_sha,
        )
    except (OSError, ValueError) as exc:
        print(
            json.dumps(
                {
                    "status": "FAIL",
                    "error": type(exc).__name__,
                },
                sort_keys=True,
            ),
            file=sys.stderr,
        )
        return 2
    print(json.dumps(evidence, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
