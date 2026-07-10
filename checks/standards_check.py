#!/usr/bin/env python3
"""Dependency-free conformance checks for Engineering Standards."""

from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parents[1]
SEMVER = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+$")

REQUIRED_FILES = (
    "README.md",
    "AGENTS.md",
    "VERSION",
    "CHANGELOG.md",
    "GOVERNANCE.md",
    "SECURITY.md",
    "CONTRIBUTING.md",
    "LICENSE",
    ".gitignore",
    ".editorconfig",
    "Makefile",
    "policies/schema.json",
    "policies/baseline.json",
    "profiles/minimal.json",
    "profiles/standard.json",
    "profiles/hardened.json",
    "profiles/public-portfolio.json",
    "scripts/doctor.sh",
    "scripts/test.sh",
    ".github/workflows/standards-ci.yml",
    ".github/CODEOWNERS",
)

REQUIRED_STANDARD_AREAS = (
    "standards/universal",
    "standards/engineering",
    "standards/github",
    "standards/ai-development",
    "standards/product-ux",
    "standards/stacks",
)

REQUIRED_ADAPTERS = (
    "adapters/codex/AGENTS.overlay.md",
    "adapters/claude/CLAUDE.overlay.md",
    "adapters/cursor/rules.md",
    "adapters/github-copilot/copilot-instructions.md",
    "adapters/gemini/GEMINI.overlay.md",
    "adapters/generic/SYSTEM_PROMPT.md",
)

TEXT_SUFFIXES = {
    ".md",
    ".txt",
    ".json",
    ".yaml",
    ".yml",
    ".toml",
    ".py",
    ".sh",
    ".js",
    ".ts",
    ".tsx",
    ".swift",
}


@dataclass(frozen=True)
class CheckResult:
    name: str
    passed: bool
    detail: str


def load_json(relative_path: str) -> dict:
    path = ROOT / relative_path
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)

    if not isinstance(value, dict):
        raise ValueError(f"{relative_path} must contain a JSON object")

    return value


def check_required_files() -> CheckResult:
    missing = [path for path in REQUIRED_FILES if not (ROOT / path).is_file()]

    if missing:
        return CheckResult("required files", False, ", ".join(missing))

    return CheckResult("required files", True, f"{len(REQUIRED_FILES)} present")


def check_version() -> CheckResult:
    version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()

    if not SEMVER.fullmatch(version):
        return CheckResult(
            "semantic version",
            False,
            f"invalid VERSION: {version!r}",
        )

    baseline = load_json("policies/baseline.json")
    policy_version = baseline.get("standard_version")

    if policy_version != version:
        return CheckResult(
            "semantic version",
            False,
            f"VERSION is {version}, baseline is {policy_version!r}",
        )

    return CheckResult("semantic version", True, version)


def check_json_documents() -> CheckResult:
    paths = sorted((ROOT / "policies").glob("*.json"))
    paths += sorted((ROOT / "profiles").glob("*.json"))

    errors: list[str] = []

    for path in paths:
        try:
            with path.open("r", encoding="utf-8") as handle:
                value = json.load(handle)

            if not isinstance(value, dict):
                errors.append(f"{path.relative_to(ROOT)} is not an object")
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"{path.relative_to(ROOT)}: {exc}")

    if errors:
        return CheckResult("JSON documents", False, "; ".join(errors))

    return CheckResult("JSON documents", True, f"{len(paths)} parsed")


def check_profiles() -> CheckResult:
    errors: list[str] = []

    for path in sorted((ROOT / "profiles").glob("*.json")):
        data = load_json(str(path.relative_to(ROOT)))

        if data.get("name") != path.stem:
            errors.append(f"{path.name}: name must be {path.stem!r}")

        inherited = data.get("inherits")

        if not isinstance(inherited, str) or not (ROOT / inherited).is_file():
            errors.append(
                f"{path.name}: invalid inherits path {inherited!r}"
            )

    if errors:
        return CheckResult("profiles", False, "; ".join(errors))

    return CheckResult(
        "profiles",
        True,
        "inheritance paths resolve",
    )


def check_standard_areas() -> CheckResult:
    empty: list[str] = []

    for relative in REQUIRED_STANDARD_AREAS:
        directory = ROOT / relative

        if not directory.is_dir() or not any(directory.glob("*.md")):
            empty.append(relative)

    if empty:
        return CheckResult("standard areas", False, ", ".join(empty))

    return CheckResult(
        "standard areas",
        True,
        f"{len(REQUIRED_STANDARD_AREAS)} populated",
    )


def check_adapters() -> CheckResult:
    missing = [
        path
        for path in REQUIRED_ADAPTERS
        if not (ROOT / path).is_file()
    ]

    if missing:
        return CheckResult("harness adapters", False, ", ".join(missing))

    return CheckResult(
        "harness adapters",
        True,
        f"{len(REQUIRED_ADAPTERS)} present",
    )


def iter_text_files() -> Iterable[Path]:
    excluded_parts = {
        ".git",
        ".venv",
        "venv",
        "node_modules",
        "__pycache__",
    }

    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue

        if any(part in excluded_parts for part in path.parts):
            continue

        if path.suffix.lower() in TEXT_SUFFIXES or path.name in {
            "VERSION",
            "Makefile",
            "LICENSE",
            ".gitignore",
            ".editorconfig",
        }:
            yield path


def secret_patterns() -> tuple[re.Pattern[str], ...]:
    # Assemble markers so this checker does not match its own source text.
    aws = "A" + "KIA" + r"[0-9A-Z]{16}"
    github = "gh" + r"[pousr]_[A-Za-z0-9_]{30,}"
    openai = "s" + "k-" + r"[A-Za-z0-9_-]{20,}"
    private_key = (
        "-----BEGIN "
        + r"(?:RSA |EC |OPENSSH )?PRIVATE KEY-----"
    )
    mongodb = (
        "mongodb"
        + r"(?:\+srv)?://[^:\s/]+:[^@\s/]+@"
    )

    return tuple(
        re.compile(pattern)
        for pattern in (
            aws,
            github,
            openai,
            private_key,
            mongodb,
        )
    )


def check_secrets() -> CheckResult:
    findings: list[str] = []
    patterns = secret_patterns()

    for path in iter_text_files():
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue

        for line_number, line in enumerate(
            text.splitlines(),
            start=1,
        ):
            if any(pattern.search(line) for pattern in patterns):
                findings.append(
                    f"{path.relative_to(ROOT)}:{line_number}"
                )

    if findings:
        return CheckResult(
            "high-confidence secret scan",
            False,
            ", ".join(findings),
        )

    return CheckResult(
        "high-confidence secret scan",
        True,
        "no matches",
    )


def run_checks() -> list[CheckResult]:
    checks = (
        check_required_files,
        check_version,
        check_json_documents,
        check_profiles,
        check_standard_areas,
        check_adapters,
        check_secrets,
    )

    results: list[CheckResult] = []

    for check in checks:
        try:
            results.append(check())
        except Exception as exc:
            results.append(
                CheckResult(
                    check.__name__,
                    False,
                    f"{type(exc).__name__}: {exc}",
                )
            )

    return results


def main() -> int:
    results = run_checks()

    print("Engineering Standards Doctor")
    print("============================")

    for result in results:
        status = "PASS" if result.passed else "FAIL"
        print(f"{status:4}  {result.name}: {result.detail}")

    failed = [result for result in results if not result.passed]

    print()

    if failed:
        print(
            f"Engineering Standards Doctor: "
            f"FAIL ({len(failed)} failed)"
        )
        return 1

    print("Engineering Standards Doctor: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
