from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from grimoire.predicates import PredicateValidationError, evaluate_predicate


class PredicateEngineTests(unittest.TestCase):
    def context(self):
        return {
            "project": {
                "lifecycle_stage": "BUILD_READY",
                "product_types": ["consumer-mobile"],
            },
            "platforms": ["web", "ios"],
            "markets": ["Canada"],
            "ai": {"user_facing": True, "external_models": False},
            "data": {"personal_data": True},
        }

    def test_allowed_operations_return_stable_trace(self):
        predicate = {
            "all": [
                {
                    "field": "project.lifecycle_stage",
                    "op": "equals",
                    "value": "BUILD_READY",
                },
                {"field": "platforms", "op": "contains", "value": "web"},
                {"field": "markets", "op": "non_empty"},
                {"field": "data.personal_data", "op": "exists"},
            ]
        }

        first = evaluate_predicate(predicate, self.context())
        second = evaluate_predicate(predicate, self.context())

        self.assertTrue(first.result)
        self.assertEqual(first.to_dict(), second.to_dict())
        self.assertEqual(first.trace["op"], "all")
        self.assertEqual(first.reason_codes, ("predicate_matched",))

    def test_unknown_operator_and_malformed_operands_fail_closed(self):
        for predicate in (
            {"field": "ai.user_facing", "op": "exec", "value": True},
            {"field": "ai.user_facing", "op": "equals"},
            {"field": "ai.user_facing", "op": "in", "value": "yes"},
            {"field": "ai.user_facing", "op": "exists", "value": True},
        ):
            with self.subTest(predicate=predicate):
                with self.assertRaises(PredicateValidationError) as raised:
                    evaluate_predicate(predicate, self.context())
                self.assertIn("invalid_predicate", raised.exception.reason_codes)

    def test_membership_does_not_use_ambiguous_type_coercion(self):
        context = {
            "flags": [1],
            "answer": True,
        }

        contains = evaluate_predicate(
            {"field": "flags", "op": "contains", "value": True},
            context,
        )
        member = evaluate_predicate(
            {"field": "answer", "op": "in", "value": [1]},
            context,
        )

        self.assertFalse(contains.result)
        self.assertFalse(member.result)

    def test_predicate_cannot_call_functions_or_perform_io(self):
        predicate = {
            "field": "__import__('os').system",
            "op": "call",
            "value": "touch /tmp/not-allowed",
        }

        with self.assertRaises(PredicateValidationError) as raised:
            evaluate_predicate(predicate, self.context())

        self.assertIn("unsupported_operator", raised.exception.reason_codes)

    def test_depth_and_collection_limits_are_enforced(self):
        deep = {"not": {"not": {"not": {"not": {"not": {"not": {"not": {"not": {"not": {"field": "markets", "op": "non_empty"}}}}}}}}}}
        too_many = {"any": [{"field": "markets", "op": "non_empty"}] * 65}

        for predicate in (deep, too_many):
            with self.subTest(predicate=predicate):
                with self.assertRaises(PredicateValidationError) as raised:
                    evaluate_predicate(predicate, self.context())
                self.assertIn("predicate_limit_exceeded", raised.exception.reason_codes)


if __name__ == "__main__":
    unittest.main()
