from __future__ import annotations

import copy
import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "policies" / "grimoire-2-release-gates.json"
SCHEMA = ROOT / "policies" / "schemas" / "grimoire-2-release-gates.schema.json"
MODULE = ROOT / "src" / "grimoire" / "release" / "rubric.py"
FINDINGS = ROOT / "docs" / "audits" / "2026-08-15" / "FINDINGS.json"

EXPECTED_DIMENSIONS = {
    "repository_identity",
    "canonical_vocabulary",
    "authority_precedence",
    "normative_schema_conformance",
    "human_machine_parity",
    "work_type_coverage",
    "runtime_boundary",
    "legacy_compatibility_isolation",
    "official_source_provenance",
    "source_currentness",
    "temporal_legal_routing",
    "applicability",
    "contradiction_detection",
    "compiler_determinism",
    "project_pack_verification",
    "human_ai_experience",
    "bounded_ai_context",
    "shiroe_handoff_receipt",
    "python_platform_matrix",
    "release_candidate_benchmarks",
    "exact_head_ci",
    "independent_reproduction_audit",
    "security_reporting",
    "open_release_blocking_findings",
}


def _load_module():
    if not MODULE.is_file():
        raise AssertionError("Grimoire 2.0 release-rubric evaluator is missing")
    spec = importlib.util.spec_from_file_location("grimoire_2_release_rubric_test", MODULE)
    if spec is None or spec.loader is None:
        raise AssertionError("cannot load release-rubric evaluator")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _load_policy(module):
    if not POLICY.is_file():
        raise AssertionError("Grimoire 2.0 release-gate policy is missing")
    if not SCHEMA.is_file():
        raise AssertionError("Grimoire 2.0 release-gate schema is missing")
    return module.load_release_gate_policy(POLICY)


def _all_pass_results(policy: dict) -> dict[str, str]:
    return {item["id"]: "PASS" for item in policy["dimensions"] if item["required"]}


class Grimoire2ReleaseGateTests(unittest.TestCase):
    def test_required_partial_blocks_release(self):
        module = _load_module()
        policy = _load_policy(module)
        results = _all_pass_results(policy)
        first_required = next(item["id"] for item in policy["dimensions"] if item["required"])
        results[first_required] = "PARTIAL"

        decision = module.evaluate_release_gate_results(policy, results)

        self.assertEqual(decision["eligibility_status"], "BLOCKED")
        self.assertFalse(decision["eligible_for_owner_approval"])
        self.assertFalse(decision["release_authorized"])
        self.assertIn(first_required, decision["blocking_dimensions"])

    def test_required_blocked_blocks_release(self):
        module = _load_module()
        policy = _load_policy(module)
        results = _all_pass_results(policy)
        first_required = next(item["id"] for item in policy["dimensions"] if item["required"])
        results[first_required] = "BLOCKED"

        decision = module.evaluate_release_gate_results(policy, results)

        self.assertEqual(decision["eligibility_status"], "BLOCKED")
        self.assertFalse(decision["eligible_for_owner_approval"])
        self.assertIn(first_required, decision["blocking_dimensions"])

    def test_required_not_verified_blocks_release(self):
        module = _load_module()
        policy = _load_policy(module)
        results = _all_pass_results(policy)
        first_required = next(item["id"] for item in policy["dimensions"] if item["required"])
        results[first_required] = "NOT_VERIFIED"

        decision = module.evaluate_release_gate_results(policy, results)

        self.assertEqual(decision["eligibility_status"], "BLOCKED")
        self.assertFalse(decision["eligible_for_owner_approval"])
        self.assertIn(first_required, decision["blocking_dimensions"])

    def test_all_required_pass_allows_eligibility_evaluation(self):
        module = _load_module()
        policy = _load_policy(module)
        decision = module.evaluate_release_gate_results(policy, _all_pass_results(policy))

        self.assertEqual(decision["eligibility_status"], "PASS")
        self.assertTrue(decision["eligible_for_owner_approval"])
        self.assertTrue(decision["owner_approval_required"])
        self.assertEqual(decision["owner_approval_scope"], "exact-commit-release")
        self.assertFalse(decision["release_authorized"])
        self.assertEqual(decision["blocking_dimensions"], [])

    def test_missing_required_results_fail_closed_as_not_verified(self):
        module = _load_module()
        policy = _load_policy(module)
        decision = module.evaluate_release_gate_results(policy, {})

        required = {item["id"] for item in policy["dimensions"] if item["required"]}
        self.assertFalse(decision["eligible_for_owner_approval"])
        self.assertEqual(set(decision["blocking_dimensions"]), required)
        self.assertEqual(
            {item["status"] for item in decision["dimension_results"] if item["id"] in required},
            {"NOT_VERIFIED"},
        )

    def test_optional_non_pass_does_not_block_when_explicitly_optional(self):
        module = _load_module()
        policy = copy.deepcopy(_load_policy(module))
        optional = policy["dimensions"][-1]
        optional["required"] = False
        module.validate_release_gate_policy(policy)
        results = _all_pass_results(policy)
        results[optional["id"]] = "PARTIAL"

        decision = module.evaluate_release_gate_results(policy, results)

        self.assertTrue(decision["eligible_for_owner_approval"])
        self.assertNotIn(optional["id"], decision["blocking_dimensions"])
        self.assertFalse(decision["release_authorized"])

    def test_policy_declares_complete_required_operational_dimensions(self):
        module = _load_module()
        policy = _load_policy(module)

        dimensions = {item["id"] for item in policy["dimensions"]}
        self.assertEqual(dimensions, EXPECTED_DIMENSIONS)
        self.assertTrue(all(item["required"] for item in policy["dimensions"]))
        self.assertEqual(
            policy["completion_statuses"],
            ["PASS", "PARTIAL", "BLOCKED", "NOT_VERIFIED"],
        )
        self.assertTrue(policy["eligibility"]["required_non_pass_blocks"])
        self.assertEqual(policy["eligibility"]["missing_required_status"], "NOT_VERIFIED")
        self.assertTrue(policy["eligibility"]["owner_approval_separate"])
        self.assertFalse(policy["eligibility"]["release_action_permitted"])

    def test_all_phase_10_findings_map_to_exactly_one_machine_gate(self):
        module = _load_module()
        policy = _load_policy(module)
        finding_document = json.loads(FINDINGS.read_text(encoding="utf-8"))
        expected = {item["id"] for item in finding_document["findings"]}
        mapped = [
            finding_id
            for dimension in policy["dimensions"]
            for finding_id in dimension["finding_ids"]
        ]

        self.assertEqual(set(mapped), expected)
        self.assertEqual(len(mapped), len(set(mapped)))

    def test_policy_does_not_embed_live_pass_results(self):
        module = _load_module()
        policy = _load_policy(module)
        forbidden = {"status", "current_status", "observed_status", "result"}
        for dimension in policy["dimensions"]:
            self.assertTrue(forbidden.isdisjoint(dimension))


if __name__ == "__main__":
    unittest.main()
