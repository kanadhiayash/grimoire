#!/usr/bin/env python3
"""Apply the one-time repository identity migration to Grimoire."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEXT_SUFFIXES = {".md", ".json", ".py", ".yml", ".yaml", ".toml", ".txt", ".sh"}
NEW_SLUG = "kanadhiayash/grimoire"
NEW_URL = "https://github.com/kanadhiayash/grimoire"
VERSION = "0.5.0"


def old_slug() -> str:
    return "kanadhiayash/" + "engineering-standards"


def old_url() -> str:
    return "https://github.com/" + old_slug()


def text_files() -> list[Path]:
    result: list[Path] = []
    for path in ROOT.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        if any(part in {".git", "artifacts", "dist", "__pycache__"} for part in path.parts):
            continue
        result.append(path)
    return sorted(result)


def replace_all(text: str) -> str:
    replacements = (
        (old_url(), NEW_URL),
        (old_slug(), NEW_SLUG),
        ("Product Engineering Standards & Operations", "Grimoire"),
        ("Product Engineering Standards and Operations", "Grimoire"),
        ("Engineering Standards Doctor", "Grimoire Doctor"),
        ("Engineering Standards", "Grimoire"),
        ("engineering_standards", "grimoire"),
        ("ENGINEERING_STANDARDS", "GRIMOIRE"),
        ("engineering-standards-commit", "grimoire-commit"),
        ("engineering-standards:zeref-activation", "grimoire:zeref-activation"),
        ("Standards CI", "Grimoire CI"),
        ("standards-check", "grimoire-check"),
        ("standards doctor", "grimoire doctor"),
        ("# Standards Orchestrator Agent Contract", "# Grimoire Agent Contract"),
        ("future Standards Orchestrator name", "Grimoire identity"),
        ("will later be renamed Standards Orchestrator", "operates as the Standards Orchestrator"),
        ("scripts/standards.py", "scripts/grimoire.py"),
    )
    for before, after in replacements:
        text = text.replace(before, after)
    return text


def write_text(path: Path, text: str, changed: set[str]) -> None:
    old = path.read_text(encoding="utf-8") if path.exists() else None
    if old == text:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    changed.add(str(path.relative_to(ROOT)))


def write_json(path: Path, value: object, changed: set[str]) -> None:
    write_text(path, json.dumps(value, indent=2) + "\n", changed)


def migrate_text(changed: set[str]) -> None:
    for path in text_files():
        if path.name == Path(__file__).name:
            continue
        text = path.read_text(encoding="utf-8")
        write_text(path, replace_all(text), changed)


def migrate_index(changed: set[str]) -> None:
    path = ROOT / "REPOSITORY_INDEX.json"
    index = json.loads(path.read_text(encoding="utf-8"))
    index["standard_version"] = VERSION
    index["repository"] = NEW_SLUG
    index["display_name"] = "Grimoire"
    index.pop("future_name", None)
    index["descriptor"] = "Global Product Engineering Standards Orchestrator"
    index["canonical_url"] = NEW_URL
    index["purpose"] = (
        "Neutral, versioned global product engineering standards and a one-entrypoint "
        "control plane for human, AI, and Zeref-assisted product work."
    )
    write_json(path, index, changed)


def migrate_versions(changed: set[str]) -> None:
    write_text(ROOT / "VERSION", VERSION + "\n", changed)
    path = ROOT / "policies" / "baseline.json"
    baseline = json.loads(path.read_text(encoding="utf-8"))
    baseline["standard_version"] = VERSION
    write_json(path, baseline, changed)


def migrate_manifests(changed: set[str]) -> None:
    root_path = ROOT / "instructions" / "instructions-manifest.json"
    root_manifest = json.loads(root_path.read_text(encoding="utf-8"))
    root_manifest["pack_version"] = "4.0.0"
    sources = root_manifest.setdefault("canonical_sources", {})
    sources.pop("engineering_standards", None)
    sources["grimoire"] = NEW_URL
    write_json(root_path, root_manifest, changed)

    personal_path = ROOT / "instructions" / "personal" / "yash" / "manifest.json"
    personal = json.loads(personal_path.read_text(encoding="utf-8"))
    personal["version"] = "5.0.0"
    personal["canonical_sources"] = {
        "grimoire": NEW_URL,
        "zeref_memory_engine": "https://github.com/kanadhiayash/zeref-memory-engine",
    }
    write_json(personal_path, personal, changed)


def migrate_python_compatibility(changed: set[str]) -> None:
    compile_path = ROOT / "scripts" / "compile_surface_pack.py"
    text = compile_path.read_text(encoding="utf-8")
    text = text.replace(
        'value.add_argument("--grimoire-commit", required=True)',
        'value.add_argument("--grimoire-commit", "--engineering-standards-commit", '
        'dest="grimoire_commit", required=True, help="Pinned Grimoire commit SHA")',
    )
    write_text(compile_path, text, changed)

    standards_path = ROOT / "scripts" / "standards.py"
    text = standards_path.read_text(encoding="utf-8")
    text = text.replace(
        '        "future_name": index.get("future_name"),\n',
        '        "descriptor": index.get("descriptor"),\n'
        '        "canonical_url": index.get("canonical_url"),\n',
    )
    text = text.replace(
        'pack_compile.add_argument("--grimoire-commit", required=True)',
        'pack_compile.add_argument("--grimoire-commit", "--engineering-standards-commit", '
        'dest="grimoire_commit", required=True, help="Pinned Grimoire commit SHA")',
    )
    write_text(standards_path, text, changed)

    install_path = ROOT / "scripts" / "install_ai_harness_standards.py"
    text = install_path.read_text(encoding="utf-8")
    text = text.replace(
        'START = "<!-- grimoire:zeref-activation:start -->"\n'
        'END = "<!-- grimoire:zeref-activation:end -->"\n',
        'START = "<!-- grimoire:zeref-activation:start -->"\n'
        'END = "<!-- grimoire:zeref-activation:end -->"\n'
        'LEGACY_START = "<!-- engineering-standards:zeref-activation:start -->"\n'
        'LEGACY_END = "<!-- engineering-standards:zeref-activation:end -->"\n',
    )
    text = text.replace(
        '    if START in text and END in text:\n'
        '        before, rest = text.split(START, 1)\n'
        '        _, after = rest.split(END, 1)\n'
        '        return before.rstrip() + "\\n\\n" + managed + after\n',
        '    for start, end in ((START, END), (LEGACY_START, LEGACY_END)):\n'
        '        if start in text and end in text:\n'
        '            before, rest = text.split(start, 1)\n'
        '            _, after = rest.split(end, 1)\n'
        '            return before.rstrip() + "\\n\\n" + managed + after\n',
    )
    text = text.replace(
        '    if START not in text or END not in text:\n'
        '        return text\n'
        '    before, rest = text.split(START, 1)\n'
        '    _, after = rest.split(END, 1)\n'
        '    return (before.rstrip() + "\\n" + after.lstrip()).strip() + "\\n"\n',
        '    for start, end in ((START, END), (LEGACY_START, LEGACY_END)):\n'
        '        if start in text and end in text:\n'
        '            before, rest = text.split(start, 1)\n'
        '            _, after = rest.split(end, 1)\n'
        '            return (before.rstrip() + "\\n" + after.lstrip()).strip() + "\\n"\n'
        '    return text\n',
    )
    text = text.replace(
        '            and START in target.read_text(encoding="utf-8", errors="replace"),\n',
        '            and any(marker in target.read_text(encoding="utf-8", errors="replace") '
        'for marker in (START, LEGACY_START)),\n',
    )
    text = text.replace(
        '    parser.add_argument("--grimoire-commit")',
        '    parser.add_argument("--grimoire-commit", "--engineering-standards-commit", '
        'dest="grimoire_commit")',
    )
    write_text(install_path, text, changed)

    verify_path = ROOT / "scripts" / "verify_surface_pack.py"
    text = verify_path.read_text(encoding="utf-8")
    text = text.replace(
        '    for source in ("grimoire", "zeref_memory_engine"):\n'
        '        commit = commits.get(source, {}).get("commit")\n'
        '        if not isinstance(commit, str) or not SHA.fullmatch(commit):\n'
        '            errors.append(f"{source} commit is not pinned")\n',
        '    grimoire_record = commits.get("grimoire") or commits.get("engineering_standards")\n'
        '    if not isinstance(grimoire_record, dict):\n'
        '        errors.append("grimoire commit is not pinned")\n'
        '    else:\n'
        '        commit = grimoire_record.get("commit")\n'
        '        if not isinstance(commit, str) or not SHA.fullmatch(commit):\n'
        '            errors.append("grimoire commit is not pinned")\n'
        '    zeref_commit = commits.get("zeref_memory_engine", {}).get("commit")\n'
        '    if not isinstance(zeref_commit, str) or not SHA.fullmatch(zeref_commit):\n'
        '        errors.append("zeref_memory_engine commit is not pinned")\n',
    )
    write_text(verify_path, text, changed)


def create_primary_cli(changed: set[str]) -> None:
    path = ROOT / "scripts" / "grimoire.py"
    write_text(
        path,
        '#!/usr/bin/env python3\n"""Primary Grimoire command entrypoint."""\n\n'
        'from standards import main\n\n\nif __name__ == "__main__":\n'
        '    raise SystemExit(main())\n',
        changed,
    )


def create_release_docs(changed: set[str]) -> None:
    migration = """# Grimoire identity migration

## Outcome

The canonical repository identity is `Grimoire`, with the repository URL
`https://github.com/kanadhiayash/grimoire` and the descriptor
`Global Product Engineering Standards Orchestrator`.

## Active interfaces

- Primary CLI: `python3 scripts/grimoire.py`
- Browser-pack source key: `grimoire`
- Browser-pack commit flag: `--grimoire-commit`
- Managed harness marker: `grimoire:zeref-activation`

## Compatibility window

`--engineering-standards-commit` remains a deprecated compatibility alias for
`--grimoire-commit` during the 0.5.x migration window. Existing browser packs
using the legacy source key and existing installed harness blocks using the
legacy marker remain readable and removable. New outputs use only Grimoire.

## Repository settings operation

Rename the GitHub repository in Settings from its previous name to `grimoire`.
After the rename, update local remotes to the canonical Grimoire URL. GitHub may
redirect old links, but active documentation and generated artifacts must not
rely on redirects.

## Verification

Run `python3 scripts/grimoire.py check` and confirm the repository-wide identity
test reports no stale canonical repository URL or slug.
"""
    write_text(ROOT / "docs" / "migrations" / "0.5.0-grimoire.md", migration, changed)

    release = """# Grimoire 0.5.0

## Release outcome

Version 0.5.0 establishes Grimoire as the canonical identity for the global
product engineering standards and operations control plane.

## Changed

- Canonical repository slug and provenance changed to `kanadhiayash/grimoire`.
- Display name changed to `Grimoire`.
- Functional descriptor is `Global Product Engineering Standards Orchestrator`.
- Neutral and personal instruction packs now cite Grimoire.
- Browser-pack manifests use the `grimoire` source key.
- The primary CLI is `scripts/grimoire.py`.
- CI, doctor output, adapters, schemas, prompts, templates, and release metadata
  use the Grimoire identity.

## Compatibility

Deprecated aliases remain for the previous browser-pack commit flag, source key,
and installed harness marker. No Zeref runtime internals are changed.

## Verification

The release requires an exact-head Grimoire CI pass, repository-wide identity
scan, instruction budget tests, browser-pack compatibility tests, and all
existing conformance checks.
"""
    write_text(ROOT / "docs" / "releases" / "0.5.0.md", release, changed)


def update_changelog(changed: set[str]) -> None:
    path = ROOT / "CHANGELOG.md"
    text = path.read_text(encoding="utf-8")
    marker = "## [0.4.0] - 2026-07-24"
    section = """## [0.5.0] - 2026-07-27

### Added

- Grimoire repository identity, canonical URL, descriptor, migration guide, and release record.
- Primary `scripts/grimoire.py` command entrypoint and repository-wide identity checks.
- Backward-compatible browser-pack, CLI-flag, and harness-marker migration support.

### Changed

- Prompts, instructions, policies, schemas, adapters, templates, CI labels, doctor output, and metadata now use Grimoire.
- Repository and baseline release versions advanced to 0.5.0.

### Compatibility

- Existing 0.4.0 project and browser packs remain readable during the 0.5.x migration window.
- Zeref Memory Engine remains a separate, unchanged runtime.

"""
    if section not in text:
        text = text.replace(marker, section + marker)
    write_text(path, text, changed)


def update_readme_identity(changed: set[str]) -> None:
    path = ROOT / "README.md"
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    if lines:
        lines[0] = "# Grimoire"
    text = "\n".join(lines) + "\n"
    text = text.replace(
        "Private, versioned engineering policy and an executable control plane for human and AI-assisted product development.",
        "Global Product Engineering Standards Orchestrator for human, AI, and Zeref-assisted product work.",
    )
    text = text.replace("Version `0.4.0`", "Version `0.5.0`")
    text = text.replace("version `0.4.0`", "version `0.5.0`")
    write_text(path, text, changed)


def update_agent_identity(changed: set[str]) -> None:
    path = ROOT / "AGENTS.md"
    text = path.read_text(encoding="utf-8")
    text = text.replace(
        "This repository is a neutral, private, versioned Grimoire control plane. It operates as the Standards Orchestrator.",
        "Grimoire is the neutral, private, versioned Global Product Engineering Standards Orchestrator.",
    )
    write_text(path, text, changed)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--report", default="artifacts/grimoire-migration.json")
    args = parser.parse_args()
    if not args.apply:
        parser.error("this one-time utility requires --apply")

    changed: set[str] = set()
    migrate_text(changed)
    migrate_index(changed)
    migrate_versions(changed)
    migrate_manifests(changed)
    migrate_python_compatibility(changed)
    create_primary_cli(changed)
    create_release_docs(changed)
    update_changelog(changed)
    update_readme_identity(changed)
    update_agent_identity(changed)

    report_path = ROOT / args.report
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(
        json.dumps({"status": "PASS", "version": VERSION, "changed_files": sorted(changed)}, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({"changed_files": sorted(changed)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
