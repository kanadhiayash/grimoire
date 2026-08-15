import json
import re
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CHECKS = ROOT / "checks"
if str(CHECKS) not in sys.path:
    sys.path.insert(0, str(CHECKS))

from grimoire_2_findings_check import validate_findings  # noqa: E402


FINDINGS_PATH = ROOT / "docs" / "audits" / "2026-08-15" / "FINDINGS.json"
FINDING_SCHEMA = ROOT / "policies" / "schemas" / "audit-finding.schema.json"
OBSERVED_REPOSITORY_VISIBILITY = "public"

EXPECTED_FINDINGS = {
    "GRM2-P10-001": "repository_metadata",
    "GRM2-P10-002": "runtime_boundary",
    "GRM2-P10-003": "standard_authoring_enforcement",
    "GRM2-P10-004": "stack_overlay_migration",
    "GRM2-P10-005": "official_source_provenance",
}

ACTIVE_ZEREF_SCAN_PATHS = (
    "AGENTS.md",
    "README.md",
    "REPOSITORY_INDEX.json",
    "policies",
    "standards",
    "adapters",
    "src",
    "templates",
    "checks",
)


def load_json(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise AssertionError(f"{path.relative_to(ROOT)} must contain a JSON object")
    return value


def load_findings() -> dict[str, dict]:
    if not FINDINGS_PATH.is_file():
        return {}
    document = load_json(FINDINGS_PATH)
    return {
        item["id"]: item
        for item in document.get("findings", [])
        if isinstance(item, dict) and isinstance(item.get("id"), str)
    }


def assert_open_finding(testcase: unittest.TestCase, finding_id: str, gate: str) -> None:
    findings = load_findings()
    testcase.assertIn(finding_id, findings, msg=f"missing baseline finding {finding_id}")
    testcase.assertEqual(findings[finding_id].get("status"), "OPEN")
    testcase.assertEqual(findings[finding_id].get("affected_gate"), gate)


class Grimoire2BaselineTests(unittest.TestCase):
    def test_baseline_finding_artifacts_exist(self):
        self.assertTrue(FINDINGS_PATH.is_file(), "Phase 10 finding register is missing")
        self.assertTrue(FINDING_SCHEMA.is_file(), "audit finding schema is missing")

    def test_finding_register_passes_dependency_free_checker(self):
        self.assertEqual(validate_findings(), [])

    def test_repository_visibility_matches_observed_public_state(self):
        index = load_json(ROOT / "REPOSITORY_INDEX.json")
        self.assertEqual(index.get("visibility"), OBSERVED_REPOSITORY_VISIBILITY)

    def test_active_zeref_runtime_references_are_registered_as_open_debt(self):
        matches: list[str] = []
        for relative in ACTIVE_ZEREF_SCAN_PATHS:
            path = ROOT / relative
            candidates = [path] if path.is_file() else path.rglob("*")
            for candidate in candidates:
                if not candidate.is_file() or candidate.suffix.lower() not in {".md", ".json", ".py"}:
                    continue
                text = candidate.read_text(encoding="utf-8", errors="ignore")
                if re.search(r"\bZeref\b|\bZEREF_", text):
                    matches.append(str(candidate.relative_to(ROOT)))

        self.assertGreater(len(matches), 0, "baseline unexpectedly has no active Zeref references")
        assert_open_finding(self, "GRM2-P10-002", "runtime_boundary")

    def test_normative_authoring_gap_is_registered_as_open_debt(self):
        authoring = (ROOT / "standards" / "universal" / "standard-authoring.md").read_text(encoding="utf-8")
        required_sections = re.findall(r"^\d+\.\s+(.+)$", authoring, flags=re.MULTILINE)
        self.assertEqual(len(required_sections), 25)

        inventory = load_json(ROOT / "inventory" / "standards-classification.json")
        incomplete: list[str] = []
        for item in inventory.get("documents", []):
            if item.get("classification") != "NORMATIVE":
                continue
            relative = item.get("path")
            if not isinstance(relative, str):
                continue
            text = (ROOT / relative).read_text(encoding="utf-8")
            headings = set(re.findall(r"^##\s+(.+?)\s*$", text, flags=re.MULTILINE))
            if any(section not in headings for section in required_sections):
                incomplete.append(relative)

        self.assertGreater(len(incomplete), 0, "baseline unexpectedly has no authoring gap")
        assert_open_finding(
            self,
            "GRM2-P10-003",
            "standard_authoring_enforcement",
        )

    def test_four_stack_overlays_remain_migration_required_and_are_registered(self):
        inventory = load_json(ROOT / "inventory" / "standards-classification.json")
        migration_required = [
            item["path"]
            for item in inventory.get("documents", [])
            if item.get("domain") == "stack-overlays"
            and item.get("review_status") == "MIGRATION_REQUIRED"
        ]
        self.assertEqual(len(migration_required), 4)
        assert_open_finding(self, "GRM2-P10-004", "stack_overlay_migration")

    def test_official_source_provenance_gap_is_registered_as_open_debt(self):
        official_sources = 0
        for path in sorted((ROOT / "registry" / "sources").rglob("*.json")):
            value = load_json(path)
            for source in value.get("sources", []):
                if isinstance(source, dict) and source.get("source_type") == "official_source":
                    official_sources += 1

        self.assertEqual(
            official_sources,
            0,
            "baseline expectation changed: official source records now exist and finding must be re-audited",
        )
        assert_open_finding(
            self,
            "GRM2-P10-005",
            "official_source_provenance",
        )

    def test_required_baseline_findings_have_stable_gate_mapping(self):
        findings = load_findings()
        for finding_id, gate in EXPECTED_FINDINGS.items():
            self.assertIn(finding_id, findings)
            self.assertEqual(findings[finding_id].get("affected_gate"), gate)


if __name__ == "__main__":
    unittest.main()
