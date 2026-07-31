from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

try:
    from jsonschema import Draft202012Validator
except ImportError:  # The external validator is installed only in schema CI.
    Draft202012Validator = None  # type: ignore[assignment]

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from grimoire.zeref.profile import build_profile_v2  # noqa: E402
from grimoire.zeref.receipt import (  # noqa: E402
    receipt_integrity_hash,
    verify_zeref_receipt,
    zeref_profile_hash,
)


class ZerefReceiptVerifierTests(unittest.TestCase):
    now = datetime(2026, 7, 31, 1, 0, tzinfo=timezone.utc)

    def profile(self) -> dict[str, object]:
        return build_profile_v2(
            {
                "plan_id": "GRM-PILOT-001",
                "plan_revision": 1,
                "project_repository": "local/grimoire-pilot",
                "project_commit": "a" * 40,
                "approved_scope": ["docs/pilot.md"],
                "excluded_scope": ["deploy", "publish"],
                "permitted_tools": [
                    "filesystem-read",
                    "filesystem-write",
                    "test-runner",
                ],
                "prohibited_tools": ["network", "credential-store"],
                "approval_required_for": [
                    "merge",
                    "deploy",
                    "publish",
                    "external_send",
                    "destructive_change",
                    "credential_change",
                    "canonical_memory_write",
                ],
                "retry_ceiling": 2,
                "receipt_expiry_seconds": 3600,
                "cost_limit": {"amount": 0, "currency": "USD"},
            },
            pack_hash="b" * 64,
            required_controls=("GRM-UNI-001", "GRM-AI-001"),
            required_documents=("Implementation plan",),
            acceptance_criteria=("Tests pass",),
            stop_conditions=("missing evidence",),
            grimoire_version="0.5.0",
            mode="standard",
            cost_ceiling="bounded",
        ).to_dict()

    def receipt(self, profile: dict[str, object]) -> dict[str, object]:
        value: dict[str, object] = {
            "schema_id": "grimoire.zeref.receipt.v1",
            "schema_version": "1.0",
            "profile_hash": zeref_profile_hash(profile),
            "pack_hash": profile["pack_hash"],
            "plan": {"id": "GRM-PILOT-001", "revision": 1},
            "project": {
                "repository": "local/grimoire-pilot",
                "commit_before": "a" * 40,
                "commit_after": "c" * 40,
                "branch": "feat/pilot",
            },
            "roles": [{"name": "Codex Implementer", "kind": "lead"}],
            "models": [
                {
                    "requested": "lowest-cost-capable",
                    "actual": "NOT_OBSERVABLE",
                }
            ],
            "tools": ["filesystem-read", "filesystem-write", "test-runner"],
            "commands": ["python3 -m unittest tests.test_zeref_receipt -v"],
            "files_changed": ["docs/pilot.md"],
            "tests": [
                {
                    "name": "zeref-receipt",
                    "result": "PASS",
                    "evidence_id": "EVD-001",
                }
            ],
            "evidence": [
                {
                    "id": "EVD-001",
                    "control_id": "GRM-UNI-001",
                    "subject_commit": "c" * 40,
                    "command": "python3 -m unittest tests.test_zeref_receipt -v",
                    "result": "PASS",
                    "timestamp": "2026-07-31T00:30:00+00:00",
                    "reviewer": "Codex",
                },
                {
                    "id": "EVD-002",
                    "control_id": "GRM-AI-001",
                    "subject_commit": "c" * 40,
                    "command": "python3 scripts/grimoire.py check",
                    "result": "PASS",
                    "timestamp": "2026-07-31T00:31:00+00:00",
                    "reviewer": "Codex",
                },
            ],
            "approvals": [],
            "retries": 0,
            "cost": {
                "amount": 0,
                "currency": "USD",
                "ceiling_status": "WITHIN_CEILING",
            },
            "stop_events": [],
            "completion_status": "PASS",
            "memory_proposals": [],
            "external_actions": [],
            "timestamp": "2026-07-31T00:30:00+00:00",
            "expires_at": "2026-07-31T01:30:00+00:00",
            "runtime": {
                "harness": "codex",
                "zeref_layer": "installed-contract",
                "capability": "LOCAL_HARNESS_EXECUTION",
            },
        }
        value["integrity"] = {
            "algorithm": "sha256-canonical-json-v1",
            "digest": receipt_integrity_hash(value),
        }
        return value

    def rehash(self, receipt: dict[str, object]) -> None:
        receipt["integrity"] = {
            "algorithm": "sha256-canonical-json-v1",
            "digest": receipt_integrity_hash(receipt),
        }

    def test_fixture_catalog_names_every_required_failure_class(self) -> None:
        catalog = json.loads(
            (
                ROOT
                / "tests"
                / "fixtures"
                / "zeref"
                / "receipt"
                / "cases.json"
            ).read_text(encoding="utf-8")
        )
        self.assertEqual(
            {item["id"] for item in catalog["cases"]},
            {
                "valid",
                "plan-mismatch",
                "pack-mismatch",
                "project-mismatch",
                "missing-evidence",
                "expired",
                "unauthorized-external-action",
                "unauthorized-memory-promotion",
            },
        )

    def test_valid_receipt_passes_only_zeref_execution_dimension(self) -> None:
        profile = self.profile()
        result = verify_zeref_receipt(
            self.receipt(profile),
            profile,
            now=self.now,
        ).to_dict()
        self.assertEqual(result["verification_status"], "PASS")
        self.assertEqual(result["zeref_execution_status"], "PASS")
        self.assertEqual(
            result["assurance_ceiling"],
            {
                "CONTROL_VERIFICATION_STATUS": "NOT_VERIFIED",
                "PROJECT_READINESS_STATUS": "NOT_VERIFIED",
                "RELEASE_ASSURANCE_STATUS": "NOT_VERIFIED",
                "LEGAL_REVIEW_STATUS": "NOT_VERIFIED",
            },
        )

    @unittest.skipUnless(
        Draft202012Validator is not None,
        "jsonschema is installed only for schema validation",
    )
    def test_valid_receipt_matches_closed_draft_2020_12_schema(self) -> None:
        profile = self.profile()
        receipt = self.receipt(profile)
        schema = json.loads(
            (
                ROOT
                / "policies"
                / "schemas"
                / "zeref-execution-receipt-v1.schema.json"
            ).read_text(encoding="utf-8")
        )
        Draft202012Validator.check_schema(schema)
        self.assertEqual([], list(Draft202012Validator(schema).iter_errors(receipt)))

    def test_plan_pack_profile_and_project_mismatches_fail_stably(self) -> None:
        mutations = (
            ("plan", lambda value: value["plan"].update({"id": "other"}), "plan_mismatch"),
            ("revision", lambda value: value["plan"].update({"revision": 2}), "revision_mismatch"),
            ("pack", lambda value: value.update({"pack_hash": "d" * 64}), "pack_hash_mismatch"),
            ("profile", lambda value: value.update({"profile_hash": "d" * 64}), "profile_hash_mismatch"),
            (
                "project",
                lambda value: value["project"].update({"commit_before": "d" * 40}),
                "project_commit_mismatch",
            ),
        )
        profile = self.profile()
        for name, mutate, expected in mutations:
            with self.subTest(name=name):
                receipt = self.receipt(profile)
                mutate(receipt)
                self.rehash(receipt)
                result = verify_zeref_receipt(receipt, profile, now=self.now)
                self.assertEqual(result.verification_status, "FAIL")
                self.assertIn(expected, result.reason_codes)

    def test_missing_evidence_and_unauthorized_action_fail(self) -> None:
        profile = self.profile()
        receipt = self.receipt(profile)
        receipt["evidence"] = receipt["evidence"][:1]
        receipt["external_actions"] = [
            {"action": "publish", "status": "PERFORMED"}
        ]
        self.rehash(receipt)
        result = verify_zeref_receipt(receipt, profile, now=self.now)
        self.assertIn("required_control_evidence_missing", result.reason_codes)
        self.assertIn("external_action_unauthorized", result.reason_codes)

    def test_expired_receipt_and_invalid_memory_promotion_fail(self) -> None:
        profile = self.profile()
        receipt = self.receipt(profile)
        receipt["expires_at"] = "2026-07-31T00:45:00+00:00"
        receipt["memory_proposals"] = [
            {
                "target": "canonical_memory",
                "approved": False,
                "approval_id": "",
            }
        ]
        self.rehash(receipt)
        result = verify_zeref_receipt(receipt, profile, now=self.now)
        self.assertIn("receipt_expired", result.reason_codes)
        self.assertIn("memory_promotion_unauthorized", result.reason_codes)

    def test_scope_tool_retry_cost_and_integrity_limits_fail(self) -> None:
        profile = self.profile()
        receipt = self.receipt(profile)
        receipt["files_changed"] = ["src/out-of-scope.py"]
        receipt["tools"] = ["network"]
        receipt["retries"] = 3
        receipt["cost"] = {
            "amount": 1,
            "currency": "USD",
            "ceiling_status": "EXCEEDED",
        }
        self.rehash(receipt)
        receipt["stop_events"] = [{"code": "after_integrity"}]
        result = verify_zeref_receipt(receipt, profile, now=self.now)
        self.assertIn("file_scope_unauthorized", result.reason_codes)
        self.assertIn("tool_unauthorized", result.reason_codes)
        self.assertIn("retry_ceiling_exceeded", result.reason_codes)
        self.assertIn("cost_ceiling_exceeded", result.reason_codes)
        self.assertIn("receipt_integrity_mismatch", result.reason_codes)

    def test_untrusted_structure_and_evidence_links_fail_without_crash(self) -> None:
        self.assertIn(
            "invalid_receipt",
            verify_zeref_receipt([], self.profile(), now=self.now).reason_codes,
        )
        self.assertIn(
            "invalid_profile",
            verify_zeref_receipt({}, [], now=self.now).reason_codes,
        )
        profile = self.profile()
        receipt = self.receipt(profile)
        receipt["roles"] = [{"name": "Support only", "kind": "support"}]
        receipt["models"] = []
        receipt["commands"] = []
        receipt["tests"][0]["evidence_id"] = "missing"
        receipt["evidence"][0]["subject_commit"] = "d" * 40
        receipt["external_actions"] = [
            {"action": "unknown-write", "status": "PERFORMED"}
        ]
        receipt["runtime"]["capability"] = "BROWSER_SIMULATION"
        self.rehash(receipt)
        result = verify_zeref_receipt(receipt, profile, now=self.now)
        self.assertIn("invalid_role_record", result.reason_codes)
        self.assertIn("invalid_model_record", result.reason_codes)
        self.assertIn("invalid_command_record", result.reason_codes)
        self.assertIn("required_test_evidence_missing", result.reason_codes)
        self.assertIn("required_control_evidence_missing", result.reason_codes)
        self.assertIn("external_action_unauthorized", result.reason_codes)
        self.assertIn("runtime_capability_not_verified", result.reason_codes)

    def test_cli_returns_machine_diagnostic_without_network(self) -> None:
        profile = self.profile()
        receipt = self.receipt(profile)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            profile_path = root / "profile.json"
            receipt_path = root / "receipt.json"
            profile_path.write_text(json.dumps(profile), encoding="utf-8")
            receipt_path.write_text(json.dumps(receipt), encoding="utf-8")
            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/grimoire.py",
                    "zeref",
                    "verify-receipt",
                    "--profile",
                    str(profile_path),
                    "--receipt",
                    str(receipt_path),
                    "--now",
                    self.now.isoformat(),
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(json.loads(completed.stdout)["verification_status"], "PASS")


if __name__ == "__main__":
    unittest.main()
