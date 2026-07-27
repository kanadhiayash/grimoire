import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class InstructionBoundaryTests(unittest.TestCase):
    def test_neutral_instructions_exclude_personal_identity(self):
        forbidden = ("Yash", "Kanadhia", "Mavis", "Toronto")
        for path in (ROOT / "instructions/global").glob("*.md"):
            text = path.read_text(encoding="utf-8")
            for term in forbidden:
                self.assertNotIn(term, text, path)

    def test_personal_overlay_is_explicitly_excluded(self):
        manifest = json.loads((ROOT / "instructions/global/manifest.json").read_text(encoding="utf-8"))
        self.assertIn("../personal/", manifest["excluded_from_neutral_packs"])

    def test_standard_template_has_all_required_sections(self):
        text = (ROOT / "templates/standards/STANDARD.md").read_text(encoding="utf-8")
        headings = [
            "Purpose", "Expected outcome", "Applicability", "Non-applicability",
            "Required inputs", "Unknowns to resolve", "Required actions",
            "Required decisions", "Required details", "Expected documents and artifacts",
            "Document structure", "Acceptance criteria", "Verification method",
            "Evidence required", "Failure conditions", "Risks and abuse cases",
            "Guards and limits", "Exceptions", "Cost considerations", "Dependencies",
            "Related standards", "Source provenance", "Owner and review cycle",
            "Zeref execution behavior", "Examples", "Anti-patterns",
        ]
        for heading in headings:
            self.assertIn(f"## {heading}", text)

    def test_legal_policy_forbids_automated_compliance_status(self):
        policy = json.loads((ROOT / "policies/standards-orchestrator.json").read_text(encoding="utf-8"))
        self.assertNotIn("COMPLIANT", policy["applicability_statuses"])


if __name__ == "__main__":
    unittest.main()
