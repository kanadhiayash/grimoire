#!/usr/bin/env python3
"""Run the inert local Grimoire trust-boundary suite."""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from grimoire.benchmarks import run_trust_boundary_suite


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output")
    args = parser.parse_args()
    if args.output:
        report = run_trust_boundary_suite(
            root=ROOT,
            artifact_root=Path(args.output),
        )
    else:
        with tempfile.TemporaryDirectory() as directory:
            report = run_trust_boundary_suite(
                root=ROOT,
                artifact_root=Path(directory) / "evidence",
            )
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["verdict"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
