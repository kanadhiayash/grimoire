#!/usr/bin/env python3
"""Verify bounded gold-scenario quality metrics without self-scoring."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from grimoire.benchmarks import load_gold_scenarios, run_gold_scenarios


def _write(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    scenarios = load_gold_scenarios(
        ROOT / "benchmarks" / "scenarios" / "gold" / "scenarios.json"
    )
    report = run_gold_scenarios(scenarios, root=ROOT)
    reasons: list[str] = []
    if report["case_count"] != 16:
        reasons.append("gold_case_count_mismatch")
    if report["compiler_failures"]:
        reasons.append("gold_compiler_failures")
    if report["verifier_failures"]:
        reasons.append("gold_verifier_failures")
    if report["control_set_mismatches"]:
        reasons.append("gold_control_set_mismatches")
    if report["critical_control_recall"] != 1.0:
        reasons.append("critical_control_recall_below_threshold")
    if report["critical_false_non_applicability"]:
        reasons.append("critical_false_non_applicability")
    if report["false_compliance_claims"]:
        reasons.append("false_compliance_claims")
    result = {
        "schema_version": 1,
        "status": "FAIL" if reasons else "PASS",
        "reason_codes": reasons,
        "quality_scope": "bounded_gold_scenario_matrix",
        "unsupported_claims": [
            "overall_product_recall",
            "overall_product_precision",
            "final_legal_counsel_accuracy",
        ],
        "metrics": {
            "case_count": report["case_count"],
            "critical_control_recall": report["critical_control_recall"],
            "critical_false_non_applicability": report[
                "critical_false_non_applicability"
            ],
            "control_set_mismatches": report["control_set_mismatches"],
            "false_compliance_claims": report["false_compliance_claims"],
        },
    }
    _write(Path(args.output), result)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
