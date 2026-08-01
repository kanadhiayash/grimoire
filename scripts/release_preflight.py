#!/usr/bin/env python3
"""Report final release blockers without changing Git or GitHub."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from grimoire.release import (  # noqa: E402
    evaluate_final_release,
    verify_release_tag,
)


def _json_object(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("expected_json_object")
    return value


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    actions = parser.add_subparsers(dest="action", required=True)
    preflight = actions.add_parser("preflight")
    preflight.add_argument("--candidate-run", action="append", required=True)
    preflight.add_argument("--comparison", required=True)
    preflight.add_argument("--release-evidence", required=True)
    preflight.add_argument("--expected-sha", required=True)
    preflight.add_argument("--version", required=True)
    preflight.add_argument("--tag", required=True)
    preflight.add_argument("--require-tag", action="store_true")
    tag = actions.add_parser("verify-tag")
    tag.add_argument("--expected-sha", required=True)
    tag.add_argument("--tag", required=True)
    return parser


def _blocked_input() -> dict:
    return {
        "status": "BLOCKED",
        "eligible": False,
        "reason_codes": ["final_release_input_invalid"],
    }


def main() -> int:
    args = _parser().parse_args()
    try:
        if args.action == "verify-tag":
            result = verify_release_tag(
                ROOT,
                tag=args.tag,
                expected_commit=args.expected_sha,
            )
        else:
            result = evaluate_final_release(
                root=ROOT,
                expected_commit=args.expected_sha,
                intended_version=args.version,
                intended_tag=args.tag,
                candidate_runs=[Path(item) for item in args.candidate_run],
                candidate_comparison=_json_object(Path(args.comparison)),
                release_evidence=_json_object(Path(args.release_evidence)),
                require_tag=args.require_tag,
            )
    except (OSError, UnicodeError, ValueError, TypeError, json.JSONDecodeError):
        print(json.dumps(_blocked_input(), sort_keys=True), file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
