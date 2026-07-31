#!/usr/bin/env python3
"""Validate non-cyber CI governance and dependency boundaries."""

from __future__ import annotations

import argparse
import ast
import json
import os
import re
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ACTION_SHA = re.compile(r"^[^@\s]+@[0-9a-f]{40}$")
ACTION_LINE = re.compile(
    r"^\s*(?:-\s*)?uses:\s*(\S+)\s*(?:#.*)?$"
)
PACKAGE_LINE = re.compile(r"^([A-Za-z0-9_.-]+)==[^\s\\]+")
HASH_LINE = re.compile(r"--hash=sha256:[0-9a-f]{64}")


def is_immutable_action_reference(reference: str) -> bool:
    if reference.startswith("./"):
        return True
    if reference.startswith("docker://"):
        return "@sha256:" in reference
    return ACTION_SHA.fullmatch(reference) is not None


def _git(root: Path, *arguments: str) -> str:
    completed = subprocess.run(
        ["git", *arguments],
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode != 0:
        return "NOT_VERIFIED"
    return completed.stdout.strip()


def _workflow_findings(
    root: Path,
) -> tuple[list[dict[str, str]], list[str], int]:
    findings: list[dict[str, str]] = []
    workflows: list[str] = []
    action_count = 0
    for path in sorted((root / ".github" / "workflows").glob("*.yml")):
        relative = str(path.relative_to(root))
        workflows.append(relative)
        text = path.read_text(encoding="utf-8")
        if "permissions:\n  contents: read" not in text:
            findings.append(
                {
                    "code": "workflow_permissions_not_read_only",
                    "path": relative,
                }
            )
        if re.search(r"continue-on-error:\s*true", text):
            findings.append(
                {
                    "code": "workflow_failure_suppressed",
                    "path": relative,
                }
            )
        if re.search(r"\|\|\s*true(?:\s|$)", text):
            findings.append(
                {
                    "code": "shell_failure_suppressed",
                    "path": relative,
                }
            )
        for line in text.splitlines():
            match = ACTION_LINE.match(line)
            if not match:
                continue
            action_count += 1
            if not is_immutable_action_reference(match.group(1)):
                findings.append(
                    {
                        "code": "action_reference_not_immutable",
                        "path": relative,
                    }
                )
    if not workflows:
        findings.append({"code": "workflow_set_missing", "path": ".github"})
    return findings, workflows, action_count


def _hashed_dependencies(root: Path) -> tuple[list[dict[str, str]], int]:
    path = root / "requirements" / "ci-schema.txt"
    if not path.is_file():
        return [{"code": "ci_lock_missing", "path": str(path)}], 0
    lines = path.read_text(encoding="utf-8").splitlines()
    findings: list[dict[str, str]] = []
    count = 0
    for index, line in enumerate(lines):
        match = PACKAGE_LINE.match(line.strip())
        if not match:
            continue
        count += 1
        following = "\n".join(lines[index : index + 4])
        if not HASH_LINE.search(following):
            findings.append(
                {
                    "code": "ci_dependency_hash_missing",
                    "path": f"requirements/ci-schema.txt:{index + 1}",
                }
            )
    if count == 0:
        findings.append(
            {
                "code": "ci_dependency_lock_empty",
                "path": "requirements/ci-schema.txt",
            }
        )
    return findings, count


def _runtime_external_imports(root: Path) -> list[str]:
    external: set[str] = set()
    standard = set(sys.stdlib_module_names)
    for path in sorted((root / "src" / "grimoire").rglob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            names: list[str] = []
            if isinstance(node, ast.Import):
                names = [alias.name for alias in node.names]
            elif isinstance(node, ast.ImportFrom) and node.level == 0:
                names = [node.module or ""]
            for name in names:
                top = name.split(".", 1)[0]
                if (
                    top
                    and top not in standard
                    and top not in {"grimoire", "scripts"}
                ):
                    external.add(top)
    return sorted(external)


def evaluate_ci_policy(root: Path = ROOT) -> dict[str, Any]:
    workflow_findings, workflows, action_count = _workflow_findings(root)
    lock_findings, dependency_count = _hashed_dependencies(root)
    external_imports = _runtime_external_imports(root)
    findings = [*workflow_findings, *lock_findings]
    findings.extend(
        {
            "code": "runtime_external_dependency",
            "path": name,
        }
        for name in external_imports
    )
    commit = _git(root, "rev-parse", "HEAD")
    tree = _git(root, "status", "--porcelain", "--untracked-files=no")
    if commit == "NOT_VERIFIED":
        findings.append(
            {"code": "commit_not_verified", "path": ".git"}
        )
    permission_status = (
        "FAIL"
        if any(
            finding["code"] == "workflow_permissions_not_read_only"
            for finding in findings
        )
        else "PASS"
    )
    return {
        "schema_version": 1,
        "status": "PASS" if not findings else "FAIL",
        "commit": commit,
        "tree_state": (
            "NOT_VERIFIED"
            if tree == "NOT_VERIFIED"
            else ("CLEAN" if tree == "" else "DIRTY")
        ),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "workflows": workflows,
        "action_reference_count": action_count,
        "hashed_ci_dependency_count": dependency_count,
        "runtime_external_imports": external_imports,
        "workflow_permissions_status": permission_status,
        "cyber_tooling_status": "NOT_VERIFIED",
        "cyber_tooling_reason": "owner_no_cyber_boundary",
        "findings": sorted(
            findings,
            key=lambda value: (value["path"], value["code"]),
        ),
    }


def _write_json(path: Path, value: dict[str, Any]) -> None:
    if path.is_symlink() or path.parent.is_symlink():
        raise ValueError("CI policy evidence path must not be a symlink")
    path.parent.mkdir(parents=True, exist_ok=True)
    encoded = json.dumps(value, indent=2, sort_keys=True) + "\n"
    temporary_name = ""
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=path.parent,
            prefix=f".{path.name}.",
            suffix=".tmp",
            delete=False,
        ) as temporary:
            temporary.write(encoded)
            temporary.flush()
            os.fsync(temporary.fileno())
            temporary_name = temporary.name
        os.replace(temporary_name, path)
    finally:
        if temporary_name:
            Path(temporary_name).unlink(missing_ok=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json-output")
    args = parser.parse_args()
    try:
        result = evaluate_ci_policy()
        if args.json_output:
            _write_json(Path(args.json_output), result)
    except (OSError, SyntaxError, ValueError) as exc:
        print(
            json.dumps(
                {"status": "FAIL", "error": type(exc).__name__},
                sort_keys=True,
            ),
            file=sys.stderr,
        )
        return 2
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
