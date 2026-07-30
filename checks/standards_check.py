#!/usr/bin/env python3
"""Dependency-free conformance checks for Grimoire."""

from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from grimoire.registry import RegistryValidationError, load_standard_registry  # noqa: E402

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
    "policies/ai-operations.json",
    "policies/schemas/ai-operations.schema.json",
    "policies/schemas/predicates/predicate.schema.json",
    "policies/schemas/control-trace.schema.json",
    "policies/schemas/exclusions.schema.json",
    "policies/schemas/conflict-report.schema.json",
    "policies/schemas/standards/standard-registry-record.schema.json",
    "requirements/ci-schema.txt",
    "checks/json_schema_check.py",
    "profiles/minimal.json",
    "profiles/standard.json",
    "profiles/hardened.json",
    "profiles/public-portfolio.json",
    "standards/ai-development/ai-operations-governance.md",
    "docs/architecture/0002-ai-operations-control-plane.md",
    "docs/architecture/0010-runtime-schema-validation.md",
    "docs/architecture/0011-declarative-predicate-language.md",
    "docs/architecture/0017-applicability-resolution.md",
    "docs/architecture/0018-control-trace-evidence.md",
    "docs/adapters/ai-operations-adapter-contract.md",
    "templates/ai-operations/mission-packet.md",
    "templates/ai-operations/approval-record.md",
    "templates/ai-operations/run-report.md",
    "templates/ai-operations/cross-harness-handoff.md",
    "templates/ai-operations/escalation-packet.md",
    "scripts/doctor.sh",
    "scripts/test.sh",
    "registry/standards/GRIM-STD-0001.json",
    "registry/standards/GRIM-STD-0002.json",
    "registry/standards/GRIM-STD-0003.json",
    "registry/standards/GRIM-STD-0004.json",
    "registry/standards/GRIM-STD-0005.json",
    "src/grimoire/predicates/__init__.py",
    "src/grimoire/predicates/engine.py",
    "src/grimoire/applicability/__init__.py",
    "src/grimoire/applicability/resolver.py",
    "src/grimoire/evidence/__init__.py",
    "src/grimoire/evidence/project_trace.py",
    "scripts/project_explain.py",
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

AI_COMMANDS = {
    "activate",
    "ingest",
    "resume",
    "audit",
    "council",
    "plan",
    "lock",
    "approve",
    "execute",
    "verify",
    "ship",
    "handoff",
    "park",
    "promote_memory",
    "halt",
}

AI_AUTONOMY_LEVELS = {"0", "1", "2", "3", "4", "5"}
AI_COMPLETION_STATUSES = [
    "PASS",
    "PARTIAL",
    "BLOCKED",
    "NOT_VERIFIED",
]
AI_MEMORY_LIFECYCLE = [
    "raw",
    "candidate",
    "validated",
    "approved",
    "canonical",
]

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


def version_tuple(value: str) -> tuple[int, int, int]:
    return tuple(int(part) for part in value.split("."))


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
    baseline_version = baseline.get("standard_version")

    if baseline_version != version:
        return CheckResult(
            "semantic version",
            False,
            f"VERSION is {version}, baseline is {baseline_version!r}",
        )

    components = {
        "ai_operations": (
            load_json("policies/ai-operations.json").get("standard_version"),
            baseline.get("ai_operations", {}).get("policy_version"),
        ),
        "surface_activation": (
            load_json("policies/surface-activation.json").get("standard_version"),
            baseline.get("surface_activation", {}).get("policy_version"),
        ),
    }
    errors: list[str] = []
    root_version = version_tuple(version)

    for name, (actual, declared) in components.items():
        if not isinstance(actual, str) or not SEMVER.fullmatch(actual):
            errors.append(f"{name} has invalid version {actual!r}")
            continue
        if declared != actual:
            errors.append(
                f"baseline declares {name} {declared!r}, policy is {actual!r}"
            )
        if version_tuple(actual) > root_version:
            errors.append(
                f"{name} version {actual} cannot exceed repository version {version}"
            )

    if errors:
        return CheckResult("semantic version", False, "; ".join(errors))

    detail = ", ".join(
        f"{name}={actual}" for name, (actual, _) in components.items()
    )
    return CheckResult("semantic version", True, f"repository={version}; {detail}")


def check_json_documents() -> CheckResult:
    paths = sorted((ROOT / "policies").rglob("*.json"))
    paths += sorted((ROOT / "profiles").rglob("*.json"))
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
            errors.append(f"{path.name}: invalid inherits path {inherited!r}")

    if errors:
        return CheckResult("profiles", False, "; ".join(errors))

    return CheckResult("profiles", True, "inheritance paths resolve")


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
    missing = [path for path in REQUIRED_ADAPTERS if not (ROOT / path).is_file()]

    if missing:
        return CheckResult("harness adapters", False, ", ".join(missing))

    return CheckResult(
        "harness adapters",
        True,
        f"{len(REQUIRED_ADAPTERS)} present",
    )


def check_ai_operations_policy() -> CheckResult:
    policy = load_json("policies/ai-operations.json")
    errors: list[str] = []

    commands = policy.get("commands")
    if not isinstance(commands, dict):
        errors.append("commands must be an object")
    else:
        missing_commands = AI_COMMANDS - set(commands)
        extra_commands = set(commands) - AI_COMMANDS
        if missing_commands:
            errors.append(
                "missing commands: " + ", ".join(sorted(missing_commands))
            )
        if extra_commands:
            errors.append(
                "unknown commands: " + ", ".join(sorted(extra_commands))
            )

        escalating = [
            name
            for name, config in commands.items()
            if isinstance(config, dict) and config.get("may_escalate") is True
        ]
        if escalating:
            errors.append(
                "commands may not silently escalate: "
                + ", ".join(sorted(escalating))
            )

    autonomy = policy.get("autonomy_levels")
    if not isinstance(autonomy, dict) or set(autonomy) != AI_AUTONOMY_LEVELS:
        errors.append("autonomy levels must be exactly 0 through 5")

    if policy.get("completion_statuses") != AI_COMPLETION_STATUSES:
        errors.append("completion statuses do not match the canonical set")

    memory = policy.get("memory")
    if not isinstance(memory, dict):
        errors.append("memory must be an object")
    else:
        if memory.get("single_writer_required") is not True:
            errors.append("memory must require a single writer")
        if memory.get("lifecycle") != AI_MEMORY_LIFECYCLE:
            errors.append("memory lifecycle does not match the canonical order")
        if memory.get("two_strikes_for_permanent_rules") is not True:
            errors.append("Two-Strikes Rule must be enabled")

    approval = policy.get("approval")
    if not isinstance(approval, dict):
        errors.append("approval must be an object")
    else:
        for key in (
            "plan_id_required",
            "revision_required",
            "approved_scope_required",
            "material_revision_invalidates_approval",
        ):
            if approval.get(key) is not True:
                errors.append(f"approval.{key} must be true")

    if errors:
        return CheckResult("AI operations policy", False, "; ".join(errors))

    return CheckResult(
        "AI operations policy",
        True,
        f"{len(AI_COMMANDS)} commands, 6 autonomy levels",
    )


def check_standard_registry() -> CheckResult:
    try:
        records = load_standard_registry(ROOT / "registry" / "standards", root=ROOT)
    except RegistryValidationError as exc:
        return CheckResult(
            "standard registry",
            False,
            ", ".join(exc.reason_codes),
        )

    return CheckResult(
        "standard registry",
        True,
        f"{len(records)} normative records",
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
    aws = "A" + "KIA" + r"[0-9A-Z]{16}"
    github = "gh" + r"[pousr]_[A-Za-z0-9_]{30,}"
    openai = r"(?<![A-Za-z0-9])" + "s" + "k-" + r"[A-Za-z0-9_-]{20,}"
    private_key = "-----BEGIN " + r"(?:RSA |EC |OPENSSH )?PRIVATE KEY-----"
    mongodb = "mongodb" + r"(?:\+srv)?://[^:\s/]+:[^@\s/]+@"

    return tuple(
        re.compile(pattern)
        for pattern in (aws, github, openai, private_key, mongodb)
    )


def check_secrets() -> CheckResult:
    findings: list[str] = []
    patterns = secret_patterns()

    for path in iter_text_files():
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue

        for line_number, line in enumerate(text.splitlines(), start=1):
            if any(pattern.search(line) for pattern in patterns):
                findings.append(f"{path.relative_to(ROOT)}:{line_number}")

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
        check_ai_operations_policy,
        check_standard_registry,
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

    print("Grimoire Doctor")
    print("============================")

    for result in results:
        status = "PASS" if result.passed else "FAIL"
        print(f"{status:4}  {result.name}: {result.detail}")

    failed = [result for result in results if not result.passed]

    print()

    if failed:
        print(f"Grimoire Doctor: FAIL ({len(failed)} failed)")
        return 1

    print("Grimoire Doctor: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
