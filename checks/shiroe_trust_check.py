#!/usr/bin/env python3
"""Verify the pinned public Shiroe source contract used by Grimoire."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import tempfile
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any


def _json_object(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("expected_json_object")
    return value


def _fetch(url: str) -> bytes:
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "grimoire-shiroe-trust-check/1.0"},
    )
    with urllib.request.urlopen(request, timeout=20) as response:
        return response.read()


def _read_checkout_file(checkout: Path, relative_path: str) -> bytes:
    root = checkout.resolve()
    target = (root / relative_path).resolve()
    if root not in target.parents and target != root:
        raise ValueError("shiroe_checkout_path_escape")
    if not target.is_file():
        raise FileNotFoundError(relative_path)
    return target.read_bytes()


def _verify_checkout_commit(checkout: Path, expected_commit: str) -> None:
    observed = subprocess.run(
        ["git", "-C", str(checkout), "rev-parse", "HEAD"],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    ).stdout.strip()
    if observed != expected_commit:
        raise ValueError("shiroe_checkout_commit_mismatch")


def _checkout_repository(repository: str, commit: str, checkout: Path) -> None:
    url = f"https://github.com/{repository}.git"
    subprocess.run(
        ["git", "init", "--quiet", str(checkout)],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    subprocess.run(
        ["git", "-C", str(checkout), "remote", "add", "origin", url],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    subprocess.run(
        ["git", "-C", str(checkout), "fetch", "--depth", "1", "origin", commit],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    subprocess.run(
        ["git", "-C", str(checkout), "checkout", "--detach", "--quiet", "FETCH_HEAD"],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    _verify_checkout_commit(checkout, commit)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument(
        "--source-checkout",
        help="Optional existing Shiroe checkout pinned to the contract commit.",
    )
    args = parser.parse_args()
    contract = _json_object(Path(args.contract))
    reasons: list[str] = []
    fetched: list[dict[str, Any]] = []
    repository = contract.get("runtime_repository")
    commit = contract.get("commit")
    if repository != "kanadhiayash/shiroe":
        reasons.append("shiroe_repository_mismatch")
    if not isinstance(commit, str) or len(commit) != 40:
        reasons.append("shiroe_commit_invalid")
        commit = ""
    source_checkout = args.source_checkout or os.environ.get("SHIROE_SOURCE_CHECKOUT")
    checkout_path = Path(source_checkout).resolve() if source_checkout else None
    checkout_verified = False
    with tempfile.TemporaryDirectory(prefix="grimoire-shiroe-trust-") as directory:
        fallback_checkout: Path | None = None
        for record in contract.get("required_files", []):
            if not isinstance(record, dict):
                reasons.append("shiroe_contract_file_invalid")
                continue
            path = record.get("path")
            expected = record.get("sha256")
            if not isinstance(path, str) or not isinstance(expected, str):
                reasons.append("shiroe_contract_file_invalid")
                continue
            url = f"https://raw.githubusercontent.com/{repository}/{commit}/{path}"
            transport = "raw_github"
            try:
                content = _fetch(url)
            except (urllib.error.URLError, TimeoutError, OSError):
                try:
                    if checkout_path is not None:
                        if not checkout_verified:
                            _verify_checkout_commit(checkout_path, commit)
                            checkout_verified = True
                        content = _read_checkout_file(checkout_path, path)
                        transport = "source_checkout"
                    else:
                        if fallback_checkout is None:
                            fallback_checkout = Path(directory) / "shiroe"
                            _checkout_repository(repository, commit, fallback_checkout)
                        content = _read_checkout_file(fallback_checkout, path)
                        transport = "git_checkout"
                except (
                    OSError,
                    subprocess.CalledProcessError,
                    ValueError,
                ):
                    reasons.append("shiroe_source_unreachable")
                    continue
            observed = hashlib.sha256(content).hexdigest()
            fetched.append(
                {
                    "path": path,
                    "sha256": observed,
                    "size": len(content),
                    "transport": transport,
                }
            )
            if observed != expected:
                reasons.append("shiroe_source_hash_mismatch")
            if path == "shiroe-registry.json":
                try:
                    registry = json.loads(content.decode("utf-8"))
                except (UnicodeDecodeError, json.JSONDecodeError):
                    reasons.append("shiroe_registry_invalid")
                    continue
                required = contract.get("required_registry", {})
                if registry.get("version") != required.get("version"):
                    reasons.append("shiroe_registry_version_mismatch")
                if len(registry.get("skills", [])) < required.get("skills_minimum", 0):
                    reasons.append("shiroe_registry_skill_count_low")
                commands = registry.get("commands", [])
                if isinstance(commands, list) and len(commands) < required.get(
                    "commands_minimum", 0
                ):
                    reasons.append("shiroe_registry_command_count_low")
    result = {
        "schema_version": 1,
        "status": "FAIL" if reasons else "PASS",
        "reason_codes": sorted(set(reasons)),
        "runtime": "shiroe",
        "runtime_repository": repository,
        "commit": commit,
        "fetched": fetched,
        "claims_verified": contract.get("claims", {}).get("verified", []),
        "claims_not_made": contract.get("claims", {}).get("not_claimed", []),
    }
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
