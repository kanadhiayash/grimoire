from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from grimoire.applicability import (  # noqa: E402
    ApplicabilityDecision,
    DecisionState,
    ProfileResolutionError,
    resolve_applicability,
)
from grimoire.registry import load_standard_registry  # noqa: E402
from scripts.project_orchestrator import validate_manifest  # noqa: E402


SCENARIOS = ROOT / "benchmarks" / "scenarios" / "phase3-applicability"


class ApplicabilityResolverTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.registry = load_standard_registry(
            ROOT / "registry" / "standards",
            root=ROOT,
        )

    def scenario(self, name: str) -> dict[str, object]:
        return json.loads((SCENARIOS / name / "manifest.json").read_text("utf-8"))

    def expected(self, name: str) -> dict[str, object]:
        return json.loads(
            (SCENARIOS / name / "expected-controls.json").read_text("utf-8")
        )

    def test_first_five_gold_scenarios_match_expected_control_sets(self):
        for directory in sorted(path for path in SCENARIOS.iterdir() if path.is_dir()):
            with self.subTest(scenario=directory.name):
                report = resolve_applicability(
                    validate_manifest(self.scenario(directory.name)),
                    self.registry,
                )
                expected = self.expected(directory.name)
                self.assertEqual(report.to_dict()["selected"], expected["selected"])
                self.assertEqual(report.to_dict()["excluded"], expected["excluded"])
                self.assertEqual(report.to_dict()["uncertain"], expected["uncertain"])
                self.assertEqual(report.to_dict()["conflicted"], expected["conflicted"])

    def test_decisions_are_deterministic_and_preserve_registry_identity(self):
        manifest = validate_manifest(self.scenario("05-fintech-mobile-location"))
        first = resolve_applicability(manifest, self.registry)
        second = resolve_applicability(manifest, self.registry)

        self.assertEqual(first.to_dict(), second.to_dict())
        self.assertEqual(
            [decision.standard_id for decision in first.decisions],
            sorted(self.registry),
        )
        for decision in first.decisions:
            self.assertIsInstance(decision, ApplicabilityDecision)
            self.assertEqual(decision.version, self.registry[decision.standard_id].version)
            self.assertEqual(
                decision.provenance,
                dict(self.registry[decision.standard_id].provenance),
            )
            self.assertTrue(decision.reason_codes)

    def test_missing_material_fact_is_uncertain_not_false_non_applicability(self):
        records = dict(self.registry)
        records["GRIM-STD-0999"] = self._record(
            "GRIM-STD-0999",
            {"field": "industry", "op": "equals", "value": "financial-services"},
        )

        report = resolve_applicability(
            validate_manifest(self.scenario("01-static-site")),
            records,
        )
        decision = report.by_id("GRIM-STD-0999")

        self.assertEqual(decision.state, DecisionState.UNCERTAIN)
        self.assertIn("missing_fact", decision.reason_codes)
        self.assertEqual(decision.missing_facts, ("industry",))

    def test_profile_cycle_and_ambiguous_overlay_fail_deterministically(self):
        manifest = validate_manifest(self.scenario("01-static-site"))
        with self.assertRaises(ProfileResolutionError) as cycle:
            resolve_applicability(
                manifest,
                self.registry,
                profiles={
                    "one": {"parents": ["two"], "facts": {}},
                    "two": {"parents": ["one"], "facts": {}},
                },
                active_profiles=("one",),
            )
        self.assertEqual(cycle.exception.reason_codes, ("profile_cycle",))

        report = resolve_applicability(
            manifest,
            self.registry,
            overlays=(
                {"id": "one", "facts": {"industry": "retail"}},
                {"id": "two", "facts": {"industry": "health"}},
            ),
        )
        self.assertTrue(report.conflicts)
        self.assertEqual(
            report.conflicts[0]["path"],
            "industry",
        )

    def test_approved_exception_preserves_provenance_and_review(self):
        manifest = validate_manifest(self.scenario("05-fintech-mobile-location"))
        report = resolve_applicability(
            manifest,
            self.registry,
            exceptions=(
                {
                    "standard_id": "GRIM-STD-0004",
                    "approved_by": "named-owner",
                    "reason": "temporarily not user-facing",
                    "review_required": True,
                },
            ),
        )
        decision = report.by_id("GRIM-STD-0004")

        self.assertEqual(decision.state, DecisionState.EXCLUDED)
        self.assertEqual(
            decision.reason_codes,
            ("approved_exception", "review_required"),
        )
        self.assertEqual(decision.provenance["source_id"], self.registry[decision.standard_id].provenance["source_id"])
        self.assertTrue(decision.review_required)

    def test_invalid_injected_predicate_is_conflicted_not_an_exception(self):
        records = dict(self.registry)
        records["GRIM-STD-0998"] = self._record(
            "GRIM-STD-0998",
            {"field": "industry", "op": "unknown"},
        )

        report = resolve_applicability(
            validate_manifest(self.scenario("01-static-site")),
            records,
        )

        decision = report.by_id("GRIM-STD-0998")
        self.assertEqual(decision.state, DecisionState.CONFLICTED)
        self.assertEqual(decision.reason_codes, ("invalid_predicate",))

    def _record(self, standard_id: str, applicability: dict[str, object]):
        from grimoire.registry.standards import StandardRecord

        base = self.registry["GRIM-STD-0001"]
        return StandardRecord(
            id=standard_id,
            version=base.version,
            status=base.status,
            domain=base.domain,
            requirement_level=base.requirement_level,
            title="Synthetic missing-fact control",
            owner=base.owner,
            review_date=base.review_date,
            human_document=base.human_document,
            provenance=base.provenance,
            applicability=applicability,
        )


if __name__ == "__main__":
    unittest.main()
