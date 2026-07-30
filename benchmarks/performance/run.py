#!/usr/bin/env python3
"""Run deterministic Grimoire synthetic control-scale measurements."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from grimoire.benchmarks import run_scale_benchmark


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sizes", nargs="+", type=int, required=True)
    parser.add_argument("--seed", type=int, default=20260730)
    parser.add_argument("--repeats", type=int, default=7)
    parser.add_argument("--thresholds", default="benchmarks/performance/thresholds.json")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    thresholds = json.loads(
        (ROOT / args.thresholds).read_text(encoding="utf-8")
    )
    report = run_scale_benchmark(
        sizes=tuple(args.sizes),
        seed=args.seed,
        repeats=args.repeats,
        thresholds=thresholds,
        output=Path(args.output),
    )
    print(json.dumps(report, indent=2, sort_keys=True))
    return 1 if report["verdict"] == "FAIL" else 0


if __name__ == "__main__":
    raise SystemExit(main())
