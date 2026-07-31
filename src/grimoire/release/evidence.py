"""Dependency-free release evidence generation and verification."""

from __future__ import annotations

import hashlib
import json
import os
import platform
import re
import subprocess
import sys
from copy import deepcopy
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable, Mapping

from grimoire.benchmarks.runner import (
    BenchmarkContractError,
    validate_benchmark_result,
)


SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")
COMMIT_PATTERN = re.compile(r"^[0-9a-f]{40}$")
EVIDENCE_ID_PATTERN = re.compile(r"^GRM-RELEASE-[0-9a-f]{12}$")
SUITE_ID_PATTERN = re.compile(r"^[a-z0-9][a-z0-9-]{0,79}$")


class ReleaseEvidenceError(ValueError):
    """Raised when release evidence inputs violate the closed contract."""


def _canonical_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n"
    ).encode("utf-8")


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _git(root: Path, *arguments: str) -> str:
    completed = subprocess.run(
        ["git", *arguments],
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode != 0:
        raise ReleaseEvidenceError("git_state_not_verified")
    return completed.stdout.strip()


def _relative_file(root: Path, path: Path) -> tuple[str, Path]:
    resolved_root = root.resolve()
    candidate = Path(os.path.abspath(path))
    resolved = candidate.resolve()
    try:
        relative = resolved.relative_to(resolved_root)
    except ValueError as exc:
        raise ReleaseEvidenceError("release_input_outside_repository") from exc
    cursor = candidate
    while cursor != resolved_root:
        if cursor.is_symlink():
            raise ReleaseEvidenceError("release_input_not_regular_file")
        if cursor == cursor.parent:
            raise ReleaseEvidenceError("release_input_outside_repository")
        cursor = cursor.parent
    if not resolved.is_file():
        raise ReleaseEvidenceError("release_input_not_regular_file")
    return str(relative), resolved


def _benchmark_metadata(
    path: Path,
    *,
    expected_commit: str,
) -> tuple[str, str, str]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ReleaseEvidenceError("invalid_benchmark_evidence") from exc
    if not isinstance(value, dict):
        raise ReleaseEvidenceError("invalid_benchmark_evidence")
    try:
        validate_benchmark_result(value, evidence_root=path.parent)
    except (BenchmarkContractError, OSError, TypeError) as exc:
        raise ReleaseEvidenceError("invalid_benchmark_evidence") from exc
    status = value.get("verdict", value.get("status"))
    if status not in {"PASS", "PARTIAL", "FAIL", "NOT_VERIFIED"}:
        raise ReleaseEvidenceError("invalid_benchmark_status")
    commit = value.get("commit")
    if commit != expected_commit:
        raise ReleaseEvidenceError("benchmark_commit_mismatch")
    suite_id = value.get("suite_id")
    if (
        not isinstance(suite_id, str)
        or not SUITE_ID_PATTERN.fullmatch(suite_id)
    ):
        raise ReleaseEvidenceError("invalid_benchmark_suite")
    return str(status), commit, suite_id


def _is_timestamp(value: Any) -> bool:
    if not isinstance(value, str) or not value:
        return False
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return False
    return parsed.tzinfo is not None


def _is_approval(value: Any) -> bool:
    return (
        isinstance(value, dict)
        and set(value)
        == {"action", "commit", "approver", "approved_at", "scope"}
        and value.get("action") == "release"
        and isinstance(value.get("commit"), str)
        and bool(COMMIT_PATTERN.fullmatch(value["commit"]))
        and isinstance(value.get("approver"), str)
        and bool(value["approver"])
        and _is_timestamp(value.get("approved_at"))
        and value.get("scope") == "exact-commit-release"
    )


def release_evidence_digest(evidence: Mapping[str, Any]) -> str:
    unsigned = deepcopy(dict(evidence))
    unsigned.pop("integrity", None)
    return hashlib.sha256(_canonical_bytes(unsigned)).hexdigest()


def build_release_evidence(
    root: Path,
    *,
    artifacts: Iterable[Path],
    benchmarks: Iterable[Path],
    expected_commit: str,
    timestamp: str,
    approvals: Iterable[Mapping[str, Any]] = (),
) -> dict[str, Any]:
    root = root.resolve()
    observed_commit = _git(root, "rev-parse", "HEAD")
    if observed_commit != expected_commit:
        raise ReleaseEvidenceError("source_commit_mismatch")
    tree_output = _git(root, "status", "--porcelain", "--untracked-files=no")
    artifact_records = []
    for path in artifacts:
        relative, resolved = _relative_file(root, path)
        artifact_records.append(
            {
                "path": relative,
                "sha256": _sha256(resolved),
                "size": resolved.stat().st_size,
            }
        )
    benchmark_records = []
    for path in benchmarks:
        relative, resolved = _relative_file(root, path)
        status, commit, suite_id = _benchmark_metadata(
            resolved,
            expected_commit=expected_commit,
        )
        benchmark_records.append(
            {
                "path": relative,
                "sha256": _sha256(resolved),
                "status": status,
                "commit": commit,
                "suite_id": suite_id,
            }
        )
    if not artifact_records or not benchmark_records:
        raise ReleaseEvidenceError("release_evidence_inputs_missing")
    if not _is_timestamp(timestamp):
        raise ReleaseEvidenceError("release_timestamp_invalid")
    approval_records = [dict(item) for item in approvals]
    if not all(_is_approval(item) for item in approval_records):
        raise ReleaseEvidenceError("release_approval_invalid")
    value: dict[str, Any] = {
        "schema_id": "grimoire.release.evidence.v1",
        "schema_version": "1.0",
        "evidence_id": f"GRM-RELEASE-{observed_commit[:12]}",
        "source_commit": observed_commit,
        "created_at": timestamp,
        "environment": {
            "python": platform.python_version(),
            "implementation": platform.python_implementation(),
            "platform": platform.platform(),
            "tree_state": "CLEAN" if not tree_output else "DIRTY",
        },
        "artifacts": sorted(artifact_records, key=lambda item: item["path"]),
        "benchmarks": sorted(
            benchmark_records,
            key=lambda item: item["path"],
        ),
        "approvals": approval_records,
        "permissions": {
            "allowed": [
                "generate-evidence",
                "rollback-dry-run",
                "verify-evidence",
            ],
            "prohibited": ["deploy", "publish", "release", "sign"],
        },
        "signature": {
            "status": "NOT_VERIFIED",
            "method": "EXTERNAL_NOT_CONFIGURED",
            "reason": "release_signing_not_authorized_in_evidence_pr",
        },
    }
    value["integrity"] = {
        "algorithm": "sha256-canonical-json-v1",
        "digest": release_evidence_digest(value),
    }
    return value


def verify_release_evidence(
    evidence: Any,
    *,
    root: Path,
    expected_commit: str,
) -> dict[str, Any]:
    reasons: set[str] = set()
    if not isinstance(evidence, dict):
        return {
            "verification_status": "FAIL",
            "release_assurance_status": "BLOCKED",
            "package_status": "FAIL",
            "reason_codes": ["invalid_release_evidence"],
        }
    required = {
        "schema_id",
        "schema_version",
        "evidence_id",
        "source_commit",
        "created_at",
        "environment",
        "artifacts",
        "benchmarks",
        "approvals",
        "permissions",
        "signature",
        "integrity",
    }
    if set(evidence) != required:
        reasons.add("invalid_release_evidence_shape")
    if (
        evidence.get("schema_id") != "grimoire.release.evidence.v1"
        or evidence.get("schema_version") != "1.0"
        or not isinstance(evidence.get("evidence_id"), str)
        or not EVIDENCE_ID_PATTERN.fullmatch(evidence["evidence_id"])
    ):
        reasons.add("release_schema_mismatch")
    if evidence.get("source_commit") != expected_commit:
        reasons.add("source_commit_mismatch")
    if (
        not isinstance(evidence.get("source_commit"), str)
        or not COMMIT_PATTERN.fullmatch(evidence["source_commit"])
        or evidence.get("evidence_id")
        != f"GRM-RELEASE-{evidence.get('source_commit', '')[:12]}"
    ):
        reasons.add("release_identity_invalid")
    if not _is_timestamp(evidence.get("created_at")):
        reasons.add("release_timestamp_invalid")
    environment = evidence.get("environment")
    if (
        not isinstance(environment, dict)
        or set(environment)
        != {"python", "implementation", "platform", "tree_state"}
        or not all(
            isinstance(environment.get(key), str) and environment.get(key)
            for key in ("python", "implementation", "platform")
        )
        or environment.get("tree_state") not in {"CLEAN", "DIRTY"}
    ):
        reasons.add("environment_record_invalid")
    try:
        observed_commit = _git(root, "rev-parse", "HEAD")
        if observed_commit != expected_commit:
            reasons.add("checked_out_commit_mismatch")
    except ReleaseEvidenceError:
        reasons.add("checked_out_commit_not_verified")
    integrity = evidence.get("integrity")
    if (
        not isinstance(integrity, dict)
        or integrity.get("algorithm") != "sha256-canonical-json-v1"
        or integrity.get("digest") != release_evidence_digest(evidence)
    ):
        reasons.add("evidence_integrity_mismatch")
    artifact_records = evidence.get("artifacts")
    if not isinstance(artifact_records, list):
        reasons.add("artifact_records_invalid")
        artifact_records = []
    elif not artifact_records:
        reasons.add("artifact_records_missing")
    for record in artifact_records:
        if (
            not isinstance(record, dict)
            or set(record) != {"path", "sha256", "size"}
            or not isinstance(record.get("path"), str)
            or not isinstance(record.get("sha256"), str)
            or not SHA256_PATTERN.fullmatch(record["sha256"])
            or not isinstance(record.get("size"), int)
            or isinstance(record.get("size"), bool)
            or record["size"] < 0
        ):
            reasons.add("artifact_record_invalid")
            continue
        try:
            relative, path = _relative_file(root, root / record["path"])
            if (
                relative != record["path"]
                or _sha256(path) != record["sha256"]
                or path.stat().st_size != record["size"]
            ):
                reasons.add("artifact_hash_mismatch")
        except ReleaseEvidenceError:
            reasons.add("artifact_record_invalid")
    benchmark_records = evidence.get("benchmarks")
    if not isinstance(benchmark_records, list):
        reasons.add("benchmark_records_invalid")
        benchmark_records = []
    elif not benchmark_records:
        reasons.add("benchmark_records_missing")
    for record in benchmark_records:
        if (
            not isinstance(record, dict)
            or set(record)
            != {"path", "sha256", "status", "commit", "suite_id"}
            or not isinstance(record.get("path"), str)
            or not isinstance(record.get("sha256"), str)
            or not SHA256_PATTERN.fullmatch(record["sha256"])
            or record.get("status")
            not in {"PASS", "PARTIAL", "FAIL", "NOT_VERIFIED"}
            or record.get("commit") != expected_commit
            or not isinstance(record.get("suite_id"), str)
            or not SUITE_ID_PATTERN.fullmatch(record["suite_id"])
        ):
            reasons.add("benchmark_record_invalid")
            continue
        try:
            relative, path = _relative_file(root, root / record["path"])
            observed_status, observed_commit, observed_suite = (
                _benchmark_metadata(path, expected_commit=expected_commit)
            )
            if (
                relative != record["path"]
                or _sha256(path) != record["sha256"]
                or observed_status != record["status"]
                or observed_status != "PASS"
                or observed_commit != record["commit"]
                or observed_suite != record["suite_id"]
            ):
                reasons.add("benchmark_result_mismatch")
        except ReleaseEvidenceError:
            reasons.add("benchmark_record_invalid")
    expected_permissions = {
        "allowed": [
            "generate-evidence",
            "rollback-dry-run",
            "verify-evidence",
        ],
        "prohibited": ["deploy", "publish", "release", "sign"],
    }
    if evidence.get("permissions") != expected_permissions:
        reasons.add("release_permission_scope_mismatch")
    signature = evidence.get("signature")
    if (
        not isinstance(signature, dict)
        or set(signature) != {"status", "method", "reason"}
        or not all(
            isinstance(signature.get(key), str) and signature.get(key)
            for key in ("status", "method", "reason")
        )
    ):
        reasons.add("signature_record_invalid")
    elif signature.get("status") != "NOT_VERIFIED":
        reasons.add("unsupported_signature_claim")
    approvals = evidence.get("approvals")
    if not isinstance(approvals, list):
        reasons.add("approval_records_invalid")
        approvals = []
    for approval in approvals:
        if not _is_approval(approval):
            reasons.add("approval_record_invalid")
    approval_present = (
        any(
            isinstance(item, dict)
            and item.get("action") == "release"
            and item.get("commit") == expected_commit
            and item.get("scope") == "exact-commit-release"
            for item in approvals
        )
    )
    blocking = {
        reason
        for reason in reasons
        if reason
        not in {
            "release_approval_missing",
            "signature_not_verified",
        }
    }
    if blocking:
        return {
            "verification_status": "FAIL",
            "release_assurance_status": "BLOCKED",
            "package_status": "FAIL",
            "reason_codes": sorted(reasons),
        }
    assurance_reasons = []
    if not approval_present:
        assurance_reasons.append("release_approval_missing")
    if isinstance(signature, dict) and signature.get("status") == "NOT_VERIFIED":
        assurance_reasons.append("signature_not_verified")
    return {
        "verification_status": "PASS",
        "release_assurance_status": (
            "NOT_VERIFIED" if assurance_reasons else "PASS"
        ),
        "package_status": "PARTIAL" if assurance_reasons else "PASS",
        "reason_codes": assurance_reasons,
    }


def rollback_dry_run(
    evidence: Any,
    *,
    root: Path,
    expected_commit: str,
) -> dict[str, Any]:
    verification = verify_release_evidence(
        evidence,
        root=root,
        expected_commit=expected_commit,
    )
    if verification["verification_status"] != "PASS":
        return {
            "status": "BLOCKED",
            "executed": False,
            "steps": [],
            "reason_codes": verification["reason_codes"],
        }
    return {
        "status": "PASS",
        "executed": False,
        "steps": [
            "Confirm no release, tag, package, or deployment was created.",
            "Retain the evidence package and exact commit for review.",
            "Discard only the generated local evidence directory if requested.",
            "Revert the evidence PR through a reviewed Git commit if required.",
        ],
        "reason_codes": ["private_dry_run_only"],
    }
