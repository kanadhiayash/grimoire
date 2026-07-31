#!/usr/bin/env python3
"""Run, attest, or verify the Grimoire Zeref boundary pilot."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from grimoire.benchmarks.zeref_pilot import (  # noqa: E402
    create_reproduction_attestation,
    run_pilot,
    verify_pilot_reproduction,
)


def _changed_files(commit_before: str, commit_after: str) -> tuple[str, ...]:
    completed = subprocess.run(
        [
            "git",
            "diff",
            "--name-only",
            f"{commit_before}..{commit_after}",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode != 0:
        raise ValueError("unable to determine pilot changed-file set")
    return tuple(
        line
        for line in completed.stdout.splitlines()
        if line.strip()
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="action", required=True)
    run = subparsers.add_parser("run")
    run.add_argument("--output", required=True)
    run.add_argument("--commit-after", required=True)
    run.add_argument("--timestamp")
    attest = subparsers.add_parser("attest")
    attest.add_argument("--primary", required=True)
    attest.add_argument("--reproduction", required=True)
    attest.add_argument("--output", required=True)
    attest.add_argument("--reviewer", required=True)
    attest.add_argument("--producer", required=True)
    attest.add_argument("--timestamp")
    verify = subparsers.add_parser("verify")
    verify.add_argument("--primary", required=True)
    verify.add_argument("--reproduction", required=True)
    verify.add_argument("--attestation", required=True)
    verify.add_argument("--now")
    args = parser.parse_args()
    try:
        if args.action == "run":
            binding = json.loads(
                (
                    ROOT
                    / "benchmarks"
                    / "zeref-pilot"
                    / "plan-binding.json"
                ).read_text(encoding="utf-8")
            )
            result = run_pilot(
                ROOT,
                Path(args.output),
                commit_after=args.commit_after,
                files_changed=_changed_files(
                    binding["project_commit"],
                    args.commit_after,
                ),
                timestamp=(
                    args.timestamp
                    or datetime.now(timezone.utc).isoformat()
                ),
            )
        elif args.action == "attest":
            result = create_reproduction_attestation(
                Path(args.primary),
                Path(args.reproduction),
                reviewer=args.reviewer,
                producer=args.producer,
                timestamp=(
                    args.timestamp
                    or datetime.now(timezone.utc).isoformat()
                ),
            )
            output = Path(args.output)
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text(
                json.dumps(result, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
        else:
            attestation = json.loads(
                Path(args.attestation).read_text(encoding="utf-8")
            )
            result = verify_pilot_reproduction(
                Path(args.primary),
                Path(args.reproduction),
                attestation,
                now=(
                    datetime.fromisoformat(args.now)
                    if args.now
                    else datetime.now(timezone.utc)
                ),
            )
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError):
        print(
            json.dumps(
                {
                    "pilot_status": "FAIL",
                    "reason_codes": ["pilot_input_invalid"],
                },
                indent=2,
            )
        )
        return 2
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result.get("pilot_status") in {"PASS", "PARTIAL"} else 2


if __name__ == "__main__":
    raise SystemExit(main())
