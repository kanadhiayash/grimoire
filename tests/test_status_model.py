import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from grimoire.status import (
    CompletionStatus,
    StatusDimension,
    StatusReport,
    StatusResult,
    aggregate_status,
    conservative_legacy_status,
)


MANDATORY_DIMENSIONS = {
    "PACK_GENERATION_STATUS",
    "MANIFEST_VALIDATION_STATUS",
    "APPLICABILITY_STATUS",
    "CONTROL_VERIFICATION_STATUS",
    "PROJECT_READINESS_STATUS",
    "RELEASE_ASSURANCE_STATUS",
    "LEGAL_REVIEW_STATUS",
    "ZEREF_EXECUTION_STATUS",
}


class StatusModelTests(unittest.TestCase):
    def result(
        self,
        dimension: StatusDimension,
        status: CompletionStatus = CompletionStatus.PASS,
    ) -> StatusResult:
        return StatusResult(
            dimension=dimension,
            status=status,
            reason_codes=("test_evidence",),
        )

    def complete_results(self) -> dict[StatusDimension, StatusResult]:
        return {
            dimension: self.result(dimension) for dimension in StatusDimension
        }

    def test_mandatory_dimensions_are_exact(self):
        self.assertEqual(
            {dimension.value for dimension in StatusDimension},
            MANDATORY_DIMENSIONS,
        )

    def test_status_report_requires_every_dimension(self):
        results = self.complete_results()
        results.pop(StatusDimension.LEGAL_REVIEW_STATUS)
        with self.assertRaisesRegex(ValueError, "missing status dimensions"):
            StatusReport(results)

    def test_blocked_dimension_dominates_aggregate(self):
        statuses = [
            CompletionStatus.PASS,
            CompletionStatus.PARTIAL,
            CompletionStatus.NOT_VERIFIED,
            CompletionStatus.BLOCKED,
        ]
        self.assertEqual(aggregate_status(statuses), CompletionStatus.BLOCKED)

    def test_not_verified_dominates_partial_and_pass(self):
        self.assertEqual(
            aggregate_status(
                [
                    CompletionStatus.PASS,
                    CompletionStatus.PARTIAL,
                    CompletionStatus.NOT_VERIFIED,
                ]
            ),
            CompletionStatus.NOT_VERIFIED,
        )

    def test_pack_pass_cannot_raise_project_or_release_status(self):
        results = self.complete_results()
        results[StatusDimension.PROJECT_READINESS_STATUS] = self.result(
            StatusDimension.PROJECT_READINESS_STATUS,
            CompletionStatus.NOT_VERIFIED,
        )
        results[StatusDimension.RELEASE_ASSURANCE_STATUS] = self.result(
            StatusDimension.RELEASE_ASSURANCE_STATUS,
            CompletionStatus.NOT_VERIFIED,
        )
        report = StatusReport(results)

        self.assertEqual(
            report.results[StatusDimension.PACK_GENERATION_STATUS].status,
            CompletionStatus.PASS,
        )
        self.assertEqual(report.aggregate, CompletionStatus.NOT_VERIFIED)

    def test_compliant_is_rejected_from_legal_status(self):
        with self.assertRaises(ValueError):
            StatusResult(
                dimension=StatusDimension.LEGAL_REVIEW_STATUS,
                status="COMPLIANT",
                reason_codes=("automated_legal_claim_forbidden",),
            )

    def test_legacy_single_status_is_conservative(self):
        self.assertEqual(
            conservative_legacy_status("PASS"),
            CompletionStatus.NOT_VERIFIED,
        )
        self.assertEqual(
            conservative_legacy_status("PARTIAL"),
            CompletionStatus.NOT_VERIFIED,
        )
        self.assertEqual(
            conservative_legacy_status("BLOCKED"),
            CompletionStatus.BLOCKED,
        )
        self.assertEqual(
            conservative_legacy_status("NOT_VERIFIED"),
            CompletionStatus.NOT_VERIFIED,
        )

    def test_status_schemas_require_every_dimension(self):
        for name in ("project-status.schema.json", "execution-receipt.schema.json"):
            schema = json.loads(
                (ROOT / "policies" / "schemas" / name).read_text(encoding="utf-8")
            )
            dimensions = schema["$defs"]["statusReport"]["properties"][
                "dimensions"
            ]
            self.assertEqual(set(dimensions["required"]), MANDATORY_DIMENSIONS)
            self.assertFalse(dimensions["additionalProperties"])


if __name__ == "__main__":
    unittest.main()
