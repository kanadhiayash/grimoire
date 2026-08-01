"""Exact-commit release-candidate benchmark orchestration."""

from __future__ import annotations

import hashlib
import json
import os
import platform
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Sequence

from .runner import BenchmarkContractError

CASE_ID = re.compile(r"^[a-z0-9][a-z0-9-]{0,79}$")
REASON_CODE = re.compile(r"^[a-z0-9][a-z0-9_-]{0,79}$")
COMMIT = re.compile(r"^[0-9a-f]{40}$")
STATUSES = {"PASS", "PARTIAL", "FAIL", "NOT_VERIFIED"}
PACKAGE_FILES = {
    "ENVIRONMENT.json",
    "RAW_OUTPUT",
    "RELEASE_CANDIDATE_RESULTS.json",
    "SCORECARD.md",
    "SOURCE_MANIFEST.json",
}
RESULT_FIELDS = {
    "schema_version",
    "suite_id",
    "run_id",
    "commit",
    "environment",
    "source_manifest",
    "raw_artifact_manifest",
    "gates",
    "hard_gate_status",
    "verdict",
    "overall_score",
    "score_reason",
}


def _canonical_json(value: Any) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _sha256_path(path: Path) -> str:
    return _sha256_bytes(path.read_bytes())


def _run_git(root: Path, *arguments: str) -> str:
    completed = subprocess.run(
        ["git", *arguments],
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode != 0:
        raise BenchmarkContractError("git_state_unavailable")
    return completed.stdout.strip()


def _verify_repository(root: Path, expected_commit: str) -> None:
    if not COMMIT.fullmatch(expected_commit):
        raise BenchmarkContractError("invalid_commit")
    if _run_git(root, "rev-parse", "HEAD") != expected_commit:
        raise BenchmarkContractError("commit_mismatch")
    if _run_git(root, "status", "--porcelain", "--untracked-files=all"):
        raise BenchmarkContractError("dirty_repository")


def _prepare_output(output: Path) -> None:
    current = output
    while True:
        if current.is_symlink():
            raise BenchmarkContractError("unsafe_output")
        if current.exists() or current.parent == current:
            break
        current = current.parent
    if output.exists() and (not output.is_dir() or any(output.iterdir())):
        raise BenchmarkContractError("output_not_empty")
    output.mkdir(parents=True, exist_ok=True)
    if output.is_symlink():
        raise BenchmarkContractError("unsafe_output")
    (output / "RAW_OUTPUT").mkdir()


def _validate_suite(suite: Mapping[str, Any], root: Path) -> None:
    if set(suite) != {"schema_version", "suite_id", "sources", "gates"}:
        raise BenchmarkContractError("invalid_release_candidate_suite")
    if suite.get("schema_version") != 1:
        raise BenchmarkContractError("unsupported_release_candidate_suite")
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
    gates = suite.get("gates")
    if not isinstance(gates, list) or not gates:
        raise BenchmarkContractError("missing_gates")
    seen: set[str] = set()
    for gate in gates:
        if not isinstance(gate, dict):
            raise BenchmarkContractError("invalid_gate")
        gate_id = gate.get("id")
        if (
            not isinstance(gate_id, str)
            or not CASE_ID.fullmatch(gate_id)
            or gate_id in seen
        ):
            raise BenchmarkContractError("invalid_gate_id")
        seen.add(gate_id)
        if not isinstance(gate.get("category"), str) or not gate["category"]:
            raise BenchmarkContractError("invalid_gate_category")
        if not isinstance(gate.get("hard_gate"), bool):
            raise BenchmarkContractError("invalid_hard_gate")
        if "command" in gate:
            if set(gate) != {
                "id",
                "category",
                "command",
                "hard_gate",
            }:
                raise BenchmarkContractError("invalid_executable_gate")
            command = gate["command"]
            if (
                not isinstance(command, list)
                or not command
                or not all(isinstance(item, str) and item for item in command)
            ):
                raise BenchmarkContractError("invalid_command")
        else:
            if set(gate) != {
                "id",
                "category",
                "declared_status",
                "reason_codes",
                "hard_gate",
            }:
                raise BenchmarkContractError("invalid_declared_gate")
            if gate.get("declared_status") != "NOT_VERIFIED":
                raise BenchmarkContractError("unsafe_declared_status")
            if (
                not isinstance(gate.get("reason_codes"), list)
                or not gate["reason_codes"]
                or not all(
                    isinstance(item, str) and REASON_CODE.fullmatch(item)
                    for item in gate["reason_codes"]
                )
            ):
                raise BenchmarkContractError("invalid_reason_codes")


def load_release_candidate_suite(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise BenchmarkContractError("invalid_release_candidate_suite") from exc
    if not isinstance(value, dict):
        raise BenchmarkContractError("invalid_release_candidate_suite")
    return value


def _environment(expected_commit: str, run_id: str) -> dict[str, Any]:
    return {
        "commit": expected_commit,
        "implementation": platform.python_implementation(),
        "platform": platform.platform(),
        "python": platform.python_version(),
        "run_id": run_id,
        "repository_clean_before_run": True,
        "repository_clean_after_run": True,
    }


def _source_manifest(
    root: Path,
    sources: Sequence[str],
    expected_commit: str,
) -> dict[str, Any]:
    return {
        "commit": expected_commit,
        "sources": [
            {"path": source, "sha256": _sha256_path(root / source)}
            for source in sorted(sources)
        ],
        "tree": _run_git(root, "rev-parse", f"{expected_commit}^{{tree}}"),
    }


def _raw_artifact_manifest(output: Path) -> list[dict[str, str]]:
    raw_root = output / "RAW_OUTPUT"
    artifacts: list[dict[str, str]] = []
    for path in sorted(raw_root.rglob("*")):
        if path.is_symlink():
            raise BenchmarkContractError("unsafe_raw_artifact")
        if path.is_dir():
            continue
        if not path.is_file():
            raise BenchmarkContractError("unsafe_raw_artifact")
        artifacts.append(
            {
                "path": path.relative_to(output).as_posix(),
                "sha256": _sha256_path(path),
            }
        )
    if not artifacts:
        raise BenchmarkContractError("missing_raw_output")
    return artifacts


def _expand_command(
    command: Sequence[str],
    *,
    output: Path,
    expected_commit: str,
) -> list[str]:
    replacements = {
        "{python}": sys.executable,
        "{run_output}": str(output),
        "{commit}": expected_commit,
    }
    expanded: list[str] = []
    for item in command:
        value = item
        for marker, replacement in replacements.items():
            value = value.replace(marker, replacement)
        if "{" in value or "}" in value:
            raise BenchmarkContractError("unknown_command_placeholder")
        expanded.append(value)
    return expanded


def _aggregate(gates: Sequence[Mapping[str, Any]]) -> tuple[str, str]:
    hard_statuses = {
        gate["status"] for gate in gates if gate.get("hard_gate") is True
    }
    if "FAIL" in hard_statuses:
        return "FAIL", "FAIL"
    if "NOT_VERIFIED" in hard_statuses:
        return "NOT_VERIFIED", "NOT_VERIFIED"
    if "PARTIAL" in hard_statuses:
        return "PARTIAL", "PARTIAL"
    if any(gate["status"] == "FAIL" for gate in gates):
        return "PASS", "PARTIAL"
    if any(gate["status"] == "NOT_VERIFIED" for gate in gates):
        return "PASS", "NOT_VERIFIED"
    if any(gate["status"] == "PARTIAL" for gate in gates):
        return "PASS", "PARTIAL"
    return "PASS", "PASS"


def run_release_candidate(
    suite: Mapping[str, Any],
    *,
    root: Path,
    output: Path,
    expected_commit: str,
    run_id: str,
) -> dict[str, Any]:
    """Run one clean exact-commit release-candidate evidence package."""

    root = root.resolve()
    output = output.expanduser().absolute()
    if not CASE_ID.fullmatch(run_id):
        raise BenchmarkContractError("invalid_run_id")
    _validate_suite(suite, root)
    _verify_repository(root, expected_commit)
    _prepare_output(output)
    environment = _environment(expected_commit, run_id)
    source_manifest = _source_manifest(
        root, list(suite["sources"]), expected_commit
    )
    gate_results: list[dict[str, Any]] = []
    for gate in suite["gates"]:
        if "command" not in gate:
            gate_results.append(
                {
                    "id": gate["id"],
                    "category": gate["category"],
                    "hard_gate": gate["hard_gate"],
                    "status": "NOT_VERIFIED",
                    "reason_codes": list(gate["reason_codes"]),
                }
            )
            continue
        command = _expand_command(
            gate["command"],
            output=output,
            expected_commit=expected_commit,
        )
        started_at = datetime.now(timezone.utc).isoformat()
        completed = subprocess.run(
            command,
            cwd=root,
            text=False,
            capture_output=True,
            check=False,
            env=dict(os.environ),
        )
        finished_at = datetime.now(timezone.utc).isoformat()
        stdout_path = output / "RAW_OUTPUT" / f"{gate['id']}.stdout"
        stderr_path = output / "RAW_OUTPUT" / f"{gate['id']}.stderr"
        stdout_path.write_bytes(completed.stdout)
        stderr_path.write_bytes(completed.stderr)
        gate_results.append(
            {
                "id": gate["id"],
                "category": gate["category"],
                "command": command,
                "hard_gate": gate["hard_gate"],
                "started_at": started_at,
                "finished_at": finished_at,
                "exit_code": completed.returncode,
                "status": "PASS" if completed.returncode == 0 else "FAIL",
                "reason_codes": (
                    [] if completed.returncode == 0 else ["command_failed"]
                ),
                "stdout": f"RAW_OUTPUT/{gate['id']}.stdout",
                "stdout_sha256": _sha256_bytes(completed.stdout),
                "stderr": f"RAW_OUTPUT/{gate['id']}.stderr",
                "stderr_sha256": _sha256_bytes(completed.stderr),
            }
        )
    _verify_repository(root, expected_commit)
    hard_gate_status, verdict = _aggregate(gate_results)
    raw_artifact_manifest = _raw_artifact_manifest(output)
    result = {
        "schema_version": 1,
        "suite_id": suite["suite_id"],
        "run_id": run_id,
        "commit": expected_commit,
        "environment": environment,
        "source_manifest": source_manifest,
        "raw_artifact_manifest": raw_artifact_manifest,
        "gates": gate_results,
        "hard_gate_status": hard_gate_status,
        "verdict": verdict,
        "overall_score": None,
        "score_reason": "No aggregate product score is self-awarded.",
    }
    (output / "ENVIRONMENT.json").write_text(
        _canonical_json(environment), encoding="utf-8"
    )
    (output / "SOURCE_MANIFEST.json").write_text(
        _canonical_json(source_manifest), encoding="utf-8"
    )
    (output / "RELEASE_CANDIDATE_RESULTS.json").write_text(
        _canonical_json(result), encoding="utf-8"
    )
    (output / "SCORECARD.md").write_text(
        "# Release-Candidate Scorecard\n\n"
        f"- Run: `{run_id}`\n"
        f"- Commit: `{expected_commit}`\n"
        f"- Verdict: `{verdict}`\n"
        f"- Hard gates: `{hard_gate_status}`\n\n"
        + "\n".join(
            f"- `{gate['category']}/{gate['id']}`: `{gate['status']}`"
            for gate in gate_results
        )
        + "\n\nNo aggregate product score is awarded by this runner.\n",
        encoding="utf-8",
    )
    validate_release_candidate_run(
        result,
        evidence_root=output,
        expected_commit=expected_commit,
    )
    return result


def validate_release_candidate_run(
    result: Mapping[str, Any],
    *,
    evidence_root: Path,
    expected_commit: str,
) -> None:
    """Validate one release-candidate package without trusting its verdict."""

    evidence_root = evidence_root.resolve()
    if set(result) != RESULT_FIELDS or result.get("schema_version") != 1:
        raise BenchmarkContractError("invalid_release_candidate_result")
    if result.get("commit") != expected_commit:
        raise BenchmarkContractError("commit_mismatch")
    if result.get("overall_score") is not None:
        raise BenchmarkContractError("self_awarded_score")
    environment_path = evidence_root / "ENVIRONMENT.json"
    if not environment_path.is_file() or not result.get("environment"):
        raise BenchmarkContractError("missing_environment")
    try:
        environment = json.loads(environment_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise BenchmarkContractError("missing_environment") from exc
    if (
        environment != result["environment"]
        or environment.get("commit") != expected_commit
        or environment.get("repository_clean_before_run") is not True
        or environment.get("repository_clean_after_run") is not True
    ):
        raise BenchmarkContractError("invalid_environment")
    source_path = evidence_root / "SOURCE_MANIFEST.json"
    if not source_path.is_file() or not result.get("source_manifest"):
        raise BenchmarkContractError("missing_source_manifest")
    try:
        source_manifest = json.loads(source_path.read_text(encoding="utf-8"))
        recorded_result = json.loads(
            (evidence_root / "RELEASE_CANDIDATE_RESULTS.json").read_text(
                encoding="utf-8"
            )
        )
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise BenchmarkContractError("incomplete_evidence_package") from exc
    if (
        source_manifest != result["source_manifest"]
        or source_manifest.get("commit") != expected_commit
    ):
        raise BenchmarkContractError("source_manifest_mismatch")
    if recorded_result != result:
        raise BenchmarkContractError("result_file_mismatch")
    if set(path.name for path in evidence_root.iterdir()) != PACKAGE_FILES:
        raise BenchmarkContractError("incomplete_evidence_package")
    gates = result.get("gates")
    if not isinstance(gates, list) or not gates:
        raise BenchmarkContractError("missing_gates")
    for gate in gates:
        if gate.get("status") not in STATUSES:
            raise BenchmarkContractError("invalid_gate_status")
        if "command" not in gate:
            if gate.get("status") != "NOT_VERIFIED":
                raise BenchmarkContractError("unsafe_declared_status")
            continue
        expected_status = "PASS" if gate.get("exit_code") == 0 else "FAIL"
        if gate.get("status") != expected_status:
            raise BenchmarkContractError("invalid_gate_status")
        for path_field, hash_field in (
            ("stdout", "stdout_sha256"),
            ("stderr", "stderr_sha256"),
        ):
            if path_field not in gate or hash_field not in gate:
                raise BenchmarkContractError("missing_raw_output")
            raw_path = (evidence_root / gate[path_field]).resolve()
            if (
                evidence_root not in raw_path.parents
                or not raw_path.is_file()
                or _sha256_path(raw_path) != gate[hash_field]
            ):
                raise BenchmarkContractError("missing_raw_output")
    if result.get("raw_artifact_manifest") != _raw_artifact_manifest(
        evidence_root
    ):
        raise BenchmarkContractError("raw_artifact_manifest_mismatch")
    hard_gate_status, verdict = _aggregate(gates)
    if (
        result.get("hard_gate_status") != hard_gate_status
        or result.get("verdict") != verdict
    ):
        raise BenchmarkContractError("invalid_aggregate_status")


def compare_release_candidate_runs(
    evidence_roots: Sequence[Path],
    *,
    expected_commit: str,
) -> dict[str, Any]:
    """Compare exactly three clean runs without inventing an overall score."""

    if len(evidence_roots) != 3:
        raise BenchmarkContractError("expected_three_runs")
    results: list[dict[str, Any]] = []
    for root in evidence_roots:
        try:
            result = json.loads(
                (root / "RELEASE_CANDIDATE_RESULTS.json").read_text(
                    encoding="utf-8"
                )
            )
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            raise BenchmarkContractError("missing_run_result") from exc
        if not isinstance(result, dict):
            raise BenchmarkContractError("missing_run_result")
        validate_release_candidate_run(
            result,
            evidence_root=root,
            expected_commit=expected_commit,
        )
        results.append(result)
    run_ids = [str(result["run_id"]) for result in results]
    if len(set(run_ids)) != 3:
        raise BenchmarkContractError("duplicate_run_id")
    if any(
        result["source_manifest"] != results[0]["source_manifest"]
        for result in results[1:]
    ):
        raise BenchmarkContractError("source_manifest_mismatch")
    expected_gate_ids = [gate["id"] for gate in results[0]["gates"]]
    status_variance = 0
    gate_comparison: list[dict[str, Any]] = []
    for index, gate_id in enumerate(expected_gate_ids):
        statuses: list[str] = []
        for result in results:
            gate_ids = [gate["id"] for gate in result["gates"]]
            if gate_ids != expected_gate_ids:
                raise BenchmarkContractError("gate_set_mismatch")
            statuses.append(result["gates"][index]["status"])
        distinct = sorted(set(statuses))
        if len(distinct) > 1:
            status_variance += 1
        gate_comparison.append(
            {
                "id": gate_id,
                "statuses": statuses,
                "status_variance": len(distinct) - 1,
            }
        )
    verdicts = [str(result["verdict"]) for result in results]
    if "FAIL" in verdicts:
        verdict = "FAIL"
    elif status_variance:
        verdict = "FAIL"
    elif "NOT_VERIFIED" in verdicts:
        verdict = "NOT_VERIFIED"
    elif "PARTIAL" in verdicts:
        verdict = "PARTIAL"
    else:
        verdict = "PASS"
    return {
        "schema_version": 1,
        "commit": expected_commit,
        "run_count": 3,
        "run_ids": run_ids,
        "gate_comparison": gate_comparison,
        "status_variance": status_variance,
        "approved_status_variance": 0,
        "verdict": verdict,
        "overall_score": None,
        "score_reason": "No aggregate product score is self-awarded.",
    }
