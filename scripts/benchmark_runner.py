#!/usr/bin/env python3
"""Run or compare Grimoire benchmark evidence."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from grimoire.benchmarks import (
    BenchmarkContractError,
    compare_benchmark_results,
    load_benchmark_suite,
    run_benchmark_suite,
)


def parser() -> argparse.ArgumentParser:
    value = argparse.ArgumentParser(description=__doc__)
    subparsers = value.add_subparsers(dest="action", required=True)
    run = subparsers.add_parser("run")
    run.add_argument("--suite", required=True)
    run.add_argument("--output", required=True)
    run.add_argument("--commit", required=True)
    compare = subparsers.add_parser("compare")
    compare.add_argument("--current", required=True)
    compare.add_argument("--baseline", required=True)
    compare.add_argument("--thresholds", required=True)
    compare.add_argument("--output", required=True)
    return value


def _load_object(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise BenchmarkContractError("expected_json_object")
    return value


def main() -> int:
    args = parser().parse_args()
    try:
        if args.action == "run":
            result = run_benchmark_suite(
                load_benchmark_suite(Path(args.suite)),
                root=ROOT,
                output=Path(args.output),
                commit=args.commit,
            )
            print(json.dumps(result, indent=2, sort_keys=True))
            return 0 if result["verdict"] != "FAIL" else 1
        regressions = compare_benchmark_results(
            _load_object(Path(args.current)),
            _load_object(Path(args.baseline)),
            _load_object(Path(args.thresholds)),
        )
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(
            json.dumps({"regressions": regressions}, indent=2, sort_keys=True)
            + "\n",
            encoding="utf-8",
        )
        print(output)
        return 1 if regressions else 0
    except (BenchmarkContractError, OSError, json.JSONDecodeError) as exc:
        print(f"FAIL  {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
