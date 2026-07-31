"""Reproducible Grimoire-to-Zeref boundary pilot."""

from __future__ import annotations

import hashlib
import json
import platform
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Sequence

from grimoire.filesystem import atomic_write_directory
from grimoire.zeref import (
    receipt_integrity_hash,
    verify_zeref_receipt,
    zeref_profile_hash,
)

PACK_FILES = (
    "AI_CONTEXT.md",
    "CONTROL_PACK.json",
    "PROJECT_STATUS.json",
    "EXPECTED_OUTCOMES.md",
    "REQUIRED_DOCUMENTS.md",
    "DOCUMENT_SCHEMAS.json",
    "REQUIRED_GATES.md",
    "ACCEPTANCE_MATRIX.md",
    "VERIFICATION_PLAN.md",
    "SOURCE_MANIFEST.json",
    "ZEREF_EXECUTION_PROFILE.json",
    "CONTROL_TRACE.json",
    "CONFLICT_REPORT.json",
    "EXCLUSIONS.json",
    "EXECUTION_RECEIPT.json",
)
PILOT_FILES = (
    *(f"PACK/{name}" for name in PACK_FILES),
    "EXECUTION_RECEIPT.v1.json",
    "RECEIPT_VERIFICATION.json",
    "PILOT_RESULT.json",
    "RAW_OUTPUT/focused-tests.stdout.txt",
    "RAW_OUTPUT/focused-tests.stderr.txt",
    "ENVIRONMENT.json",
    "ROLLBACK.md",
    "PILOT_SOURCE_MANIFEST.json",
)


def _json(value: Any) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(_json(value), encoding="utf-8")


def _load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("pilot JSON input must contain an object")
    return value


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical_hash(value: Any) -> str:
    return hashlib.sha256(
        (
            json.dumps(value, sort_keys=True, separators=(",", ":"))
            + "\n"
        ).encode("utf-8")
    ).hexdigest()


def _manifest_hash(directory: Path) -> str:
    manifest = _load_json(directory / "PILOT_SOURCE_MANIFEST.json")
    return _canonical_hash(manifest["files"])


def _verify_file_manifest(directory: Path) -> list[str]:
    reasons: list[str] = []
    try:
        manifest = _load_json(directory / "PILOT_SOURCE_MANIFEST.json")
        recorded = manifest["files"]
        if not isinstance(recorded, dict):
            return ["invalid_pilot_source_manifest"]
        actual = {
            str(path.relative_to(directory)): _sha256(path)
            for path in directory.rglob("*")
            if path.is_file()
            and path.name != "PILOT_SOURCE_MANIFEST.json"
        }
        if recorded != actual:
            reasons.append("pilot_artifact_hash_mismatch")
    except (OSError, ValueError, KeyError, json.JSONDecodeError):
        reasons.append("invalid_pilot_source_manifest")
    return reasons


def run_pilot(
    root: Path,
    output: Path,
    *,
    commit_after: str,
    files_changed: Sequence[str],
    timestamp: str,
) -> dict[str, Any]:
    """Compile, execute focused verification, receipt, and conservative verdict."""

    from scripts.project_orchestrator import compile_project

    manifest = _load_json(root / "benchmarks" / "zeref-pilot" / "manifest.json")
    binding = _load_json(
        root / "benchmarks" / "zeref-pilot" / "plan-binding.json"
    )
    if not files_changed:
        raise ValueError("pilot requires an observed changed-file set")
    started = datetime.fromisoformat(timestamp).astimezone(timezone.utc)
    verification_now = started + timedelta(minutes=30)
    result_holder: dict[str, Any] = {}

    def build(target: Path) -> None:
        pack = target / "PACK"
        compile_project(
            manifest,
            pack,
            deterministic=True,
            generated_at=timestamp,
            zeref_contract=binding,
        )
        profile = _load_json(pack / "ZEREF_EXECUTION_PROFILE.json")
        command = [
            sys.executable,
            "-m",
            "unittest",
            "tests.test_zeref_profile",
            "tests.test_zeref_receipt",
            "-v",
        ]
        completed = subprocess.run(
            command,
            cwd=root,
            text=True,
            capture_output=True,
            check=False,
        )
        raw = target / "RAW_OUTPUT"
        raw.mkdir(parents=True)
        (raw / "focused-tests.stdout.txt").write_text(
            completed.stdout,
            encoding="utf-8",
        )
        (raw / "focused-tests.stderr.txt").write_text(
            completed.stderr,
            encoding="utf-8",
        )
        evidence = [
            {
                "id": f"EVD-{index:03d}",
                "control_id": control_id,
                "subject_commit": commit_after,
                "command": " ".join(command),
                "result": "PASS" if completed.returncode == 0 else "FAIL",
                "timestamp": timestamp,
                "reviewer": "primary-agent",
            }
            for index, control_id in enumerate(
                profile["required_controls"],
                start=1,
            )
        ]
        receipt: dict[str, Any] = {
            "schema_id": "grimoire.zeref.receipt.v1",
            "schema_version": "1.0",
            "profile_hash": zeref_profile_hash(profile),
            "pack_hash": profile["pack_hash"],
            "plan": profile["plan"],
            "project": {
                "repository": profile["project"]["repository"],
                "commit_before": profile["project"]["commit"],
                "commit_after": commit_after,
                "branch": "test/grimoire-61-zeref-end-to-end-pilot",
            },
            "roles": [{"name": "Codex Implementer", "kind": "lead"}],
            "models": [
                {
                    "requested": "lowest-cost-capable",
                    "actual": "HOST_NOT_EXPOSED",
                }
            ],
            "tools": [
                "filesystem-read",
                "filesystem-write",
                "git-read",
                "test-runner",
            ],
            "commands": [" ".join(command)],
            "files_changed": sorted(set(files_changed)),
            "tests": [
                {
                    "name": "phase-7-contract-tests",
                    "result": "PASS" if completed.returncode == 0 else "FAIL",
                    "evidence_id": evidence[0]["id"],
                }
            ],
            "evidence": evidence,
            "approvals": [],
            "retries": 0,
            "cost": {
                "amount": 0,
                "currency": "USD",
                "ceiling_status": "WITHIN_CEILING",
            },
            "stop_events": [],
            "completion_status": (
                "PASS" if completed.returncode == 0 else "BLOCKED"
            ),
            "memory_proposals": [],
            "external_actions": [],
            "timestamp": timestamp,
            "expires_at": (started + timedelta(hours=1)).isoformat(),
            "runtime": {
                "harness": "codex",
                "zeref_layer": "installed-contract",
                "capability": "LOCAL_HARNESS_EXECUTION",
            },
        }
        receipt["integrity"] = {
            "algorithm": "sha256-canonical-json-v1",
            "digest": receipt_integrity_hash(receipt),
        }
        _write_json(target / "EXECUTION_RECEIPT.v1.json", receipt)
        verification = verify_zeref_receipt(
            receipt,
            profile,
            now=verification_now,
        ).to_dict()
        _write_json(target / "RECEIPT_VERIFICATION.json", verification)
        pilot_result = {
            "schema_version": 1,
            "pilot_status": (
                "PARTIAL"
                if verification["verification_status"] == "PASS"
                else "FAIL"
            ),
            "receipt_verification_status": verification[
                "verification_status"
            ],
            "zeref_execution_status": verification[
                "zeref_execution_status"
            ],
            "reason_codes": (
                ["independent_reproduction_required"]
                if verification["verification_status"] == "PASS"
                else verification["reason_codes"]
            ),
            "profile_hash": receipt["profile_hash"],
            "pack_hash": receipt["pack_hash"],
            "commit_before": profile["project"]["commit"],
            "commit_after": commit_after,
            "focused_test_exit_code": completed.returncode,
        }
        _write_json(target / "PILOT_RESULT.json", pilot_result)
        _write_json(
            target / "ENVIRONMENT.json",
            {
                "python": platform.python_version(),
                "implementation": platform.python_implementation(),
                "platform": platform.platform(),
                "commit_before": profile["project"]["commit"],
                "commit_after": commit_after,
                "timestamp": timestamp,
            },
        )
        (target / "ROLLBACK.md").write_text(
            "# Pilot Rollback\n\n"
            "Delete this generated pilot directory. No external service, "
            "credential, Zeref internal, or canonical memory was changed.\n",
            encoding="utf-8",
        )
        source_files = {
            str(path.relative_to(target)): _sha256(path)
            for path in target.rglob("*")
            if path.is_file()
            and path.name != "PILOT_SOURCE_MANIFEST.json"
        }
        _write_json(
            target / "PILOT_SOURCE_MANIFEST.json",
            {
                "schema_version": 1,
                "files": dict(sorted(source_files.items())),
            },
        )
        result_holder["result"] = pilot_result

    atomic_write_directory(output, PILOT_FILES, build)
    return result_holder["result"]


def create_reproduction_attestation(
    primary: Path,
    reproduction: Path,
    *,
    reviewer: str,
    producer: str,
    timestamp: str,
) -> dict[str, Any]:
    """Compare two complete runs and create a detached reviewer record."""

    if not reviewer or not producer or reviewer == producer:
        raise ValueError("reviewer must be distinct from producer")
    if _verify_file_manifest(primary) or _verify_file_manifest(reproduction):
        raise ValueError("pilot source artifacts do not match their manifests")
    primary_result = _load_json(primary / "PILOT_RESULT.json")
    reproduced_result = _load_json(reproduction / "PILOT_RESULT.json")
    comparable = (
        "pilot_status",
        "receipt_verification_status",
        "zeref_execution_status",
        "profile_hash",
        "pack_hash",
        "commit_before",
        "commit_after",
        "focused_test_exit_code",
    )
    if any(primary_result[key] != reproduced_result[key] for key in comparable):
        raise ValueError("independent reproduction verdict does not match")
    value: dict[str, Any] = {
        "schema_id": "grimoire.zeref.pilot-attestation.v1",
        "schema_version": "1.0",
        "primary_evidence_hash": _manifest_hash(primary),
        "reproduction_evidence_hash": _manifest_hash(reproduction),
        "pilot_evidence_hash": _manifest_hash(primary),
        "reviewer": reviewer,
        "producer": producer,
        "result": "MATCH",
        "timestamp": timestamp,
        "reviewer_identity_status": (
            "DECLARED_NOT_CRYPTOGRAPHICALLY_VERIFIED"
        ),
    }
    value["integrity"] = {
        "algorithm": "sha256-canonical-json-v1",
        "digest": _canonical_hash(value),
    }
    return value


def verify_pilot_reproduction(
    primary: Path,
    reproduction: Path,
    attestation: Any,
    *,
    now: datetime | None = None,
) -> dict[str, Any]:
    """Verify both evidence packages plus a separate reproduction attestation."""

    reasons = set(_verify_file_manifest(primary))
    reasons.update(_verify_file_manifest(reproduction))
    if not isinstance(attestation, dict):
        reasons.add("invalid_reproduction_attestation")
        attestation = {}
    integrity = attestation.get("integrity")
    unsigned = dict(attestation)
    unsigned.pop("integrity", None)
    if (
        not isinstance(integrity, dict)
        or integrity.get("algorithm") != "sha256-canonical-json-v1"
        or integrity.get("digest") != _canonical_hash(unsigned)
    ):
        reasons.add("attestation_integrity_mismatch")
    try:
        evidence_hash = _manifest_hash(primary)
        reproduction_hash = _manifest_hash(reproduction)
    except (OSError, ValueError, KeyError, json.JSONDecodeError):
        evidence_hash = ""
        reproduction_hash = ""
    if attestation.get("pilot_evidence_hash") != evidence_hash:
        reasons.add("pilot_evidence_mismatch")
    if attestation.get("primary_evidence_hash") != evidence_hash:
        reasons.add("primary_evidence_mismatch")
    if attestation.get("reproduction_evidence_hash") != reproduction_hash:
        reasons.add("reproduction_evidence_mismatch")
    if (
        not isinstance(attestation.get("reviewer"), str)
        or not attestation.get("reviewer")
        or attestation.get("reviewer") == attestation.get("producer")
    ):
        reasons.add("independent_reviewer_missing")
    if attestation.get("result") != "MATCH":
        reasons.add("independent_reproduction_mismatch")
    if attestation.get("reviewer_identity_status") != (
        "DECLARED_NOT_CRYPTOGRAPHICALLY_VERIFIED"
    ):
        reasons.add("reviewer_identity_status_invalid")
    try:
        primary_result = _load_json(primary / "PILOT_RESULT.json")
        reproduction_result = _load_json(
            reproduction / "PILOT_RESULT.json"
        )
        required_result = {
            "pilot_status": "PARTIAL",
            "receipt_verification_status": "PASS",
            "zeref_execution_status": "NOT_VERIFIED",
            "focused_test_exit_code": 0,
        }
        for field, expected in required_result.items():
            if primary_result.get(field) != expected:
                reasons.add("primary_result_not_eligible")
            if reproduction_result.get(field) != expected:
                reasons.add("reproduction_result_not_eligible")
        if "independent_reproduction_required" not in primary_result.get(
            "reason_codes",
            [],
        ):
            reasons.add("primary_result_not_eligible")
        if "independent_reproduction_required" not in reproduction_result.get(
            "reason_codes",
            [],
        ):
            reasons.add("reproduction_result_not_eligible")
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError):
        reasons.add("pilot_result_invalid")
    current = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    try:
        attested_at = datetime.fromisoformat(
            attestation["timestamp"]
        ).astimezone(timezone.utc)
        if attested_at > current or current - attested_at > timedelta(hours=24):
            reasons.add("attestation_not_current")
    except (KeyError, TypeError, ValueError):
        reasons.add("invalid_attestation_time")
    if reasons:
        return {
            "pilot_status": "FAIL",
            "zeref_execution_status": "BLOCKED",
            "reason_codes": sorted(reasons),
            "reviewer_identity_status": "NOT_VERIFIED",
        }
    return {
        "pilot_status": "PASS",
        "zeref_execution_status": "PASS",
        "reason_codes": ["independent_reproduction_matched"],
        "reviewer_identity_status": attestation[
            "reviewer_identity_status"
        ],
    }
