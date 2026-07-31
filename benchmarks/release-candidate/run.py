#!/usr/bin/env python3
"""Run or compare exact-commit Grimoire release-candidate evidence."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from grimoire.benchmarks import (  # noqa: E402
    BenchmarkContractError,
    compare_release_candidate_runs,
    load_release_candidate_suite,
    run_release_candidate,
)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="action", required=True)
    run = subparsers.add_parser("run")
    run.add_argument("--suite", required=True)
    run.add_argument("--output", required=True)
    run.add_argument("--expected-commit", required=True)
    run.add_argument("--run-id", required=True)
    compare = subparsers.add_parser("compare")
    compare.add_argument("--run", action="append", required=True)
    compare.add_argument("--expected-commit", required=True)
    compare.add_argument("--output", required=True)
    return parser


def main() -> int:
    args = _parser().parse_args()
    try:
        if args.action == "run":
            result = run_release_candidate(
                load_release_candidate_suite(ROOT / args.suite),
                root=ROOT,
                output=Path(args.output),
                expected_commit=args.expected_commit,
                run_id=args.run_id,
            )
        else:
            result = compare_release_candidate_runs(
                [Path(path) for path in args.run],
                expected_commit=args.expected_commit,
            )
            output = Path(args.output)
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text(
                json.dumps(result, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
        print(json.dumps(result, indent=2, sort_keys=True))
        return 1 if result["verdict"] == "FAIL" else 0
    except (BenchmarkContractError, OSError, json.JSONDecodeError) as exc:
        print(
            json.dumps(
                {
                    "status": "FAIL",
                    "error_code": str(exc),
                },
                indent=2,
                sort_keys=True,
            ),
            file=sys.stderr,
        )
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
