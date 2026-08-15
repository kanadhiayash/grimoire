import importlib.util
import re
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from grimoire.status import StatusDimension  # noqa: E402


ADR = ROOT / "docs" / "architecture" / "0021-grimoire-2-compatibility-and-runtime-boundary.md"
ORCHESTRATOR = ROOT / "scripts" / "project_orchestrator.py"

REQUIRED_ADR_HEADINGS = {
    "Status",
    "Context",
    "Decision",
    "Grimoire 2.0 universal execution contract",
    "Shiroe adapter boundary",
    "Grimoire 1.x compatibility mode",
    "Zeref isolation",
    "Breaking changes",
    "Fail-closed migration rules",
    "Compatibility sunset",
    "Historical evidence",
    "Compatibility impact",
    "Consequences",
    "Non-goals",
}

REQUIRED_SENTENCES = {
    "The target major release is 2.0.0.",
    "Grimoire 2.0 universal outputs use runtime-neutral execution contracts.",
    "Shiroe integration is an adapter and does not make Shiroe behavior part of Grimoire's universal standard model.",
    "Grimoire 1.x packs remain verifiable only through explicit compatibility mode.",
    "The Grimoire 2.0 compiler MUST NOT emit active Zeref filenames, Zeref status dimensions, or Zeref runtime ownership.",
    "Compatibility MUST NOT become the default v2 execution path.",
    "No migration may weaken a Grimoire control.",
}


def load_orchestrator_module():
    spec = importlib.util.spec_from_file_location("grimoire_phase10_v1_orchestrator", ORCHESTRATOR)
    if spec is None or spec.loader is None:
        raise AssertionError("cannot load project orchestrator")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Grimoire2RuntimeBoundaryTests(unittest.TestCase):
    def test_current_v1_output_contract_exposes_zeref_universal_artifacts(self):
        module = load_orchestrator_module()
        self.assertIn("ZEREF_EXECUTION_PROFILE.json", module.OUTPUT_FILES)
        self.assertIn(
            StatusDimension.ZEREF_EXECUTION_STATUS,
            set(StatusDimension),
        )

        text = ORCHESTRATOR.read_text(encoding="utf-8")
        self.assertIn("Zeref routes execution.", text)
        self.assertRegex(text, r"from grimoire\.zeref import")

    def test_adr_0021_locks_v2_runtime_neutrality_and_compatibility(self):
        self.assertTrue(ADR.is_file(), "ADR 0021 is missing")
        text = ADR.read_text(encoding="utf-8")
        headings = set(re.findall(r"^##\s+(.+?)\s*$", text, flags=re.MULTILINE))
        self.assertTrue(REQUIRED_ADR_HEADINGS.issubset(headings))
        for sentence in REQUIRED_SENTENCES:
            self.assertIn(sentence, text)

    def test_adr_0021_enumerates_breaking_zeref_removals(self):
        self.assertTrue(ADR.is_file(), "ADR 0021 is missing")
        text = ADR.read_text(encoding="utf-8")
        for token in (
            "ZEREF_EXECUTION_PROFILE.json",
            "ZEREF_EXECUTION_STATUS",
            "zeref.mode",
            "zeref.cost_ceiling",
            "EXECUTION_PROFILE.json",
            "EXECUTION_STATUS",
            "compatibility_mode",
            "v1_zeref",
        ):
            self.assertIn(token, text)

    def test_adr_0021_defines_fail_closed_compatibility_mapping(self):
        self.assertTrue(ADR.is_file(), "ADR 0021 is missing")
        text = ADR.read_text(encoding="utf-8")
        for token in (
            "UNMAPPABLE_LEGACY_CONTROL",
            "AMBIGUOUS_RUNTIME_OWNERSHIP",
            "COMPATIBILITY_NOT_EXPLICIT",
            "CONTROL_WEAKENING_DETECTED",
            "tests/fixtures/compatibility/",
            "checks/grimoire_2_compatibility_check.py",
        ):
            self.assertIn(token, text)
        self.assertIn("Phase 12 implements this migration contract; Phase 10.3 does not.", text)


if __name__ == "__main__":
    unittest.main()
