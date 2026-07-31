#!/usr/bin/env python3
"""Verify a Zeref execution receipt against one Grimoire profile v2."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from grimoire.zeref import verify_zeref_receipt  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", required=True)
    parser.add_argument("--receipt", required=True)
    parser.add_argument("--now")
    args = parser.parse_args()
    try:
        profile = json.loads(Path(args.profile).read_text(encoding="utf-8"))
        receipt = json.loads(Path(args.receipt).read_text(encoding="utf-8"))
        now = datetime.fromisoformat(args.now) if args.now else None
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError):
        print(
            json.dumps(
                {
                    "verification_status": "FAIL",
                    "zeref_execution_status": "NOT_VERIFIED",
                    "reason_codes": ["invalid_input_document"],
                },
                indent=2,
            )
        )
        return 2
    result = verify_zeref_receipt(receipt, profile, now=now)
    print(json.dumps(result.to_dict(), indent=2))
    return 0 if result.verification_status == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
