import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ADR = ROOT / "docs" / "architecture" / "0020-grimoire-2-canonical-requirement-model.md"
AUTHORING = ROOT / "standards" / "universal" / "standard-authoring.md"
HUMAN_TESTING = ROOT / "standards" / "engineering" / "testing.md"
MACHINE_TESTING = (
    ROOT
    / "registry"
    / "standards"
    / "universal-governance"
    / "GRIM-STD-0012.json"
)

REQUIRED_ADR_HEADINGS = {
    "Status",
    "Context",
    "Decision",
    "Machine normative authority",
    "Human rendering and parity",
    "Official-source authority",
    "Runtime adapters",
    "Compatibility and historical material",
    "Conflict handling",
    "Phase 11 executable parity gate contract",
    "Compatibility impact",
    "Consequences",
    "Non-goals",
}

REQUIRED_DECISION_SENTENCES = {
    "Machine registry and policy records are the canonical local normative authority.",
    "Human Markdown MUST NOT introduce, weaken, remove, or override normative semantics independently.",
    "Official external sources are authority records, not local controls until adopted through governed mapping.",
    "Runtime adapters are non-authoritative translations and MUST NOT alter requirement modality, scope, gates, or evidence.",
    "Compatibility and historical documents are non-normative by default.",
    "Same-level conflicts produce CONFLICTED and halt automatic resolution.",
}


def load_json(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise AssertionError(f"{path.relative_to(ROOT)} must contain a JSON object")
    return value


class Grimoire2CanonicalAuthorityTests(unittest.TestCase):
    def test_current_human_machine_drift_is_reproducible(self):
        authoring = AUTHORING.read_text(encoding="utf-8")
        required_sections = re.findall(r"^\d+\.\s+(.+)$", authoring, flags=re.MULTILINE)
        self.assertEqual(len(required_sections), 25)

        human = HUMAN_TESTING.read_text(encoding="utf-8")
        human_headings = set(re.findall(r"^##\s+(.+?)\s*$", human, flags=re.MULTILINE))
        missing_sections = [
            section for section in required_sections if section not in human_headings
        ]
        self.assertGreater(len(missing_sections), 0)

        machine = load_json(MACHINE_TESTING)
        self.assertEqual(machine.get("status"), "normative")
        self.assertEqual(machine.get("human_document"), "standards/engineering/testing.md")
        self.assertEqual(
            set(machine.get("contract", {})),
            {
                "expected_outcomes",
                "required_actions",
                "expected_documents",
                "acceptance",
                "verification",
                "evidence",
                "failure_conditions",
                "exceptions",
            },
        )

        # Reproducible Phase 10.2 evidence: the machine record is accepted as
        # normative while its human document is not a complete rendering of the
        # current authoring contract. Existing checks do not universally prove
        # semantic parity between these two surfaces.
        self.assertTrue(missing_sections)

    def test_adr_0020_locks_canonical_authority_and_parity_contract(self):
        self.assertTrue(ADR.is_file(), "ADR 0020 is missing")
        text = ADR.read_text(encoding="utf-8")
        headings = set(re.findall(r"^##\s+(.+?)\s*$", text, flags=re.MULTILINE))
        self.assertTrue(REQUIRED_ADR_HEADINGS.issubset(headings))
        for sentence in REQUIRED_DECISION_SENTENCES:
            self.assertIn(sentence, text)

    def test_adr_0020_defines_executable_phase_11_parity_failure(self):
        self.assertTrue(ADR.is_file(), "ADR 0020 is missing")
        text = ADR.read_text(encoding="utf-8")
        for token in (
            "PARITY_MISMATCH",
            "MISSING_HUMAN_RENDERING",
            "UNDECLARED_HUMAN_NORMATIVE_CONTENT",
            "MACHINE_CONTRACT_INCOMPLETE",
            "tests/fixtures/parity/",
            "checks/human_machine_parity_check.py",
        ):
            self.assertIn(token, text)

    def test_adr_0020_does_not_claim_phase_11_implementation(self):
        self.assertTrue(ADR.is_file(), "ADR 0020 is missing")
        text = ADR.read_text(encoding="utf-8")
        self.assertIn("Phase 11 implements this contract; Phase 10.2 does not.", text)


if __name__ == "__main__":
    unittest.main()
