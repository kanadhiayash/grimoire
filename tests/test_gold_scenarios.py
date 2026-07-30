from __future__ import annotations

import hashlib
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from grimoire.benchmarks import load_gold_scenarios, run_gold_scenarios


class GoldScenarioTests(unittest.TestCase):
    def test_minimum_product_matrix_runs_through_compiler_and_verifier(self):
        scenarios = load_gold_scenarios(
            ROOT / "benchmarks" / "scenarios" / "gold" / "scenarios.json"
        )
        self.assertGreaterEqual(len(scenarios), 15)
        self.assertTrue(
            {
                "simple-static-website",
                "public-marketing-analytics",
                "authenticated-b2b-saas",
                "consumer-mobile-application",
                "fintech-mobile-location",
                "health-regulated",
                "health-non-regulated",
                "child-directed-social",
                "eu-consumer-ai-assistant",
                "california-subscription-automated-decisions",
                "public-sector-accessible-service",
                "api-platform",
                "marketplace-user-generated-content",
                "connected-product",
                "internal-enterprise-tool",
                "agentic-automation-external-tools",
            }.issubset({item["id"] for item in scenarios})
        )
        report = run_gold_scenarios(scenarios, root=ROOT)
        self.assertEqual(report["case_count"], len(scenarios))
        self.assertEqual(report["compiler_failures"], 0)
        self.assertEqual(report["verifier_failures"], 0)
        self.assertEqual(report["control_set_mismatches"], 0)
        self.assertEqual(report["critical_control_recall"], 1.0)
        self.assertEqual(report["critical_false_non_applicability"], 0)
        self.assertEqual(report["false_compliance_claims"], 0)

    def test_expectations_cover_all_required_contract_fields(self):
        scenarios = load_gold_scenarios(
            ROOT / "benchmarks" / "scenarios" / "gold" / "scenarios.json"
        )
        required = {
            "control_state_sha256",
            "selected_count",
            "excluded_count",
            "uncertain_count",
            "conflicted_count",
            "required_documents",
            "required_evidence_sha256",
            "required_evidence_count",
            "counsel_questions",
            "expected_status",
            "critical_controls",
        }
        for scenario in scenarios:
            self.assertEqual(set(scenario["expected"]), required)
            self.assertEqual(scenario["expected"]["expected_status"], "NOT_VERIFIED")

    def test_fixture_source_manifest_detects_unreviewed_rewrites(self):
        fixture = (
            ROOT / "benchmarks" / "scenarios" / "gold" / "scenarios.json"
        )
        manifest = json.loads(
            (
                ROOT / "benchmarks" / "scenarios" / "gold" / "SOURCE_MANIFEST.json"
            ).read_text(encoding="utf-8")
        )
        self.assertEqual(
            manifest,
            {
                "schema_version": 1,
                "path": "benchmarks/scenarios/gold/scenarios.json",
                "sha256": hashlib.sha256(fixture.read_bytes()).hexdigest(),
                "review_boundary": "fixture_changes_require_separate_review",
            },
        )


if __name__ == "__main__":
    unittest.main()
