from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

try:
    from jsonschema import Draft202012Validator
except ImportError:
    Draft202012Validator = None  # type: ignore[assignment]

ROOT = Path(__file__).resolve().parents[1]


class FinalOperationalAuditTests(unittest.TestCase):
    def test_public_use_is_granted_by_mit_license_and_readme(self):
        license_text = (ROOT / "LICENSE").read_text(encoding="utf-8")
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertTrue(license_text.startswith("MIT License\n"))
        self.assertIn("Permission is hereby granted", license_text)
        self.assertIn("MIT License", readme)
        self.assertNotIn("private and proprietary", license_text)

    def test_active_policy_uses_locked_grimoire_identity(self):
        policy = json.loads(
            (
                ROOT / "policies" / "standards-orchestrator.json"
            ).read_text(encoding="utf-8")
        )
        self.assertEqual(
            {
                "display_name": "Grimoire",
                "descriptor": (
                    "Global Product Engineering Standards Orchestrator"
                ),
                "repository": "kanadhiayash/grimoire",
            },
            policy["identity"],
        )
        self.assertNotIn("future_name", policy["identity"])

    def test_orchestrator_schema_is_closed_and_complete(self):
        schema = json.loads(
            (
                ROOT
                / "policies"
                / "schemas"
                / "standards-orchestrator.schema.json"
            ).read_text(encoding="utf-8")
        )
        policy = json.loads(
            (
                ROOT / "policies" / "standards-orchestrator.json"
            ).read_text(encoding="utf-8")
        )
        self.assertFalse(schema["additionalProperties"])
        self.assertEqual(set(policy), set(schema["required"]))
        self.assertFalse(
            schema["properties"]["identity"]["additionalProperties"]
        )
        self.assertFalse(
            schema["properties"]["shiroe_boundary"]["additionalProperties"]
        )
        self.assertIn("external_action_approval", schema["properties"])

    def test_orchestrator_schema_locks_safeguard_vocabularies(self):
        policy = json.loads(
            (
                ROOT / "policies" / "standards-orchestrator.json"
            ).read_text(encoding="utf-8")
        )
        schema = json.loads(
            (
                ROOT
                / "policies"
                / "schemas"
                / "standards-orchestrator.schema.json"
            ).read_text(encoding="utf-8")
        )
        for name in (
            "principles",
            "lifecycle",
            "completion_statuses",
            "applicability_statuses",
            "authority_classes",
            "external_action_approval",
        ):
            with self.subTest(name=name):
                self.assertEqual(
                    policy[name], schema["properties"][name]["const"]
                )
        for name, expected in policy["shiroe_boundary"].items():
            with self.subTest(shiroe=name):
                self.assertEqual(
                    expected,
                    schema["properties"]["shiroe_boundary"][
                        "properties"
                    ][name]["const"],
                )
        for name, expected in policy["priority"].items():
            with self.subTest(priority=name):
                self.assertEqual(
                    expected,
                    schema["properties"]["priority"]["properties"][name][
                        "const"
                    ],
                )

    @unittest.skipUnless(
        Draft202012Validator is not None,
        "jsonschema is installed only for schema validation",
    )
    def test_schema_validator_rejects_safeguard_replacement(self):
        policy = json.loads(
            (
                ROOT / "policies" / "standards-orchestrator.json"
            ).read_text(encoding="utf-8")
        )
        schema = json.loads(
            (
                ROOT
                / "policies"
                / "schemas"
                / "standards-orchestrator.schema.json"
            ).read_text(encoding="utf-8")
        )
        validator = Draft202012Validator(schema)
        candidates = []
        replaced_approval = copy.deepcopy(policy)
        replaced_approval["external_action_approval"] = ["noop"]
        candidates.append(replaced_approval)
        replaced_shiroe = copy.deepcopy(policy)
        replaced_shiroe["shiroe_boundary"]["forbidden"] = ["noop"]
        candidates.append(replaced_shiroe)
        for candidate in candidates:
            self.assertTrue(list(validator.iter_errors(candidate)))

    def test_final_finding_register_closes_accepted_findings(self):
        register = (
            ROOT
            / "docs"
            / "audits"
            / "2026-08-01"
            / "FINAL_OPERATIONAL_AUDIT.md"
        ).read_text(encoding="utf-8")
        for finding in (
            "AUD-001",
            "AUD-002",
            "AUD-003",
            "AUD-004",
            "AUD-005",
        ):
            self.assertIn(f"`{finding}`", register)
        self.assertIn(
            "Open accepted audit findings after fixes: `0`", register
        )
        self.assertIn("External Zeref runtime: `NOT_VERIFIED`", register)
        self.assertIn("Repository visibility: `PRIVATE`", register)


if __name__ == "__main__":
    unittest.main()
