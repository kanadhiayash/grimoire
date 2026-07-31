from __future__ import annotations

import json
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from grimoire.benchmarks.zeref_pilot import (  # noqa: E402
    create_reproduction_attestation,
    run_pilot,
    verify_pilot_reproduction,
)


class ZerefEndToEndPilotTests(unittest.TestCase):
    timestamp = "2026-07-31T02:00:00+00:00"
    now = datetime(2026, 7, 31, 2, 30, tzinfo=timezone.utc)

    def test_primary_run_is_complete_but_execution_remains_not_verified(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            result = run_pilot(
                ROOT,
                Path(directory) / "pilot",
                commit_after="c" * 40,
                files_changed=(
                    "benchmarks/zeref-pilot/README.md",
                    "tests/test_zeref_pilot.py",
                ),
                timestamp=self.timestamp,
            )
        self.assertEqual(result["pilot_status"], "PARTIAL")
        self.assertEqual(result["receipt_verification_status"], "PASS")
        self.assertEqual(result["zeref_execution_status"], "NOT_VERIFIED")
        self.assertIn("independent_reproduction_required", result["reason_codes"])

    def test_separate_reproduction_attestation_completes_scoped_pilot(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "pilot"
            reproduction = Path(directory) / "reproduction"
            run_pilot(
                ROOT,
                output,
                commit_after="c" * 40,
                files_changed=(
                    "benchmarks/zeref-pilot/README.md",
                    "tests/test_zeref_pilot.py",
                ),
                timestamp=self.timestamp,
            )
            run_pilot(
                ROOT,
                reproduction,
                commit_after="c" * 40,
                files_changed=(
                    "benchmarks/zeref-pilot/README.md",
                    "tests/test_zeref_pilot.py",
                ),
                timestamp=self.timestamp,
            )
            attestation = create_reproduction_attestation(
                output,
                reproduction,
                reviewer="independent-agent",
                producer="primary-agent",
                timestamp="2026-07-31T02:10:00+00:00",
            )
            result = verify_pilot_reproduction(
                output,
                reproduction,
                attestation,
                now=self.now,
            )
        self.assertEqual(result["pilot_status"], "PASS")
        self.assertEqual(result["zeref_execution_status"], "PASS")
        self.assertEqual(
            result["reviewer_identity_status"],
            "DECLARED_NOT_CRYPTOGRAPHICALLY_VERIFIED",
        )

    def test_mismatch_same_reviewer_and_browser_simulation_fail(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "pilot"
            reproduction = Path(directory) / "reproduction"
            run_pilot(
                ROOT,
                output,
                commit_after="c" * 40,
                files_changed=(
                    "benchmarks/zeref-pilot/README.md",
                    "tests/test_zeref_pilot.py",
                ),
                timestamp=self.timestamp,
            )
            run_pilot(
                ROOT,
                reproduction,
                commit_after="c" * 40,
                files_changed=(
                    "benchmarks/zeref-pilot/README.md",
                    "tests/test_zeref_pilot.py",
                ),
                timestamp=self.timestamp,
            )
            with self.assertRaises(ValueError):
                create_reproduction_attestation(
                    output,
                    reproduction,
                    reviewer="same-agent",
                    producer="same-agent",
                    timestamp="2026-07-31T02:10:00+00:00",
                )
            attestation = create_reproduction_attestation(
                output,
                reproduction,
                reviewer="independent-agent",
                producer="primary-agent",
                timestamp="2026-07-31T02:10:00+00:00",
            )
            attestation["pilot_evidence_hash"] = "d" * 64
            result = verify_pilot_reproduction(
                output,
                reproduction,
                attestation,
                now=self.now,
            )
            self.assertEqual(result["pilot_status"], "FAIL")
            self.assertIn("pilot_evidence_mismatch", result["reason_codes"])

            second_attestation = create_reproduction_attestation(
                output,
                reproduction,
                reviewer="second-agent",
                producer="primary-agent",
                timestamp="2026-07-31T02:10:00+00:00",
            )
            receipt_path = output / "EXECUTION_RECEIPT.v1.json"
            receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
            receipt["runtime"]["capability"] = "BROWSER_SIMULATION"
            receipt_path.write_text(json.dumps(receipt), encoding="utf-8")
            result = verify_pilot_reproduction(
                output,
                reproduction,
                second_attestation,
                now=self.now,
            )
        self.assertEqual(result["pilot_status"], "FAIL")
        self.assertIn("pilot_artifact_hash_mismatch", result["reason_codes"])

    def test_reproduction_directory_and_expected_primary_state_are_verified(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "pilot"
            reproduction = Path(directory) / "reproduction"
            run_pilot(
                ROOT,
                output,
                commit_after="c" * 40,
                files_changed=("tests/test_zeref_pilot.py",),
                timestamp=self.timestamp,
            )
            run_pilot(
                ROOT,
                reproduction,
                commit_after="c" * 40,
                files_changed=("tests/test_zeref_pilot.py",),
                timestamp=self.timestamp,
            )
            attestation = create_reproduction_attestation(
                output,
                reproduction,
                reviewer="independent-agent",
                producer="primary-agent",
                timestamp="2026-07-31T02:10:00+00:00",
            )
            result_path = reproduction / "PILOT_RESULT.json"
            reproduced_result = json.loads(
                result_path.read_text(encoding="utf-8")
            )
            reproduced_result["pilot_status"] = "PASS"
            result_path.write_text(
                json.dumps(reproduced_result),
                encoding="utf-8",
            )
            result = verify_pilot_reproduction(
                output,
                reproduction,
                attestation,
                now=self.now,
            )
        self.assertEqual(result["pilot_status"], "FAIL")
        self.assertIn("pilot_artifact_hash_mismatch", result["reason_codes"])
        self.assertIn("reproduction_result_not_eligible", result["reason_codes"])


if __name__ == "__main__":
    unittest.main()
