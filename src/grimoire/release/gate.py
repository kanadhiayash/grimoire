"""Fail-closed, non-mutating final release blocker reporting."""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping

from grimoire.benchmarks import BenchmarkContractError
from grimoire.benchmarks.release_candidate import (
    compare_release_candidate_runs,
    load_release_candidate_suite,
)
from grimoire.release.evidence import (
    ReleaseEvidenceError,
    verify_release_evidence,
)


SEMVER = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+$")
COMMIT = re.compile(r"^[0-9a-f]{40}$")
TAG = re.compile(r"^v[0-9]+\.[0-9]+\.[0-9]+$")
FRESHNESS_WINDOW = timedelta(hours=24)
CANONICAL_SUITE = Path("benchmarks/release-candidate/suite.json")


def _git(root: Path, *arguments: str) -> tuple[int, str]:
    completed = subprocess.run(
        ["git", *arguments],
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
    )
    return completed.returncode, completed.stdout.strip()


def _json_object(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("expected_json_object")
    return value


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _version_blockers(root: Path, intended_version: str) -> set[str]:
    reasons: set[str] = set()
    if not SEMVER.fullmatch(intended_version):
        return {"intended_version_invalid"}
    try:
        if (root / "VERSION").read_text(encoding="utf-8").strip() != intended_version:
            reasons.add("version_file_mismatch")
    except OSError:
        reasons.add("version_file_mismatch")
    for path, code in (
        (root / "policies" / "baseline.json", "baseline_version_mismatch"),
        (root / "REPOSITORY_INDEX.json", "repository_index_version_mismatch"),
    ):
        try:
            if _json_object(path).get("standard_version") != intended_version:
                reasons.add(code)
        except (OSError, UnicodeError, ValueError, json.JSONDecodeError):
            reasons.add(code)
    try:
        changelog = (root / "CHANGELOG.md").read_text(encoding="utf-8")
        if not re.search(
            rf"^## \[{re.escape(intended_version)}\] - \d{{4}}-\d{{2}}-\d{{2}}$",
            changelog,
            flags=re.MULTILINE,
        ):
            reasons.add("changelog_version_missing")
    except OSError:
        reasons.add("changelog_version_missing")
    try:
        release = (
            root / "docs" / "releases" / f"{intended_version}.md"
        ).read_text(encoding="utf-8")
        expected_heading = f"# Grimoire {intended_version} Release\n"
        if not release.startswith(expected_heading):
            reasons.add("release_document_version_mismatch")
        if "**Status: RELEASED**" not in release:
            reasons.add("release_document_not_final")
    except OSError:
        reasons.add("release_document_version_mismatch")
        reasons.add("release_document_not_final")
    try:
        readme = (root / "README.md").read_text(encoding="utf-8")
        if f"Current release: `{intended_version}`" not in readme:
            reasons.add("readme_version_mismatch")
    except OSError:
        reasons.add("readme_version_mismatch")
    return reasons


def _approval_blockers(
    evidence: Mapping[str, Any],
    *,
    expected_commit: str,
    now: datetime,
) -> set[str]:
    approvals = evidence.get("approvals")
    if not isinstance(approvals, list):
        return {"release_approval_missing"}
    matching = [
        item
        for item in approvals
        if isinstance(item, dict)
        and item.get("action") == "release"
        and item.get("commit") == expected_commit
        and item.get("scope") == "exact-commit-release"
    ]
    if not matching:
        return {"release_approval_missing"}
    invalid = False
    stale = False
    future = False
    for approval in matching:
        approved_at = _parsed_timestamp(approval.get("approved_at"))
        if approved_at is None:
            invalid = True
            continue
        if approved_at > now:
            future = True
            continue
        if now - approved_at <= FRESHNESS_WINDOW:
            return set()
        stale = True
    reasons: set[str] = set()
    if invalid:
        reasons.add("release_approval_invalid")
    if stale:
        reasons.add("release_approval_stale")
    if future:
        reasons.add("release_approval_future")
    return reasons


def _parsed_timestamp(value: Any) -> datetime | None:
    if not isinstance(value, str):
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return None
    return parsed.astimezone(timezone.utc)


def _freshness_blockers(
    *,
    candidate_results: Iterable[Mapping[str, Any]],
    release_evidence: Mapping[str, Any],
    now: datetime,
) -> set[str]:
    reasons: set[str] = set()
    finished: list[datetime] = []
    for result in candidate_results:
        gates = result.get("gates")
        if not isinstance(gates, list):
            reasons.add("release_candidate_timestamp_invalid")
            continue
        for gate in gates:
            if not isinstance(gate, dict) or "command" not in gate:
                continue
            timestamp = _parsed_timestamp(gate.get("finished_at"))
            if timestamp is None:
                reasons.add("release_candidate_timestamp_invalid")
            else:
                finished.append(timestamp)
    if not finished:
        reasons.add("release_candidate_timestamp_invalid")
    elif any(item > now for item in finished):
        reasons.add("release_candidate_timestamp_invalid")
    elif any(now - item > FRESHNESS_WINDOW for item in finished):
        reasons.add("release_candidate_stale")

    created_at = _parsed_timestamp(release_evidence.get("created_at"))
    if created_at is None or created_at > now:
        reasons.add("release_evidence_timestamp_invalid")
    elif now - created_at > FRESHNESS_WINDOW:
        reasons.add("release_evidence_stale")
    return reasons


def _command_matches(
    expected: Any,
    observed: Any,
    *,
    expected_commit: str,
) -> bool:
    if not isinstance(expected, list) or not isinstance(observed, list):
        return False
    if len(expected) != len(observed):
        return False
    for expected_item, observed_item in zip(expected, observed):
        if not isinstance(expected_item, str) or not isinstance(observed_item, str):
            return False
        if expected_item == "{python}":
            if not observed_item:
                return False
        elif "{run_output}" in expected_item:
            prefix, suffix = expected_item.split("{run_output}", 1)
            prefix = prefix.replace("{commit}", expected_commit)
            suffix = suffix.replace("{commit}", expected_commit)
            if not observed_item.startswith(prefix) or not observed_item.endswith(suffix):
                return False
            middle = observed_item[len(prefix) :]
            if suffix:
                middle = middle[: -len(suffix)]
            if not middle or not Path(middle).is_absolute():
                return False
        elif expected_item.replace("{commit}", expected_commit) != observed_item:
            return False
    return True


def _gate_matches(
    expected: Any,
    observed: Any,
    *,
    expected_commit: str,
) -> bool:
    if not isinstance(expected, dict) or not isinstance(observed, dict):
        return False
    for key in ("id", "category", "hard_gate"):
        if observed.get(key) != expected.get(key):
            return False
    if "command" in expected:
        return "declared_status" not in observed and _command_matches(
            expected.get("command"),
            observed.get("command"),
            expected_commit=expected_commit,
        )
    return (
        "command" not in observed
        and observed.get("status") == expected.get("declared_status")
        and observed.get("reason_codes") == expected.get("reason_codes")
    )


def _canonical_candidate_blockers(
    *,
    root: Path,
    expected_commit: str,
    candidate_results: Iterable[Mapping[str, Any]],
) -> set[str]:
    try:
        suite = load_release_candidate_suite(root / CANONICAL_SUITE)
        if set(suite) != {"schema_version", "suite_id", "sources", "gates"}:
            raise ValueError("invalid_canonical_suite")
        if suite.get("schema_version") != 1:
            raise ValueError("invalid_canonical_suite")
        sources = suite.get("sources")
        gates = suite.get("gates")
        if (
            not isinstance(suite.get("suite_id"), str)
            or not isinstance(sources, list)
            or not sources
            or not all(isinstance(item, str) and item for item in sources)
            or not isinstance(gates, list)
            or not gates
        ):
            raise ValueError("invalid_canonical_suite")
        tree_code, tree = _git(root, "rev-parse", f"{expected_commit}^{{tree}}")
        if tree_code != 0:
            raise ValueError("invalid_canonical_suite")
        source_records = []
        for source in sorted(sources):
            resolved = (root / source).resolve()
            if root not in resolved.parents or not resolved.is_file():
                raise ValueError("invalid_canonical_suite")
            source_records.append({"path": source, "sha256": _sha256(resolved)})
        expected_manifest = {
            "commit": expected_commit,
            "sources": source_records,
            "tree": tree,
        }
        results = list(candidate_results)
        if len(results) != 3:
            raise ValueError("invalid_canonical_suite")
        for result in results:
            observed_gates = result.get("gates")
            if (
                result.get("suite_id") != suite["suite_id"]
                or result.get("source_manifest") != expected_manifest
                or not isinstance(observed_gates, list)
                or len(observed_gates) != len(gates)
                or not all(
                    _gate_matches(
                        expected,
                        observed,
                        expected_commit=expected_commit,
                    )
                    for expected, observed in zip(gates, observed_gates)
                )
            ):
                raise ValueError("invalid_canonical_suite")
    except (
        BenchmarkContractError,
        OSError,
        UnicodeError,
        ValueError,
        TypeError,
    ):
        return {"release_candidate_not_canonical"}
    return set()


def verify_release_tag(
    root: Path,
    *,
    tag: str,
    expected_commit: str,
) -> dict[str, Any]:
    """Verify an existing local tag resolves to the exact release commit."""

    if not TAG.fullmatch(tag):
        reasons = ["release_tag_invalid"]
    else:
        code, observed = _git(root, "rev-parse", f"refs/tags/{tag}^{{commit}}")
        if code != 0:
            reasons = ["release_tag_missing"]
        elif observed != expected_commit:
            reasons = ["release_tag_commit_mismatch"]
        else:
            reasons = []
    return {
        "status": "PASS" if not reasons else "BLOCKED",
        "verified": not reasons,
        "reason_codes": reasons,
    }


def evaluate_final_release(
    *,
    root: Path,
    expected_commit: str,
    intended_version: str,
    intended_tag: str,
    candidate_runs: Iterable[Path],
    candidate_comparison: Mapping[str, Any],
    release_evidence: Mapping[str, Any],
    require_tag: bool = False,
    now: datetime | None = None,
) -> dict[str, Any]:
    """Report release blockers without authorizing a release."""

    root = root.resolve()
    reasons = _version_blockers(root, intended_version)
    if not COMMIT.fullmatch(expected_commit):
        reasons.add("expected_commit_invalid")
    if intended_tag != f"v{intended_version}":
        reasons.add("release_tag_version_mismatch")
    code, observed_commit = _git(root, "rev-parse", "HEAD")
    if code != 0 or observed_commit != expected_commit:
        reasons.add("source_commit_mismatch")
    status_code, tree_state = _git(
        root,
        "status",
        "--porcelain",
        "--untracked-files=all",
    )
    if status_code != 0 or tree_state:
        reasons.add("release_source_not_clean")

    current = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    runs = list(candidate_runs)
    candidate_results: list[dict[str, Any]] = []
    try:
        observed_comparison = compare_release_candidate_runs(
            runs,
            expected_commit=expected_commit,
        )
        if dict(candidate_comparison) != observed_comparison:
            reasons.add("release_candidate_comparison_mismatch")
        if observed_comparison.get("verdict") != "PASS":
            reasons.add("release_candidate_not_pass")
        for path in runs:
            result = _json_object(path / "RELEASE_CANDIDATE_RESULTS.json")
            candidate_results.append(result)
            if any(
                gate.get("hard_gate") is True and gate.get("status") != "PASS"
                for gate in result.get("gates", [])
                if isinstance(gate, dict)
            ):
                reasons.add("release_candidate_hard_gate_not_pass")
    except (
        BenchmarkContractError,
        OSError,
        UnicodeError,
        ValueError,
        json.JSONDecodeError,
    ):
        reasons.add("release_candidate_evidence_invalid")

    reasons.update(
        _freshness_blockers(
            candidate_results=candidate_results,
            release_evidence=release_evidence,
            now=current,
        )
    )
    reasons.update(
        _canonical_candidate_blockers(
            root=root,
            expected_commit=expected_commit,
            candidate_results=candidate_results,
        )
    )

    try:
        evidence_result = verify_release_evidence(
            dict(release_evidence),
            root=root,
            expected_commit=expected_commit,
        )
    except (
        ReleaseEvidenceError,
        OSError,
        UnicodeError,
        ValueError,
        TypeError,
    ):
        evidence_result = {
            "verification_status": "FAIL",
            "release_assurance_status": "BLOCKED",
            "package_status": "FAIL",
            "reason_codes": ["invalid_release_evidence"],
        }
    if evidence_result.get("verification_status") != "PASS":
        reasons.add("release_evidence_verification_failed")
    if (
        evidence_result.get("release_assurance_status") != "PASS"
        or evidence_result.get("package_status") != "PASS"
    ):
        reasons.add("release_evidence_not_pass")
    reasons.update(str(item) for item in evidence_result.get("reason_codes", []))
    reasons.update(
        _approval_blockers(
            release_evidence,
            expected_commit=expected_commit,
            now=current,
        )
    )
    if require_tag:
        reasons.update(
            verify_release_tag(
                root,
                tag=intended_tag,
                expected_commit=expected_commit,
            )["reason_codes"]
        )
    reasons.add("external_signature_contract_unavailable")
    reasons.add("release_freshness_not_independently_verified")
    ordered = sorted(reasons)
    return {
        "status": "BLOCKED",
        "eligible": False,
        "decision_contract": "BLOCKER_REPORT_V1",
        "pass_supported": False,
        "source_commit": expected_commit,
        "intended_version": intended_version,
        "intended_tag": intended_tag,
        "tag_required": require_tag,
        "reason_codes": ordered,
    }
