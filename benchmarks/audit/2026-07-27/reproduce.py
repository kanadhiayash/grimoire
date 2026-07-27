#!/usr/bin/env python3
"""Reproduce the locked Grimoire 0.5.0 audit baseline without fixing it."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import platform
import random
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[3]
BENCHMARK_ROOT = Path(__file__).resolve().parent
FIXTURE_ROOT = BENCHMARK_ROOT / "fixtures"
EXPECTED_PATH = BENCHMARK_ROOT / "expected-baseline.json"
PACKAGE_ROOT = ROOT / "docs" / "audits" / "2026-07-27" / "execution-package"

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

CompileProject = Callable[[dict[str, Any], Path], dict[str, Any]]
_COMPILE_PROJECT: CompileProject | None = None


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _json(value: Any) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _sha256_file(path: Path) -> str:
    return _sha256_bytes(path.read_bytes())


def _canonical_hash(value: Any) -> str:
    encoded = json.dumps(
        value, ensure_ascii=False, separators=(",", ":"), sort_keys=True
    ).encode("utf-8")
    return _sha256_bytes(encoded)


def _git(*args: str) -> str:
    completed = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode:
        raise RuntimeError(completed.stderr.strip() or "git command failed")
    return completed.stdout.strip()


def _git_bytes(commit: str, path: str) -> bytes:
    completed = subprocess.run(
        ["git", "show", f"{commit}:{path}"],
        cwd=ROOT,
        capture_output=True,
        check=False,
    )
    if completed.returncode:
        message = completed.stderr.decode("utf-8", errors="replace").strip()
        raise RuntimeError(message or f"could not read audited input: {path}")
    return completed.stdout


def _verify_audited_commit(expected_commit: str) -> dict[str, Any]:
    head = _git("rev-parse", "HEAD")
    subject = _git("rev-parse", f"{expected_commit}^{{commit}}")
    merge_base = _git("merge-base", expected_commit, head)
    if subject != expected_commit or merge_base != expected_commit:
        raise RuntimeError(
            f"audited commit {expected_commit} is not the current branch base"
        )
    return {
        "commit": expected_commit,
        "current_head": head,
        "relationship": "AUDITED_COMMIT_IS_ANCESTOR_OR_HEAD",
    }


def _verify_fixtures(expected: dict[str, Any]) -> dict[str, str]:
    expected_hashes = expected["fixture_sha256"]
    actual_names = sorted(path.name for path in FIXTURE_ROOT.glob("*.json"))
    if actual_names != sorted(expected_hashes):
        raise RuntimeError("audit fixture file set does not match expected baseline")
    actual = {name: _sha256_file(FIXTURE_ROOT / name) for name in actual_names}
    if actual != expected_hashes:
        raise RuntimeError("audit fixture hash mismatch")
    return actual


def _parse_checksum_ledger(path: Path) -> dict[str, str]:
    checksums: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        cells = [cell.strip().strip("`") for cell in line.split("|")]
        if len(cells) >= 4 and len(cells[2]) == 64:
            checksums[cells[1]] = cells[2]
    return checksums


def _verify_package(expected: dict[str, Any]) -> dict[str, Any]:
    ledger = PACKAGE_ROOT / "18_PACKAGE_CHECKSUMS.md"
    ledger_hash = _sha256_file(ledger)
    if ledger_hash != expected["package_integrity"]["checksum_ledger_sha256"]:
        raise RuntimeError("imported execution package checksum ledger mismatch")
    checksums = _parse_checksum_ledger(ledger)
    expected_names = sorted([*checksums, ledger.name])
    actual_names = sorted(path.name for path in PACKAGE_ROOT.glob("*.md"))
    if len(checksums) != 18 or actual_names != expected_names:
        raise RuntimeError("imported execution package file set mismatch")
    for name, expected_hash in checksums.items():
        if _sha256_file(PACKAGE_ROOT / name) != expected_hash:
            raise RuntimeError(f"imported execution package hash mismatch: {name}")
    return {
        "status": "PASS",
        "listed_files_verified": len(checksums),
        "total_files": len(actual_names),
        "checksum_ledger_sha256": ledger_hash,
    }


def _load_audited_inputs(
    expected: dict[str, Any],
    expected_commit: str,
) -> tuple[dict[str, Any], dict[str, bytes]]:
    expected_hashes = expected["audited_input_sha256"]
    inputs = {
        path: _git_bytes(expected_commit, path) for path in sorted(expected_hashes)
    }
    actual_hashes = {
        path: _sha256_bytes(content) for path, content in inputs.items()
    }
    if actual_hashes != expected_hashes:
        raise RuntimeError("audited production input hash mismatch")
    return (
        {
            "status": "PASS",
            "source": "AUDITED_COMMIT",
            "sha256": actual_hashes,
        },
        inputs,
    )


def _load_audited_compiler(source: bytes, expected_commit: str) -> CompileProject:
    namespace: dict[str, Any] = {
        "__name__": "grimoire_audited_project_orchestrator",
        "__file__": (
            f"{expected_commit}:scripts/project_orchestrator.py"
        ),
    }
    code = compile(
        source,
        namespace["__file__"],
        "exec",
    )
    exec(code, namespace)
    compiler = namespace.get("compile_project")
    if not callable(compiler):
        raise RuntimeError("audited compiler does not expose compile_project")
    return compiler


def _compile_project(
    manifest: dict[str, Any],
    output: Path,
) -> dict[str, Any]:
    if _COMPILE_PROJECT is None:
        raise RuntimeError("audited compiler has not been loaded")
    return _COMPILE_PROJECT(manifest, output)


def _assert_no_symlink_components(path: Path) -> None:
    absolute = Path(os.path.abspath(path))
    for component in (absolute, *absolute.parents):
        if component.is_symlink():
            raise RuntimeError(
                f"evidence output contains a symlink component: {component.name}"
            )


def _atomic_write_text(path: Path, content: str) -> None:
    if path.is_symlink():
        raise RuntimeError(f"evidence destination must not be a symlink: {path.name}")
    temporary_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=path.parent,
            prefix=f".{path.name}.",
            delete=False,
        ) as handle:
            temporary_path = Path(handle.name)
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_path, path)
        temporary_path = None
    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)


def _finding(
    finding_id: str,
    fixture_names: list[str],
    observed: dict[str, Any],
    matched: bool,
) -> dict[str, Any]:
    return {
        "id": finding_id,
        "fixtures": fixture_names,
        "fixture_sha256": {
            name: _sha256_file(FIXTURE_ROOT / name) for name in fixture_names
        },
        "observed": observed,
        "product_status": "FAIL",
        "reproduction_status": "MATCH" if matched else "MISMATCH",
    }


def _base_manifest() -> dict[str, Any]:
    return copy.deepcopy(_load_json(FIXTURE_ROOT / "false-project-readiness.json"))


def _reproduce_false_readiness(scratch: Path) -> dict[str, Any]:
    output = scratch / "false-readiness"
    receipt = _compile_project(_base_manifest(), output)
    project_status = _load_json(output / "PROJECT_STATUS.json")
    matrix = (output / "ACCEPTANCE_MATRIX.md").read_text(encoding="utf-8")
    rows = [
        line
        for line in matrix.splitlines()
        if line.startswith("| ") and "NOT_VERIFIED" in line
    ]
    observed = {
        "execution_receipt_status": receipt["status"],
        "project_status": project_status["status"],
        "acceptance_items": len(rows),
        "acceptance_items_not_verified": len(rows),
        "evidence_inputs_supplied": 0,
    }
    matched = (
        receipt["status"] == "PASS"
        and project_status["status"] == "PASS"
        and len(rows) > 0
    )
    return _finding(
        "false_project_readiness",
        ["false-project-readiness.json"],
        observed,
        matched,
    )


def _reproduce_schema_contradiction(
    schema: dict[str, Any],
    policy: dict[str, Any],
) -> dict[str, Any]:
    contradictions = []
    for name in ("commands", "autonomy_levels"):
        definition = schema["properties"][name]
        required = definition.get("required", [])
        properties = definition.get("properties", {})
        policy_keys = sorted(policy[name])
        forbidden_required = sorted(set(required) - set(properties))
        contradictions.append(
            {
                "object": name,
                "policy_keys": len(policy_keys),
                "required_keys": len(required),
                "properties_defined": len(properties),
                "additional_properties": definition.get("additionalProperties"),
                "required_keys_forbidden": forbidden_required,
            }
        )
    matched = all(
        item["required_keys"] > 0
        and item["properties_defined"] == 0
        and item["additional_properties"] is False
        and len(item["required_keys_forbidden"]) == item["required_keys"]
        for item in contradictions
    )
    return _finding(
        "ai_operations_schema_contradiction",
        ["ai-schema-contradiction.json"],
        {"contradictions": contradictions},
        matched,
    )


def _set_manifest_value(manifest: dict[str, Any], mutation: str, value: Any) -> None:
    if mutation == "users_string":
        manifest["users"] = value
    elif mutation == "risk_string":
        manifest["risk"] = value
    elif mutation == "unknowns_string":
        manifest["unknowns"] = value
    elif mutation == "personal_data_string":
        manifest["data"]["personal_data"] = value
    elif mutation == "unsupported_version":
        manifest["standards"]["version"] = value
    elif mutation == "unknown_property":
        manifest["audit_unknown_field"] = value
    else:
        raise ValueError(f"unsupported audit mutation: {mutation}")


def _classify_manifest(manifest: dict[str, Any], output: Path) -> dict[str, Any]:
    try:
        receipt = _compile_project(manifest, output)
    except ValueError as exc:
        return {
            "outcome": "controlled_rejection",
            "exception_type": type(exc).__name__,
            "diagnostic_hash": _sha256_bytes(str(exc).encode("utf-8")),
        }
    except Exception as exc:  # Audit code intentionally classifies current crashes.
        return {
            "outcome": "unhandled_exception",
            "exception_type": type(exc).__name__,
            "diagnostic_hash": _sha256_bytes(str(exc).encode("utf-8")),
        }
    status_doc = _load_json(output / "PROJECT_STATUS.json")
    return {
        "outcome": "accepted",
        "receipt_status": receipt["status"],
        "unknown_count": status_doc["unknown_count"],
    }


def _reproduce_malformed_manifests(scratch: Path) -> dict[str, Any]:
    fixture_names = [
        "manifest-users-string.json",
        "manifest-risk-string.json",
        "manifest-unknowns-string.json",
        "manifest-personal-data-string.json",
        "manifest-unsupported-version.json",
        "manifest-unknown-property.json",
    ]
    cases = []
    for index, name in enumerate(fixture_names):
        fixture = _load_json(FIXTURE_ROOT / name)
        manifest = _base_manifest()
        _set_manifest_value(manifest, fixture["mutation"], fixture["value"])
        result = _classify_manifest(manifest, scratch / f"manifest-{index:02d}")
        expected = fixture["expected_outcome"]
        matches = result["outcome"] == expected
        if "expected_exception" in fixture:
            matches = matches and result.get("exception_type") == fixture[
                "expected_exception"
            ]
        if "expected_unknown_count" in fixture:
            matches = matches and result.get("unknown_count") == fixture[
                "expected_unknown_count"
            ]
        cases.append(
            {
                "fixture": name,
                "expected": expected,
                "observed": result,
                "matches": matches,
            }
        )
    return _finding(
        "malformed_manifest_handling",
        fixture_names,
        {"cases": cases},
        all(item["matches"] for item in cases),
    )


def _reproduce_prompt_injection(scratch: Path) -> dict[str, Any]:
    fixture = _load_json(FIXTURE_ROOT / "prompt-injection.json")
    output = scratch / "prompt-injection"
    _compile_project(fixture["manifest"], output)
    context = (output / "AI_CONTEXT.md").read_text(encoding="utf-8")
    payload = fixture["payload"]
    observed = {
        "payload_rendered_verbatim": payload in context,
        "untrusted_data_label_present": "UNTRUSTED" in context.upper(),
    }
    matched = (
        observed["payload_rendered_verbatim"]
        and not observed["untrusted_data_label_present"]
    )
    return _finding(
        "prompt_injection_rendering",
        ["prompt-injection.json"],
        observed,
        matched,
    )


def _reproduce_symlink_overwrite(scratch: Path) -> dict[str, Any]:
    output = scratch / "symlink-output"
    output.mkdir()
    target = scratch / "symlink-target.txt"
    original = "AUDIT_SENTINEL\n"
    target.write_text(original, encoding="utf-8")
    (output / "AI_CONTEXT.md").symlink_to(target)
    _compile_project(_base_manifest(), output)
    observed = {
        "target_changed": target.read_text(encoding="utf-8") != original,
        "target_within_temporary_boundary": target.parent == scratch,
    }
    return _finding(
        "symlink_overwrite",
        ["symlink-overwrite.json"],
        observed,
        all(observed.values()),
    )


def _reproduce_dirty_output(scratch: Path) -> dict[str, Any]:
    output = scratch / "dirty-output"
    output.mkdir()
    stale = output / "stale-unrelated.txt"
    stale.write_text("AUDIT_SENTINEL\n", encoding="utf-8")
    _compile_project(_base_manifest(), output)
    observed = {
        "stale_file_retained": stale.is_file(),
        "stale_content_unchanged": stale.read_text(encoding="utf-8")
        == "AUDIT_SENTINEL\n",
    }
    return _finding(
        "dirty_output_retention",
        ["dirty-output.json"],
        observed,
        all(observed.values()),
    )


def _mutation_functions() -> dict[str, Callable[[dict[str, Any], int], None]]:
    return {
        "ai_string": lambda m, i: m.__setitem__("ai", f"ai-{i}"),
        "data_null": lambda m, i: m.__setitem__("data", None),
        "lifecycle_invalid": lambda m, i: m["project"].__setitem__(
            "lifecycle_stage", f"INVALID_{i}"
        ),
        "markets_null": lambda m, i: m.__setitem__("markets", None),
        "missing_project": lambda m, i: m.pop("project"),
        "missing_risk": lambda m, i: m.pop("risk"),
        "personal_data_string": lambda m, i: m["data"].__setitem__(
            "personal_data", "false"
        ),
        "product_types_string": lambda m, i: m["project"].__setitem__(
            "product_types", f"type-{i}"
        ),
        "project_name_empty": lambda m, i: m["project"].__setitem__("name", ""),
        "project_string": lambda m, i: m.__setitem__("project", f"project-{i}"),
        "risk_string": lambda m, i: m.__setitem__("risk", "critical"),
        "schema_version_string": lambda m, i: m.__setitem__("schema_version", "1"),
        "standards_string": lambda m, i: m.__setitem__(
            "standards", f"standards-{i}"
        ),
        "unknown_property": lambda m, i: m.__setitem__(
            f"unexpected_{i}", {"nested": True}
        ),
        "unknowns_null": lambda m, i: m.__setitem__("unknowns", None),
        "unknowns_string": lambda m, i: m.__setitem__("unknowns", "none"),
        "unsupported_version": lambda m, i: m["standards"].__setitem__(
            "version", f"99.0.{i}"
        ),
        "users_string": lambda m, i: m.__setitem__("users", f"users-{i}"),
        "zeref_string": lambda m, i: m.__setitem__("zeref", f"zeref-{i}"),
    }


def _run_fuzz(cases: int, seed: int, scratch: Path) -> tuple[dict[str, Any], list]:
    rng = random.Random(seed)
    mutations = _mutation_functions()
    names = sorted(mutations)
    outcomes = {
        "accepted": 0,
        "controlled_rejection": 0,
        "unhandled_exception": 0,
    }
    case_results = []
    corpus_hash = hashlib.sha256()
    for index in range(cases):
        mutation = rng.choice(names)
        manifest = _base_manifest()
        mutations[mutation](manifest, index)
        case_id = f"GRM-AUDIT-{seed}-{index:04d}"
        encoded = json.dumps(
            manifest, ensure_ascii=False, separators=(",", ":"), sort_keys=True
        ).encode("utf-8")
        corpus_hash.update(case_id.encode("ascii"))
        corpus_hash.update(b"\0")
        corpus_hash.update(encoded)
        result = _classify_manifest(manifest, scratch / "fuzz" / case_id)
        outcomes[result["outcome"]] += 1
        case_results.append(
            {
                "case_id": case_id,
                "input_sha256": _sha256_bytes(encoded),
                "mutation": mutation,
                "result": result,
            }
        )
    return (
        {
            "cases": cases,
            "seed": seed,
            "generator": "grimoire-audit-mutations-v1",
            "corpus_sha256": corpus_hash.hexdigest(),
            "outcomes": outcomes,
            "classification": "FRESH_DETERMINISTIC_BASELINE",
            "historical_counts_reproduced": False,
        },
        case_results,
    )


def _write_evidence(
    output: Path,
    summary: dict[str, Any],
    case_results: list[dict[str, Any]],
    started_at: str,
    finished_at: str,
    exit_code: int,
    argv: list[str],
) -> None:
    _assert_no_symlink_components(output)
    output.mkdir(parents=True, exist_ok=True)
    _assert_no_symlink_components(output)
    environment = {
        "schema_version": 1,
        "os": platform.system(),
        "os_release": platform.release(),
        "machine": platform.machine(),
        "python_implementation": platform.python_implementation(),
        "python_version": platform.python_version(),
        "runtime_dependencies": 0,
        "safe_environment": {
            "LANG": os.environ.get("LANG", "NOT_SET"),
            "TZ": os.environ.get("TZ", "NOT_SET"),
        },
    }
    stdout = (
        f"{summary['reproduction_status']} "
        f"audit={summary['audit_id']} "
        f"findings={len(summary['findings'])} "
        f"fresh_fuzz_cases={summary['fresh_fuzz']['cases']}\n"
    )
    stderr = ""
    invocation = {
        "argv": argv,
        "cwd": ".",
        "started_at": started_at,
        "finished_at": finished_at,
        "exit_code": exit_code,
        "stdout_file": "stdout.txt",
        "stderr_file": "stderr.txt",
    }
    summary["invocation"] = invocation
    files = {
        "environment.json": _json(environment),
        "fresh-fuzz-cases.json": _json(case_results),
        "reproduction-summary.json": _json(summary),
        "stdout.txt": stdout,
        "stderr.txt": stderr,
    }
    for name in [*files, "hashes.json"]:
        if (output / name).is_symlink():
            raise RuntimeError(
                f"evidence destination must not be a symlink: {name}"
            )
    for name, content in files.items():
        _atomic_write_text(output / name, content)
    hashes = {
        name: _sha256_file(output / name)
        for name in sorted(files)
    }
    _atomic_write_text(
        output / "hashes.json",
        _json(
            {
                "schema_version": 1,
                "algorithm": "sha256",
                "files": hashes,
            }
        )
    )
    print(stdout, end="")


def reproduce(expected_commit: str, seed: int, output: Path) -> int:
    global _COMPILE_PROJECT

    started_at = _utc_now()
    expected = _load_json(EXPECTED_PATH)
    if expected_commit != expected["audited_subject"]["commit"]:
        raise RuntimeError("requested commit does not match locked audit subject")
    if seed != expected["fresh_fuzz"]["seed"]:
        raise RuntimeError("requested seed does not match locked audit seed")
    _assert_no_symlink_components(output)

    audited_subject = _verify_audited_commit(expected_commit)
    fixture_hashes = _verify_fixtures(expected)
    package_integrity = _verify_package(expected)
    audited_inputs, audited_input_bytes = _load_audited_inputs(
        expected,
        expected_commit,
    )
    _COMPILE_PROJECT = _load_audited_compiler(
        audited_input_bytes["scripts/project_orchestrator.py"],
        expected_commit,
    )
    audited_ai_schema = json.loads(
        audited_input_bytes[
            "policies/schemas/ai-operations.schema.json"
        ].decode("utf-8")
    )
    audited_ai_policy = json.loads(
        audited_input_bytes["policies/ai-operations.json"].decode("utf-8")
    )
    with tempfile.TemporaryDirectory(prefix="grimoire-audit-") as directory:
        scratch = Path(directory)
        findings = [
            _reproduce_false_readiness(scratch),
            _reproduce_schema_contradiction(
                audited_ai_schema,
                audited_ai_policy,
            ),
            _reproduce_malformed_manifests(scratch),
            _reproduce_prompt_injection(scratch),
            _reproduce_symlink_overwrite(scratch),
            _reproduce_dirty_output(scratch),
        ]
        fresh_fuzz, case_results = _run_fuzz(
            expected["fresh_fuzz"]["cases"], seed, scratch
        )

    all_match = all(
        finding["reproduction_status"] == "MATCH" for finding in findings
    )
    normalized_results = {
        "findings": [
            {
                "id": item["id"],
                "observed": item["observed"],
                "product_status": item["product_status"],
                "reproduction_status": item["reproduction_status"],
            }
            for item in sorted(findings, key=lambda item: item["id"])
        ],
        "fresh_fuzz": fresh_fuzz,
        "package_integrity": package_integrity,
    }
    summary = {
        "schema_version": 1,
        "audit_id": expected["audit_id"],
        "audited_subject": audited_subject,
        "audited_inputs": audited_inputs,
        "package_integrity": package_integrity,
        "fixture_sha256": fixture_hashes,
        "source_fuzz_evidence": expected["source_fuzz_evidence"],
        "fresh_fuzz": fresh_fuzz,
        "findings": sorted(findings, key=lambda item: item["id"]),
        "normalized_results": normalized_results,
        "normalized_results_sha256": _canonical_hash(normalized_results),
        "reproduction_status": "MATCH" if all_match else "MISMATCH",
        "score_claim": {
            "audited_score": 5.4,
            "scale": 10,
            "classification": "HISTORICAL_AUDITED_BASELINE",
            "current_rescore": "NOT_PERFORMED",
        },
        "limitations": [
            "The original 500-case fuzz generator, seed, raw corpus, and logs were not supplied.",
            "The fresh seed-20260727 run is a new deterministic baseline and does not reproduce historical 171/214/115 counts.",
            "This Phase 0 runner records current failures and does not implement production fixes.",
            "Zeref end-to-end consumption remains NOT_VERIFIED.",
        ],
    }
    exit_code = 0 if all_match else 1
    finished_at = _utc_now()
    argv = [
        "python3",
        "benchmarks/audit/2026-07-27/reproduce.py",
        "--expected-commit",
        expected_commit,
        "--seed",
        str(seed),
        "--output",
        "<requested-output>",
    ]
    _write_evidence(
        output,
        summary,
        case_results,
        started_at,
        finished_at,
        exit_code,
        argv,
    )
    return exit_code


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--expected-commit", required=True)
    parser.add_argument("--seed", required=True, type=int)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    try:
        return reproduce(args.expected_commit, args.seed, args.output)
    except (OSError, RuntimeError, ValueError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
