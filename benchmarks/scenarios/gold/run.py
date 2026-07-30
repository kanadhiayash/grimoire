#!/usr/bin/env python3
"""Run the immutable Grimoire gold product-scenario matrix."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from grimoire.benchmarks import load_gold_scenarios, run_gold_scenarios


def main() -> int:
    scenarios = load_gold_scenarios(Path(__file__).with_name("scenarios.json"))
    report = run_gold_scenarios(scenarios, root=ROOT)
    print(json.dumps(report, indent=2, sort_keys=True))
    hard_failures = (
        report["compiler_failures"]
        + report["verifier_failures"]
        + report["control_set_mismatches"]
        + report["critical_false_non_applicability"]
        + report["false_compliance_claims"]
    )
    return 1 if hard_failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
