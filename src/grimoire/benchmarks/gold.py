"""Gold product-scenario compiler and verifier benchmark."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

from grimoire.benchmarks.runner import BenchmarkContractError
from grimoire.registry import load_standard_registry

EXPECTED_FIELDS = {
    "control_state_sha256",
    "selected_count",
    "excluded_count",
    "uncertain_count",
    "conflicted_count",
    "required_documents",
    "required_evidence_sha256",
    "required_evidence_count",
    "counsel_questions",
    "expected_status",
    "critical_controls",
}


def _canonical_hash(value: Any) -> str:
    encoded = json.dumps(
        value, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def load_gold_scenarios(path: Path) -> list[dict[str, Any]]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise BenchmarkContractError("invalid_gold_fixture") from exc
    if (
        not isinstance(value, dict)
        or set(value) != {"schema_version", "expectation_profiles", "scenarios"}
        or value.get("schema_version") != 1
        or not isinstance(value.get("expectation_profiles"), dict)
        or not isinstance(value.get("scenarios"), list)
    ):
        raise BenchmarkContractError("invalid_gold_fixture")
    profiles = value["expectation_profiles"]
    scenarios: list[dict[str, Any]] = []
    seen: set[str] = set()
    for raw_scenario in value["scenarios"]:
        if (
            not isinstance(raw_scenario, dict)
            or set(raw_scenario)
            != {
                "id",
                "manifest",
                "expected_profile",
                "counsel_questions",
                "critical_controls",
            }
            or not isinstance(raw_scenario.get("id"), str)
            or raw_scenario["id"] in seen
            or not isinstance(raw_scenario.get("manifest"), dict)
            or raw_scenario.get("expected_profile") not in profiles
            or not isinstance(raw_scenario.get("counsel_questions"), list)
            or not isinstance(raw_scenario.get("critical_controls"), list)
        ):
            raise BenchmarkContractError("invalid_gold_scenario")
        profile = profiles[raw_scenario["expected_profile"]]
        if not isinstance(profile, dict):
            raise BenchmarkContractError("invalid_gold_profile")
        expected = {
            **profile,
            "counsel_questions": raw_scenario["counsel_questions"],
            "critical_controls": raw_scenario["critical_controls"],
        }
        if set(expected) != EXPECTED_FIELDS:
            raise BenchmarkContractError("invalid_gold_profile")
        scenario = {
            "id": raw_scenario["id"],
            "manifest": raw_scenario["manifest"],
            "expected": expected,
        }
        scenarios.append(scenario)
        seen.add(scenario["id"])
    return scenarios


def _run_one(
    scenario: dict[str, Any],
    *,
    root: Path,
    registry: dict[str, Any],
) -> dict[str, Any]:
    with tempfile.TemporaryDirectory() as directory:
        working = Path(directory)
        manifest = working / "manifest.json"
        output = working / "pack"
        manifest.write_text(
            json.dumps(scenario["manifest"], indent=2) + "\n",
            encoding="utf-8",
        )
        compile_result = subprocess.run(
            [
                sys.executable,
                "scripts/project_orchestrator.py",
                "--manifest",
                str(manifest),
                "--output",
                str(output),
                "--deterministic",
            ],
            cwd=root,
            capture_output=True,
            text=True,
            check=False,
        )
        if compile_result.returncode != 0:
            return {
                "id": scenario["id"],
                "compiler_status": "FAIL",
                "verifier_status": "NOT_RUN",
                "stderr_sha256": hashlib.sha256(
                    compile_result.stderr.encode("utf-8")
                ).hexdigest(),
            }
        verify_result = subprocess.run(
            [
                sys.executable,
                "scripts/verify_project_pack.py",
                "--directory",
                str(output),
                "--mode",
                "offline",
            ],
            cwd=root,
            capture_output=True,
            text=True,
            check=False,
        )
        trace = json.loads((output / "CONTROL_TRACE.json").read_text("utf-8"))
        pack = json.loads((output / "CONTROL_PACK.json").read_text("utf-8"))
        status = json.loads((output / "PROJECT_STATUS.json").read_text("utf-8"))
        states = {
            item["standard_id"]: item["state"]
            for item in trace["controls"]
        }
        counts = {
            state.lower(): sum(1 for value in states.values() if value == state)
            for state in ("SELECTED", "EXCLUDED", "UNCERTAIN", "CONFLICTED")
        }
        selected = {
            control_id
            for control_id, state_value in states.items()
            if state_value == "SELECTED"
        }
        evidence = sorted(
            {
                item
                for control_id in selected
                for item in registry[control_id].contract.get("evidence", [])
            }
        )
        expected = scenario["expected"]
        actual = {
            "control_state_sha256": _canonical_hash(states),
            "selected_count": counts["selected"],
            "excluded_count": counts["excluded"],
            "uncertain_count": counts["uncertain"],
            "conflicted_count": counts["conflicted"],
            "required_documents": pack["required_documents"],
            "required_evidence_sha256": _canonical_hash(evidence),
            "required_evidence_count": len(evidence),
            "expected_status": status["status"],
        }
        return {
            "id": scenario["id"],
            "compiler_status": "PASS",
            "verifier_status": (
                "PASS" if verify_result.returncode == 0 else "FAIL"
            ),
            "control_set_match": all(
                actual[field] == expected[field]
                for field in (
                    "control_state_sha256",
                    "selected_count",
                    "excluded_count",
                    "uncertain_count",
                    "conflicted_count",
                    "required_documents",
                    "required_evidence_sha256",
                    "required_evidence_count",
                    "expected_status",
                )
            ),
            "critical_selected": sorted(
                set(expected["critical_controls"]).intersection(selected)
            ),
            "critical_expected": sorted(expected["critical_controls"]),
            "false_compliance_claim": (
                status["status"] == "COMPLIANT"
                or "COMPLIANT" in json.dumps(status["status_report"])
            ),
            "actual": actual,
        }


def run_gold_scenarios(
    scenarios: list[dict[str, Any]],
    *,
    root: Path,
) -> dict[str, Any]:
    registry = dict(
        load_standard_registry(
            root / "registry" / "standards",
            root=root,
        )
    )
    cases = [
        _run_one(scenario, root=root, registry=registry)
        for scenario in scenarios
    ]
    expected_critical = sum(
        len(case.get("critical_expected", [])) for case in cases
    )
    selected_critical = sum(
        len(case.get("critical_selected", [])) for case in cases
    )
    return {
        "schema_version": 1,
        "case_count": len(cases),
        "compiler_failures": sum(
            case["compiler_status"] != "PASS" for case in cases
        ),
        "verifier_failures": sum(
            case["verifier_status"] != "PASS" for case in cases
        ),
        "control_set_mismatches": sum(
            case.get("control_set_match") is not True for case in cases
        ),
        "critical_control_recall": (
            selected_critical / expected_critical if expected_critical else 0.0
        ),
        "critical_false_non_applicability": (
            expected_critical - selected_critical
        ),
        "false_compliance_claims": sum(
            case.get("false_compliance_claim") is True for case in cases
        ),
        "overall_recall": "NOT_VERIFIED",
        "overall_precision": "NOT_VERIFIED",
        "counsel_routing": "NOT_VERIFIED",
        "cases": cases,
    }
