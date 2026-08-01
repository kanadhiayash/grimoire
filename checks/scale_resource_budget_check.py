#!/usr/bin/env python3
"""Verify release-target resource budgets from performance evidence."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def _json_object(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("expected_json_object")
    return value


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    report = _json_object(Path(args.input))
    reasons: list[str] = []
    if report.get("target_measured") is not True:
        reasons.append("release_target_not_measured")
    if report.get("memory_gate") != "PASS":
        reasons.append("memory_gate_not_pass")
    if report.get("context_token_gate") != "PASS":
        reasons.append("context_token_gate_not_pass")
    if report.get("verdict") != "PASS":
        reasons.append("scale_verdict_not_pass")
    result = {
        "schema_version": 1,
        "status": "FAIL" if reasons else "PASS",
        "reason_codes": reasons,
        "observed_verdict": report.get("verdict"),
        "memory_gate": report.get("memory_gate"),
        "context_token_gate": report.get("context_token_gate"),
        "target_control_count": report.get("target_control_count"),
    }
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
