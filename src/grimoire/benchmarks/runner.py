"""Dependency-free benchmark execution, evidence, and comparison."""

from __future__ import annotations

import hashlib
import json
import os
import platform
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Mapping

CASE_ID = re.compile(r"^[a-z0-9][a-z0-9-]{0,79}$")
RESULT_REQUIRED = {
    "schema_version",
    "suite_id",
    "commit",
    "environment",
    "source_manifest",
    "hard_gate_status",
    "verdict",
    "cases",
    "metrics",
}
EVIDENCE_FILES = {
    "BENCHMARK_SUMMARY.md",
    "BENCHMARK_RESULTS.json",
    "RAW_OUTPUT",
    "ENVIRONMENT.json",
    "SOURCE_MANIFEST.json",
    "REGRESSIONS.md",
    "SCORECARD.md",
}


class BenchmarkContractError(ValueError):
    """Raised when benchmark inputs or evidence are incomplete."""


def _canonical_json(value: Any) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _sha256_path(path: Path) -> str:
    return _sha256_bytes(path.read_bytes())


def load_benchmark_suite(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise BenchmarkContractError("invalid_suite_json") from exc
    if not isinstance(value, dict):
        raise BenchmarkContractError("invalid_suite_shape")
    return value


def _validate_suite(suite: Mapping[str, Any], root: Path) -> None:
    if set(suite) != {"schema_version", "suite_id", "sources", "cases"}:
        raise BenchmarkContractError("invalid_suite_shape")
    if suite.get("schema_version") != 1:
        raise BenchmarkContractError("unsupported_suite_version")
    if not isinstance(suite.get("suite_id"), str) or not CASE_ID.fullmatch(
        str(suite["suite_id"])
    ):
        raise BenchmarkContractError("invalid_suite_id")
    sources = suite.get("sources")
    if not isinstance(sources, list) or not sources:
        raise BenchmarkContractError("missing_sources")
    for source in sources:
        if not isinstance(source, str) or not source:
            raise BenchmarkContractError("invalid_source")
        resolved = (root / source).resolve()
        if root.resolve() not in resolved.parents or not resolved.is_file():
            raise BenchmarkContractError("invalid_source")
    cases = suite.get("cases")
    if not isinstance(cases, list) or not cases:
        raise BenchmarkContractError("missing_cases")
    seen: set[str] = set()
    for case in cases:
        if not isinstance(case, dict) or set(case) != {
            "id",
            "command",
            "hard_gate",
        }:
            raise BenchmarkContractError("invalid_case")
        case_id = case.get("id")
        if (
            not isinstance(case_id, str)
            or not CASE_ID.fullmatch(case_id)
            or case_id in seen
        ):
            raise BenchmarkContractError("invalid_case_id")
        seen.add(case_id)
        command = case.get("command")
        if (
            not isinstance(command, list)
            or not command
            or not all(isinstance(item, str) and item for item in command)
        ):
            raise BenchmarkContractError("invalid_command")
        if not isinstance(case.get("hard_gate"), bool):
            raise BenchmarkContractError("invalid_hard_gate")


def _prepare_output(output: Path) -> None:
    current = output
    while True:
        if current.is_symlink():
            raise BenchmarkContractError("unsafe_output")
        if current.exists():
            break
        if current.parent == current:
            break
        current = current.parent
    if output.exists() and any(output.iterdir()):
        raise BenchmarkContractError("output_not_empty")
    output.mkdir(parents=True, exist_ok=True)
    if output.is_symlink():
        raise BenchmarkContractError("unsafe_output")
    (output / "RAW_OUTPUT").mkdir()


def _environment() -> dict[str, str]:
    return {
        "python": platform.python_version(),
        "implementation": platform.python_implementation(),
        "platform": platform.platform(),
        "executable": sys.executable,
    }


def _source_manifest(root: Path, sources: list[str], commit: str) -> dict[str, Any]:
    return {
        "commit": commit,
        "sources": [
            {"path": source, "sha256": _sha256_path(root / source)}
            for source in sorted(sources)
        ],
    }


def run_benchmark_suite(
    suite: Mapping[str, Any],
    *,
    root: Path,
    output: Path,
    commit: str,
) -> dict[str, Any]:
    """Execute a fixed suite and write its complete evidence package."""

    root = root.resolve()
    output = output.expanduser().absolute()
    _validate_suite(suite, root)
    if not re.fullmatch(r"[0-9a-f]{40}", commit):
        raise BenchmarkContractError("invalid_commit")
    _prepare_output(output)
    environment = _environment()
    source_manifest = _source_manifest(root, list(suite["sources"]), commit)
    case_results: list[dict[str, Any]] = []
    for case in suite["cases"]:
        completed = subprocess.run(
            list(case["command"]),
            cwd=root,
            text=False,
            capture_output=True,
            check=False,
            env=dict(os.environ),
        )
        stdout_name = f"{case['id']}.stdout"
        stderr_name = f"{case['id']}.stderr"
        stdout_path = output / "RAW_OUTPUT" / stdout_name
        stderr_path = output / "RAW_OUTPUT" / stderr_name
        stdout_path.write_bytes(completed.stdout)
        stderr_path.write_bytes(completed.stderr)
        case_results.append(
            {
                "id": case["id"],
                "command": list(case["command"]),
                "hard_gate": case["hard_gate"],
                "exit_code": completed.returncode,
                "status": "PASS" if completed.returncode == 0 else "FAIL",
                "stdout": f"RAW_OUTPUT/{stdout_name}",
                "stdout_sha256": _sha256_bytes(completed.stdout),
                "stderr": f"RAW_OUTPUT/{stderr_name}",
                "stderr_sha256": _sha256_bytes(completed.stderr),
            }
        )
    hard_failed = any(
        item["hard_gate"] and item["status"] == "FAIL" for item in case_results
    )
    any_failed = any(item["status"] == "FAIL" for item in case_results)
    verdict = "FAIL" if hard_failed else ("PARTIAL" if any_failed else "PASS")
    result = {
        "schema_version": 1,
        "suite_id": suite["suite_id"],
        "commit": commit,
        "environment": environment,
        "source_manifest": source_manifest,
        "hard_gate_status": "FAIL" if hard_failed else "PASS",
        "verdict": verdict,
        "cases": case_results,
        "metrics": {},
    }
    (output / "ENVIRONMENT.json").write_text(
        _canonical_json(environment), encoding="utf-8"
    )
    (output / "SOURCE_MANIFEST.json").write_text(
        _canonical_json(source_manifest), encoding="utf-8"
    )
    (output / "BENCHMARK_RESULTS.json").write_text(
        _canonical_json(result), encoding="utf-8"
    )
    (output / "BENCHMARK_SUMMARY.md").write_text(
        "# Benchmark Summary\n\n"
        f"- Suite: `{suite['suite_id']}`\n"
        f"- Commit: `{commit}`\n"
        f"- Verdict: `{verdict}`\n"
        f"- Hard gates: `{result['hard_gate_status']}`\n\n"
        "This evidence package does not award an overall product score.\n",
        encoding="utf-8",
    )
    (output / "SCORECARD.md").write_text(
        "# Scorecard\n\n"
        + "\n".join(
            f"- `{item['id']}`: `{item['status']}`"
            + (" (hard gate)" if item["hard_gate"] else "")
            for item in case_results
        )
        + "\n\nNo aggregate score is emitted.\n",
        encoding="utf-8",
    )
    (output / "REGRESSIONS.md").write_text(
        "# Regressions\n\nNo historical comparison was requested for this run.\n",
        encoding="utf-8",
    )
    validate_benchmark_result(result, evidence_root=output)
    return result


def validate_benchmark_result(
    result: Mapping[str, Any],
    *,
    evidence_root: Path,
) -> None:
    if set(result) != RESULT_REQUIRED or result.get("schema_version") != 1:
        raise BenchmarkContractError("invalid_result_shape")
    if not re.fullmatch(r"[0-9a-f]{40}", str(result.get("commit", ""))):
        raise BenchmarkContractError("missing_commit")
    if not isinstance(result.get("environment"), dict) or not result["environment"]:
        raise BenchmarkContractError("missing_environment")
    if (
        not isinstance(result.get("source_manifest"), dict)
        or not result["source_manifest"].get("sources")
    ):
        raise BenchmarkContractError("missing_source_manifest")
    cases = result.get("cases")
    if not isinstance(cases, list) or not cases:
        raise BenchmarkContractError("missing_cases")
    for case in cases:
        for field in ("stdout", "stdout_sha256", "stderr", "stderr_sha256"):
            if field not in case:
                raise BenchmarkContractError("missing_raw_output")
        for path_field, hash_field in (
            ("stdout", "stdout_sha256"),
            ("stderr", "stderr_sha256"),
        ):
            raw_path = (evidence_root / case[path_field]).resolve()
            if evidence_root.resolve() not in raw_path.parents or not raw_path.is_file():
                raise BenchmarkContractError("missing_raw_output")
            if _sha256_path(raw_path) != case[hash_field]:
                raise BenchmarkContractError("raw_output_hash_mismatch")
    if set(path.name for path in evidence_root.iterdir()) != EVIDENCE_FILES:
        raise BenchmarkContractError("incomplete_evidence_package")
    hard_failed = any(
        case.get("hard_gate") is True and case.get("status") == "FAIL"
        for case in cases
    )
    if hard_failed and (
        result.get("hard_gate_status") != "FAIL" or result.get("verdict") != "FAIL"
    ):
        raise BenchmarkContractError("hard_gate_override")
    if "score" in result or "aggregate_score" in result:
        raise BenchmarkContractError("self_awarded_score")


def compare_benchmark_results(
    current: Mapping[str, Any],
    baseline: Mapping[str, Any],
    thresholds: Mapping[str, Any],
) -> list[dict[str, Any]]:
    """Return deterministic regression records for configured numeric metrics."""

    regressions: list[dict[str, Any]] = []
    current_metrics = current.get("metrics", {})
    baseline_metrics = baseline.get("metrics", {})
    if not isinstance(current_metrics, dict) or not isinstance(baseline_metrics, dict):
        raise BenchmarkContractError("invalid_metrics")
    for metric in sorted(thresholds):
        rule = thresholds[metric]
        if (
            not isinstance(rule, dict)
            or set(rule) not in ({"max_increase"}, {"max_decrease"})
            or metric not in current_metrics
            or metric not in baseline_metrics
        ):
            raise BenchmarkContractError("invalid_threshold")
        current_value = current_metrics[metric]
        baseline_value = baseline_metrics[metric]
        if not isinstance(current_value, (int, float)) or not isinstance(
            baseline_value, (int, float)
        ):
            raise BenchmarkContractError("invalid_metric_value")
        if "max_increase" in rule:
            delta = current_value - baseline_value
            threshold = rule["max_increase"]
            direction = "increase"
        else:
            delta = baseline_value - current_value
            threshold = rule["max_decrease"]
            direction = "decrease"
        if not isinstance(threshold, (int, float)) or threshold < 0:
            raise BenchmarkContractError("invalid_threshold")
        if delta > threshold:
            regressions.append(
                {
                    "metric": metric,
                    "baseline": baseline_value,
                    "current": current_value,
                    "delta": delta,
                    "threshold": threshold,
                    "direction": direction,
                }
            )
    return regressions
