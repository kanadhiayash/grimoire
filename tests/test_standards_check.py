from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from checks import standards_check  # noqa: E402


class StandardsCheckTests(unittest.TestCase):
    def test_all_repository_checks_pass(self) -> None:
        failures = [
            result
            for result in standards_check.run_checks()
            if not result.passed
        ]

        self.assertEqual([], failures)

    def test_baseline_version_matches_version_file(self) -> None:
        version = (
            ROOT / "VERSION"
        ).read_text(encoding="utf-8").strip()

        baseline = json.loads(
            (
                ROOT / "policies/baseline.json"
            ).read_text(encoding="utf-8")
        )

        self.assertEqual(
            version,
            baseline["standard_version"],
        )

    def test_profiles_have_resolvable_inheritance(self) -> None:
        for path in (ROOT / "profiles").glob("*.json"):
            profile = json.loads(
                path.read_text(encoding="utf-8")
            )

            self.assertTrue(
                (ROOT / profile["inherits"]).is_file(),
                path.name,
            )


if __name__ == "__main__":
    unittest.main()
