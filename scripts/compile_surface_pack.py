#!/usr/bin/env python3
"""Compile a reproducible browser-project source pack."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_DIR = ROOT / "templates" / "browser-project"
SURFACES = {
    "chatgpt-project": ("chatgpt", "CHATGPT.md", "PROJECT_SIMULATION"),
    "claude-project": ("claude-project", "CLAUDE.md", "PROJECT_SIMULATION"),
    "gemini-gem": ("gemini-gem", "GEMINI.md", "PROJECT_SIMULATION"),
    "generic-chat": ("generic-chat", "PROVIDER_ADAPTER.md", "CHAT_SIMULATION"),
}
SHA = re.compile(r"^[0-9a-f]{40}$")


def render(text: str, values: dict[str, str]) -> str:
    for key, value in values.items():
        text = text.replace("{{" + key + "}}", value)
    return text


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def compile_pack(args: argparse.Namespace) -> Path:
    if not SHA.fullmatch(args.engineering_standards_commit):
        raise ValueError("engineering standards commit must be a 40-character lowercase SHA")
    if not SHA.fullmatch(args.zeref_commit):
        raise ValueError("Zeref commit must be a 40-character lowercase SHA")

    provider_dir, adapter_name, activation_mode = SURFACES[args.surface]
    output = Path(args.output).expanduser().resolve()
    if output.exists() and any(output.iterdir()) and not args.overwrite:
        raise FileExistsError(f"{output} is not empty; use --overwrite")
    output.mkdir(parents=True, exist_ok=True)

    generated_at = args.generated_at or datetime.now(timezone.utc).isoformat()
    values = {
        "PROJECT_NAME": args.project_name,
        "SURFACE": args.surface,
        "PACK_VERSION": args.pack_version,
        "GENERATED_AT": generated_at,
        "ENGINEERING_STANDARDS_COMMIT": args.engineering_standards_commit,
        "ZEREF_COMMIT": args.zeref_commit,
        "ACTIVATION_MODE": activation_mode,
    }

    for source in TEMPLATE_DIR.iterdir():
        if source.name == "SOURCES_MANIFEST.json":
            continue
        target = output / source.name
        target.write_text(
            render(source.read_text(encoding="utf-8"), values), encoding="utf-8"
        )

    adapter_source = ROOT / "adapters" / provider_dir / adapter_name
    shutil.copyfile(adapter_source, output / "PROVIDER_ADAPTER.md")

    manifest_template = json.loads(
        (TEMPLATE_DIR / "SOURCES_MANIFEST.json").read_text(encoding="utf-8")
    )

    def render_value(value):
        if isinstance(value, str):
            return render(value, values)
        if isinstance(value, list):
            return [render_value(item) for item in value]
        if isinstance(value, dict):
            return {key: render_value(item) for key, item in value.items()}
        return value

    manifest = render_value(manifest_template)
    manifest["files"] = {
        path.name: {"sha256": digest(path), "bytes": path.stat().st_size}
        for path in sorted(output.iterdir())
        if path.name != "SOURCES_MANIFEST.json"
    }
    (output / "SOURCES_MANIFEST.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )
    return output


def parser() -> argparse.ArgumentParser:
    value = argparse.ArgumentParser()
    value.add_argument("--surface", required=True, choices=sorted(SURFACES))
    value.add_argument("--project-name", required=True)
    value.add_argument("--output", required=True)
    value.add_argument("--engineering-standards-commit", required=True)
    value.add_argument("--zeref-commit", required=True)
    value.add_argument("--pack-version", default="1.0.0")
    value.add_argument("--generated-at")
    value.add_argument("--overwrite", action="store_true")
    return value


def main() -> int:
    args = parser().parse_args()
    output = compile_pack(args)
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
