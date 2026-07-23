#!/usr/bin/env python3
"""Install, verify, or remove managed cross-harness activation fragments."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
START = "<!-- engineering-standards:zeref-activation:start -->"
END = "<!-- engineering-standards:zeref-activation:end -->"
SURFACES = {
    "claude": {
        "command": "claude",
        "target": ".claude/CLAUDE.md",
        "source": "adapters/claude/ZEREF_ACTIVATION.global.md",
    },
    "codex": {
        "command": "codex",
        "target": ".codex/AGENTS.md",
        "source": "adapters/codex/ZEREF_ACTIVATION.global.md",
    },
    "gemini": {
        "command": "gemini",
        "target": ".gemini/GEMINI.md",
        "source": "adapters/gemini/ZEREF_ACTIVATION.global.md",
    },
}


def block(source: Path) -> str:
    return f"{START}\n{source.read_text(encoding='utf-8').rstrip()}\n{END}"


def merge(text: str, managed: str) -> str:
    if START in text and END in text:
        before, rest = text.split(START, 1)
        _, after = rest.split(END, 1)
        return before.rstrip() + "\n\n" + managed + after
    return text.rstrip() + ("\n\n" if text.strip() else "") + managed + "\n"


def remove(text: str) -> str:
    if START not in text or END not in text:
        return text
    before, rest = text.split(START, 1)
    _, after = rest.split(END, 1)
    return (before.rstrip() + "\n" + after.lstrip()).strip() + "\n"


def detect(home: Path) -> dict[str, dict[str, object]]:
    result = {}
    for name, config in SURFACES.items():
        target = home / config["target"]
        result[name] = {
            "command": shutil.which(config["command"]),
            "target": str(target),
            "target_exists": target.exists(),
            "managed_block": target.exists()
            and START in target.read_text(encoding="utf-8", errors="replace"),
        }
    return result


def apply(home: Path, dry_run: bool) -> list[str]:
    actions: list[str] = []
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    for name, config in SURFACES.items():
        target = home / config["target"]
        source = ROOT / config["source"]
        current = target.read_text(encoding="utf-8") if target.exists() else ""
        updated = merge(current, block(source))
        actions.append(f"{name}: update {target}")
        if dry_run:
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists():
            backup = target.with_name(target.name + f".backup.{timestamp}")
            shutil.copy2(target, backup)
        target.write_text(updated, encoding="utf-8")
    return actions


def uninstall(home: Path, dry_run: bool) -> list[str]:
    actions: list[str] = []
    for name, config in SURFACES.items():
        target = home / config["target"]
        if not target.exists():
            continue
        current = target.read_text(encoding="utf-8")
        updated = remove(current)
        actions.append(f"{name}: remove managed block from {target}")
        if not dry_run:
            target.write_text(updated, encoding="utf-8")
    return actions


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "action",
        choices=[
            "detect",
            "plan",
            "apply",
            "verify",
            "uninstall",
            "export-browser-pack",
        ],
    )
    parser.add_argument("--home", default=str(Path.home()))
    parser.add_argument("--surface")
    parser.add_argument("--project-name")
    parser.add_argument("--output")
    parser.add_argument("--engineering-standards-commit")
    parser.add_argument("--zeref-commit")
    args = parser.parse_args()
    home = Path(args.home).expanduser().resolve()

    if args.action == "detect":
        print(json.dumps(detect(home), indent=2))
        return 0
    if args.action == "plan":
        print("\n".join(apply(home, dry_run=True)))
        return 0
    if args.action == "apply":
        print("\n".join(apply(home, dry_run=False)))
        return 0
    if args.action == "verify":
        state = detect(home)
        failures = [name for name, item in state.items() if not item["managed_block"]]
        print(json.dumps(state, indent=2))
        return 1 if failures else 0
    if args.action == "uninstall":
        print("\n".join(uninstall(home, dry_run=False)))
        return 0

    required = [
        args.surface,
        args.project_name,
        args.output,
        args.engineering_standards_commit,
        args.zeref_commit,
    ]
    if not all(required):
        parser.error(
            "export-browser-pack requires --surface, --project-name, --output, "
            "--engineering-standards-commit, and --zeref-commit"
        )
    command = [
        sys.executable,
        str(ROOT / "scripts" / "compile_surface_pack.py"),
        "--surface",
        args.surface,
        "--project-name",
        args.project_name,
        "--output",
        args.output,
        "--engineering-standards-commit",
        args.engineering_standards_commit,
        "--zeref-commit",
        args.zeref_commit,
    ]
    return subprocess.run(command, check=False).returncode


if __name__ == "__main__":
    raise SystemExit(main())
