from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

try:
    from jsonschema import Draft202012Validator
except ImportError:  # The external validator is installed only in schema CI.
    Draft202012Validator = None  # type: ignore[assignment]

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from grimoire.zeref.profile import (  # noqa: E402
    ProfileValidationError,
    build_profile_v2,
)
from scripts.project_orchestrator import compile_project  # noqa: E402


class ZerefProfileV2Tests(unittest.TestCase):
    def binding(self) -> dict[str, object]:
        return {
            "plan_id": "GRM-PILOT-001",
            "plan_revision": 1,
            "project_repository": "local/grimoire-pilot",
            "project_commit": "a" * 40,
            "approved_scope": ["docs/pilot.md"],
            "excluded_scope": ["deploy", "publish"],
            "permitted_tools": ["filesystem-read", "filesystem-write", "test-runner"],
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
        }

    def manifest(self) -> dict[str, object]:
        return {
            "schema_version": 1,
            "project": {
                "name": "Zeref Pilot",
                "lifecycle_stage": "BUILD_READY",
                "product_types": ["internal-tool"],
            },
            "users": ["authenticated"],
            "markets": [],
            "platforms": ["web"],
            "stack": {"languages": ["python"], "frameworks": [], "services": []},
            "data": {"personal_data": False, "sensitive": []},
            "ai": {
                "user_facing": False,
                "automated_decisions": False,
                "external_models": False,
            },
            "risk": {"level": "moderate"},
            "standards": {"version": "0.4.0"},
            "zeref": {"mode": "standard", "cost_ceiling": "bounded"},
            "unknowns": [],
        }

    def test_required_bindings_are_fail_closed(self) -> None:
        required = (
            "plan_id",
            "plan_revision",
            "project_repository",
            "project_commit",
            "approved_scope",
            "approval_required_for",
        )
        for field in required:
            with self.subTest(field=field):
                value = self.binding()
                value.pop(field)
                with self.assertRaises(ProfileValidationError) as raised:
                    build_profile_v2(
                        value,
                        pack_hash="b" * 64,
                        required_controls=("GRM-UNI-001",),
                        required_documents=("Implementation plan",),
                        acceptance_criteria=("Tests pass",),
                        stop_conditions=("missing evidence",),
                        grimoire_version="0.5.0",
                        mode="standard",
                        cost_ceiling="bounded",
                    )
                self.assertIn(f"missing_{field}", raised.exception.reason_codes)

    def test_required_approval_and_tool_boundaries_cannot_be_weakened(self) -> None:
        value = self.binding()
        value["approval_required_for"] = ["merge"]
        value["prohibited_tools"] = ["network", "test-runner"]
        with self.assertRaises(ProfileValidationError) as raised:
            build_profile_v2(
                value,
                pack_hash="b" * 64,
                required_controls=("GRM-UNI-001",),
                required_documents=("Implementation plan",),
                acceptance_criteria=("Tests pass",),
                stop_conditions=("missing evidence",),
                grimoire_version="0.5.0",
                mode="standard",
                cost_ceiling="bounded",
            )
        self.assertIn("approval_boundary_weakened", raised.exception.reason_codes)
        self.assertIn("tool_boundary_conflict", raised.exception.reason_codes)

    def test_compiler_emits_reproducible_profile_v2(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            first = Path(directory) / "first"
            second = Path(directory) / "second"
            compile_project(
                self.manifest(),
                first,
                deterministic=True,
                zeref_contract=self.binding(),
            )
            compile_project(
                self.manifest(),
                second,
                deterministic=True,
                zeref_contract=self.binding(),
            )
            first_profile = (first / "ZEREF_EXECUTION_PROFILE.json").read_bytes()
            second_profile = (second / "ZEREF_EXECUTION_PROFILE.json").read_bytes()
            profile = json.loads(first_profile)

        self.assertEqual(first_profile, second_profile)
        self.assertEqual(profile["schema_version"], "2.0")
        self.assertRegex(profile["pack_hash"], r"^[0-9a-f]{64}$")
        self.assertEqual(profile["plan"]["id"], "GRM-PILOT-001")
        self.assertEqual(profile["plan"]["revision"], 1)
        self.assertEqual(
            profile["expected_receipt"]["schema_id"],
            "grimoire.zeref.receipt.v1",
        )
        for constraint in profile["constraint_trace"]:
            self.assertTrue(constraint["source"])

    @unittest.skipUnless(
        Draft202012Validator is not None,
        "jsonschema is installed only for schema validation",
    )
    def test_profile_validates_under_draft_2020_12(self) -> None:
        profile = build_profile_v2(
            self.binding(),
            pack_hash="b" * 64,
            required_controls=("GRM-UNI-001",),
            required_documents=("Implementation plan",),
            acceptance_criteria=("Tests pass",),
            stop_conditions=("missing evidence",),
            grimoire_version="0.5.0",
            mode="standard",
            cost_ceiling="bounded",
        ).to_dict()
        schema = json.loads(
            (
                ROOT
                / "policies"
                / "schemas"
                / "zeref-execution-profile-v2.schema.json"
            ).read_text(encoding="utf-8")
        )
        Draft202012Validator.check_schema(schema)
        self.assertEqual([], list(Draft202012Validator(schema).iter_errors(profile)))


if __name__ == "__main__":
    unittest.main()
