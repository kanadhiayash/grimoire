#!/usr/bin/env python3
"""Execute the public, non-mutating Grimoire command smoke."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from grimoire.zeref.profile import build_profile_v2  # noqa: E402
from grimoire.zeref.receipt import (  # noqa: E402
    receipt_integrity_hash,
    zeref_profile_hash,
)


def _sha256(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _run(command_id: str, argv: list[str]) -> dict[str, Any]:
    environment = None
    if command_id == "full-check-json":
        environment = dict(os.environ)
        environment["GRIMOIRE_DOC_SMOKE_ACTIVE"] = "1"
    completed = subprocess.run(
        argv,
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
        env=environment,
    )
    return {
        "id": command_id,
        "argv": argv,
        "exit_code": completed.returncode,
        "status": "PASS" if completed.returncode == 0 else "FAIL",
        "stdout_sha256": _sha256(completed.stdout),
        "stderr_sha256": _sha256(completed.stderr),
    }


def _write_zeref_fixture(directory: Path) -> tuple[Path, Path]:
    profile = build_profile_v2(
        {
            "plan_id": "GRM-DOC-SMOKE-001",
            "plan_revision": 1,
            "project_repository": "local/grimoire-doc-smoke",
            "project_commit": "a" * 40,
            "approved_scope": ["docs/example.md"],
            "excluded_scope": ["deploy", "publish"],
            "permitted_tools": ["filesystem-read", "test-runner"],
            "prohibited_tools": ["network", "credential-store"],
            "approval_required_for": [
                "merge",
                "deploy",
                "publish",
                "external_send",
                "destructive_change",
                "credential_change",
                "canonical_memory_write",
            ],
            "retry_ceiling": 0,
            "receipt_expiry_seconds": 3600,
            "cost_limit": {"amount": 0, "currency": "USD"},
        },
        pack_hash="b" * 64,
        required_controls=("GRM-UNI-001",),
        required_documents=("Verification report",),
        acceptance_criteria=("Command exits zero",),
        stop_conditions=("missing evidence",),
        grimoire_version=(ROOT / "VERSION").read_text(encoding="utf-8").strip(),
        mode="standard",
        cost_ceiling="zero",
    ).to_dict()
    receipt: dict[str, Any] = {
        "schema_id": "grimoire.zeref.receipt.v1",
        "schema_version": "1.0",
        "profile_hash": zeref_profile_hash(profile),
        "pack_hash": profile["pack_hash"],
        "plan": {"id": "GRM-DOC-SMOKE-001", "revision": 1},
        "project": {
            "repository": "local/grimoire-doc-smoke",
            "commit_before": "a" * 40,
            "commit_after": "c" * 40,
            "branch": "docs/smoke",
        },
        "roles": [{"name": "Documentation Verifier", "kind": "lead"}],
        "models": [
            {"requested": "lowest-cost-capable", "actual": "NOT_OBSERVABLE"}
        ],
        "tools": ["filesystem-read", "test-runner"],
        "commands": ["python3 scripts/verify_documented_commands.py --json"],
        "files_changed": ["docs/example.md"],
        "tests": [
            {
                "name": "documented-command-smoke",
                "result": "PASS",
                "evidence_id": "EVD-DOC-001",
            }
        ],
        "evidence": [
            {
                "id": "EVD-DOC-001",
                "control_id": "GRM-UNI-001",
                "subject_commit": "c" * 40,
                "command": "python3 scripts/verify_documented_commands.py --json",
                "result": "PASS",
                "timestamp": "2026-07-30T18:00:00+00:00",
                "reviewer": "Documentation Verifier",
            }
        ],
        "approvals": [],
        "retries": 0,
        "cost": {
            "amount": 0,
            "currency": "USD",
            "ceiling_status": "WITHIN_CEILING",
        },
        "stop_events": [],
        "completion_status": "PASS",
        "memory_proposals": [],
        "external_actions": [],
        "timestamp": "2026-07-30T18:00:00+00:00",
        "expires_at": "2026-07-30T19:00:00+00:00",
        "runtime": {
            "harness": "documentation-smoke",
            "zeref_layer": "contract-fixture",
            "capability": "LOCAL_HARNESS_EXECUTION",
        },
    }
    receipt["integrity"] = {
        "algorithm": "sha256-canonical-json-v1",
        "digest": receipt_integrity_hash(receipt),
    }
    profile_path = directory / "zeref-profile.json"
    receipt_path = directory / "zeref-receipt.json"
    profile_path.write_text(
        json.dumps(profile, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    receipt_path.write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return profile_path, receipt_path


def execute() -> dict[str, Any]:
    commands: list[dict[str, Any]] = []
    artifacts = ROOT / "artifacts"
    artifacts.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(
        dir=artifacts,
        prefix="grimoire-doc-smoke-",
    ) as directory:
        workspace = Path(directory)
        pack = workspace / "project-pack"
        benchmark = workspace / "benchmark"
        browser_pack = workspace / "browser-pack"
        check_output = workspace / "grimoire-check.json"
        release_output = workspace / "release-evidence.json"
        commit = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        ).stdout.strip()
        commands.extend(
            [
                _run(
                    "status",
                    [sys.executable, "scripts/grimoire.py", "status", "--json"],
                ),
                _run(
                    "catalog",
                    [sys.executable, "scripts/grimoire.py", "catalog", "--json"],
                ),
                _run(
                    "doctor",
                    [sys.executable, "scripts/grimoire.py", "doctor"],
                ),
                _run(
                    "project-boot",
                    [
                        sys.executable,
                        "scripts/grimoire.py",
                        "project",
                        "boot",
                        "--manifest",
                        "templates/project/project.json",
                        "--output",
                        str(pack),
                        "--deterministic",
                        "--generated-at",
                        "2026-01-01T00:00:00+00:00",
                    ],
                ),
                _run(
                    "project-verify",
                    [
                        sys.executable,
                        "scripts/grimoire.py",
                        "project",
                        "verify",
                        "--directory",
                        str(pack),
                        "--mode",
                        "offline",
                    ],
                ),
            ]
        )
        trace_path = pack / "CONTROL_TRACE.json"
        if trace_path.is_file():
            trace = json.loads(trace_path.read_text(encoding="utf-8"))
            first_standard = trace["controls"][0]["standard_id"]
            commands.append(
                _run(
                    "project-explain",
                    [
                        sys.executable,
                        "scripts/grimoire.py",
                        "project",
                        "explain",
                        "--directory",
                        str(pack),
                        "--standard-id",
                        first_standard,
                        "--json",
                    ],
                )
            )
        else:
            commands.append(
                {
                    "id": "project-explain",
                    "argv": [],
                    "exit_code": 2,
                    "status": "FAIL",
                    "stdout_sha256": _sha256(""),
                    "stderr_sha256": _sha256("project pack missing"),
                }
            )
        commands.append(
            _run(
                "benchmark-run",
                [
                    sys.executable,
                    "scripts/grimoire.py",
                    "benchmark",
                    "run",
                    "--suite",
                    "benchmarks/suites/runner-smoke.json",
                    "--output",
                    str(benchmark),
                    "--commit",
                    commit,
                ],
            )
        )
        commands.extend(
            [
                _run(
                    "browser-pack-compile",
                    [
                        sys.executable,
                        "scripts/grimoire.py",
                        "pack",
                        "compile",
                        "--surface",
                        "chatgpt-project",
                        "--project-name",
                        "Documentation Smoke",
                        "--output",
                        str(browser_pack),
                        "--grimoire-commit",
                        commit,
                        "--zeref-commit",
                        "f" * 40,
                    ],
                ),
                _run(
                    "browser-pack-verify",
                    [
                        sys.executable,
                        "scripts/grimoire.py",
                        "pack",
                        "verify",
                        str(browser_pack),
                    ],
                ),
            ]
        )
        profile_path, receipt_path = _write_zeref_fixture(workspace)
        commands.append(
            _run(
                "zeref-receipt",
                [
                    sys.executable,
                    "scripts/grimoire.py",
                    "zeref",
                    "verify-receipt",
                    "--profile",
                    str(profile_path),
                    "--receipt",
                    str(receipt_path),
                    "--now",
                    "2026-07-30T18:30:00+00:00",
                ],
            )
        )
        commands.append(
            _run(
                "full-check-json",
                [
                    sys.executable,
                    "scripts/grimoire.py",
                    "check",
                    "--json-output",
                    str(check_output),
                ],
            )
        )
        commands.extend(
            [
                _run(
                    "release-evidence-generate",
                    [
                        sys.executable,
                        "scripts/release_evidence.py",
                        "generate",
                        "--artifact",
                        str(check_output.relative_to(ROOT)),
                        "--benchmark",
                        str(
                            (
                                benchmark / "BENCHMARK_RESULTS.json"
                            ).relative_to(ROOT)
                        ),
                        "--expected-sha",
                        commit,
                        "--timestamp",
                        datetime.now(timezone.utc).isoformat(),
                        "--output",
                        str(release_output),
                    ],
                ),
                _run(
                    "release-evidence-verify",
                    [
                        sys.executable,
                        "scripts/release_evidence.py",
                        "verify",
                        "--evidence",
                        str(release_output),
                        "--expected-sha",
                        commit,
                    ],
                ),
                _run(
                    "release-rollback-dry-run",
                    [
                        sys.executable,
                        "scripts/release_evidence.py",
                        "rollback-dry-run",
                        "--evidence",
                        str(release_output),
                        "--expected-sha",
                        commit,
                    ],
                ),
            ]
        )
    return {
        "schema_version": 1,
        "status": (
            "PASS"
            if all(item["status"] == "PASS" for item in commands)
            else "FAIL"
        ),
        "commands": commands,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = execute()
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        for command in result["commands"]:
            print(f"{command['status']:5} {command['id']}")
        print(f"\nDocumented command smoke: {result['status']}")
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
