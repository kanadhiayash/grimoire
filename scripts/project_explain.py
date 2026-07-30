#!/usr/bin/env python3
"""Explain one generated standards control from its stored trace."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from grimoire.evidence import ExplainError, explain_control  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--directory", required=True)
    parser.add_argument("--standard-id", required=True)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    try:
        result = explain_control(Path(args.directory), args.standard_id)
    except ExplainError as exc:
        print(json.dumps({"status": "INVALID", "error_code": exc.code}), file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
