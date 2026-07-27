#!/usr/bin/env python3
"""Unified human and agent command surface for Product Engineering Standards."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Sequence

ROOT = Path(__file__).resolve().parents[1]


def load_index(root: Path = ROOT) -> dict[str, Any]:
    with (root / "REPOSITORY_INDEX.json").open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError("REPOSITORY_INDEX.json must contain a JSON object")
    return value


def _entrypoint_paths(index: dict[str, Any]) -> list[str]:
    entrypoints = index.get("entrypoints", {})
    if not isinstance(entrypoints, dict):
        return []
    result: list[str] = []
    for values in entrypoints.values():
        if isinstance(values, list):
            result.extend(value for value in values if isinstance(value, str))
    return sorted(set(result))


def build_status(root: Path = ROOT) -> dict[str, Any]:
    index = load_index(root)
    version = (root / "VERSION").read_text(encoding="utf-8").strip()
    entrypoints = _entrypoint_paths(index)
    missing = [path for path in entrypoints if not (root / path).exists()]
    index_version = index.get("standard_version")
    healthy = index_version == version and not missing
    return {
        "repository": index.get("repository"),
        "display_name": index.get("display_name"),
        "future_name": index.get("future_name"),
        "standard_version": version,
        "index_version": index_version,
        "index_matches_version": index_version == version,
        "entrypoints": entrypoints,
        "missing_entrypoints": missing,
        "surface_count": len(index.get("surfaces", {})) if isinstance(index.get("surfaces"), dict) else 0,
        "command_count": len(index.get("commands", {})) if isinstance(index.get("commands"), dict) else 0,
        "health": "PASS" if healthy else "PARTIAL",
    }


def run_steps(steps: Sequence[tuple[str, Sequence[str]]], root: Path = ROOT) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for name, command in steps:
        completed = subprocess.run(list(command), cwd=root, text=True, capture_output=True, check=False)
        results.append({"name": name, "command": list(command), "exit_code": completed.returncode, "stdout": completed.stdout, "stderr": completed.stderr, "status": "PASS" if completed.returncode == 0 else "FAIL"})
    return results


def build_pack_command(*, surface: str, project_name: str, output: str, engineering_standards_commit: str, zeref_commit: str, overwrite: bool = False) -> list[str]:
    command = [sys.executable, "scripts/compile_surface_pack.py", "--surface", surface, "--project-name", project_name, "--output", output, "--engineering-standards-commit", engineering_standards_commit, "--zeref-commit", zeref_commit]
    if overwrite:
        command.append("--overwrite")
    return command


def build_harness_command(action: str, *, home: str | None = None) -> list[str]:
    command = [sys.executable, "scripts/install_ai_harness_standards.py", action]
    if home:
        command.extend(["--home", home])
    return command


def build_project_command(*, manifest: str, output: str) -> list[str]:
    return [sys.executable, "scripts/project_orchestrator.py", "--manifest", manifest, "--output", output]


def check_steps() -> list[tuple[str, Sequence[str]]]:
    python = sys.executable
    return [
        ("standards doctor", [python, "checks/standards_check.py"]),
        ("surface activation", [python, "checks/surface_activation_check.py"]),
        ("repository index", [python, "checks/repository_index_check.py"]),
        ("standards orchestrator", [python, "checks/standards_orchestrator_check.py"]),
        ("unit tests", [python, "-m", "unittest", "discover", "-s", "tests", "-p", "test_*.py", "-v"]),
        ("compile", [python, "-m", "compileall", "-q", "checks", "scripts", "tests"]),
    ]


def print_status(status: dict[str, Any], as_json: bool) -> None:
    if as_json:
        print(json.dumps(status, indent=2))
        return
    print(status.get("display_name") or "Product Engineering Standards")
    print(f"Repository: {status['repository']}")
    print(f"Version: {status['standard_version']}")
    print(f"Health: {status['health']}")
    print(f"Commands: {status['command_count']}")
    print(f"Surfaces: {status['surface_count']}")
    if status["missing_entrypoints"]:
        print("Missing entrypoints:")
        for path in status["missing_entrypoints"]:
            print(f"- {path}")


def parser() -> argparse.ArgumentParser:
    value = argparse.ArgumentParser(description=__doc__)
    subparsers = value.add_subparsers(dest="command", required=True)
    status = subparsers.add_parser("status", help="Report repository health")
    status.add_argument("--json", action="store_true")
    catalog = subparsers.add_parser("catalog", help="Print the repository index")
    catalog.add_argument("--json", action="store_true")
    check = subparsers.add_parser("check", help="Run all conformance checks")
    check.add_argument("--json-output")
    subparsers.add_parser("doctor", help="Run policy and index checks")
    subparsers.add_parser("test", help="Run the unit test suite")

    project = subparsers.add_parser("project", help="Compile project standards context")
    project_subparsers = project.add_subparsers(dest="project_action", required=True)
    project_boot = project_subparsers.add_parser("boot", help="Validate a project manifest and compile one context pack")
    project_boot.add_argument("--manifest", required=True)
    project_boot.add_argument("--output", required=True)

    pack = subparsers.add_parser("pack", help="Compile or verify browser packs")
    pack_subparsers = pack.add_subparsers(dest="pack_action", required=True)
    pack_compile = pack_subparsers.add_parser("compile")
    pack_compile.add_argument("--surface", required=True)
    pack_compile.add_argument("--project-name", required=True)
    pack_compile.add_argument("--output", required=True)
    pack_compile.add_argument("--engineering-standards-commit", required=True)
    pack_compile.add_argument("--zeref-commit", required=True)
    pack_compile.add_argument("--overwrite", action="store_true")
    pack_verify = pack_subparsers.add_parser("verify")
    pack_verify.add_argument("directory")

    harness = subparsers.add_parser("harness", help="Manage global harness adapters")
    harness.add_argument("action", choices=["detect", "plan", "apply", "verify", "uninstall"])
    harness.add_argument("--home")
    return value


def main() -> int:
    args = parser().parse_args()
    if args.command == "status":
        print_status(build_status(ROOT), args.json)
        return 0
    if args.command == "catalog":
        print(json.dumps(load_index(ROOT), indent=2))
        return 0
    if args.command == "project":
        command = build_project_command(manifest=args.manifest, output=args.output)
        return subprocess.run(command, cwd=ROOT, check=False).returncode
    if args.command == "pack":
        if args.pack_action == "compile":
            command = build_pack_command(surface=args.surface, project_name=args.project_name, output=args.output, engineering_standards_commit=args.engineering_standards_commit, zeref_commit=args.zeref_commit, overwrite=args.overwrite)
        else:
            command = [sys.executable, "scripts/verify_surface_pack.py", args.directory]
        return subprocess.run(command, cwd=ROOT, check=False).returncode
    if args.command == "harness":
        command = build_harness_command(args.action, home=args.home)
        return subprocess.run(command, cwd=ROOT, check=False).returncode

    steps = check_steps()
    if args.command == "doctor":
        steps = steps[:4]
    elif args.command == "test":
        steps = steps[4:5]
    results = run_steps(steps, ROOT)
    report = {"status": "PASS" if all(item["exit_code"] == 0 for item in results) else "FAIL", "results": results}
    if getattr(args, "json_output", None):
        output = Path(args.json_output).expanduser().resolve()
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    for result in results:
        print(f"{result['status']:4}  {result['name']}")
        if result["stdout"].strip():
            print(result["stdout"].rstrip())
        if result["stderr"].strip():
            print(result["stderr"].rstrip(), file=sys.stderr)
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
