#!/usr/bin/env python3
"""Execute the public, non-mutating Grimoire command smoke."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]


def _sha256(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _run(command_id: str, argv: list[str]) -> dict[str, Any]:
    completed = subprocess.run(
        argv,
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    return {
        "id": command_id,
        "argv": argv,
        "exit_code": completed.returncode,
        "status": "PASS" if completed.returncode == 0 else "FAIL",
        "stdout_sha256": _sha256(completed.stdout),
        "stderr_sha256": _sha256(completed.stderr),
    }


def execute() -> dict[str, Any]:
    commands: list[dict[str, Any]] = []
    with tempfile.TemporaryDirectory(prefix="grimoire-doc-smoke-") as directory:
        workspace = Path(directory)
        pack = workspace / "project-pack"
        benchmark = workspace / "benchmark"
        commit = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        ).stdout.strip()
        commands.extend(
            [
                _run(
                    "status",
                    [sys.executable, "scripts/grimoire.py", "status", "--json"],
                ),
                _run(
                    "catalog",
                    [sys.executable, "scripts/grimoire.py", "catalog", "--json"],
                ),
                _run(
                    "doctor",
                    [sys.executable, "scripts/grimoire.py", "doctor"],
                ),
                _run(
                    "project-boot",
                    [
                        sys.executable,
                        "scripts/grimoire.py",
                        "project",
                        "boot",
                        "--manifest",
                        "templates/project/project.json",
                        "--output",
                        str(pack),
                        "--deterministic",
                        "--generated-at",
                        "2026-01-01T00:00:00+00:00",
                    ],
                ),
                _run(
                    "project-verify",
                    [
                        sys.executable,
                        "scripts/grimoire.py",
                        "project",
                        "verify",
                        "--directory",
                        str(pack),
                        "--mode",
                        "offline",
                    ],
                ),
            ]
        )
        trace_path = pack / "CONTROL_TRACE.json"
        if trace_path.is_file():
            trace = json.loads(trace_path.read_text(encoding="utf-8"))
            first_standard = trace["controls"][0]["standard_id"]
            commands.append(
                _run(
                    "project-explain",
                    [
                        sys.executable,
                        "scripts/grimoire.py",
                        "project",
                        "explain",
                        "--directory",
                        str(pack),
                        "--standard-id",
                        first_standard,
                        "--json",
                    ],
                )
            )
        else:
            commands.append(
                {
                    "id": "project-explain",
                    "argv": [],
                    "exit_code": 2,
                    "status": "FAIL",
                    "stdout_sha256": _sha256(""),
                    "stderr_sha256": _sha256("project pack missing"),
                }
            )
        commands.append(
            _run(
                "benchmark-run",
                [
                    sys.executable,
                    "scripts/grimoire.py",
                    "benchmark",
                    "run",
                    "--suite",
                    "benchmarks/suites/runner-smoke.json",
                    "--output",
                    str(benchmark),
                    "--commit",
                    commit,
                ],
            )
        )
    return {
        "schema_version": 1,
        "status": (
            "PASS"
            if all(item["status"] == "PASS" for item in commands)
            else "FAIL"
        ),
        "commands": commands,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = execute()
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        for command in result["commands"]:
            print(f"{command['status']:5} {command['id']}")
        print(f"\nDocumented command smoke: {result['status']}")
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
