import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AUDIT_ROOT = ROOT / "docs" / "audits" / "2026-07-27"
RUNNER = ROOT / "benchmarks" / "audit" / "2026-07-27" / "reproduce.py"
EXPECTED_COMMIT = "72015acac8a57146ad8b00a6c7b4725b8d86a9c8"
EXPECTED_FINDINGS = {
    "ai_operations_schema_contradiction",
    "dirty_output_retention",
    "false_project_readiness",
    "malformed_manifest_handling",
    "prompt_injection_rendering",
    "symlink_overwrite",
}


class AuditBaselineTests(unittest.TestCase):
    def reproducer_command(self, output: Path) -> list[str]:
        return [
            sys.executable,
            str(RUNNER),
            "--expected-commit",
            EXPECTED_COMMIT,
            "--seed",
            "20260727",
            "--output",
            str(output),
        ]

    def run_reproducer(self, output: Path) -> dict:
        completed = subprocess.run(
            self.reproducer_command(output),
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(
            completed.returncode,
            0,
            msg=f"stdout:\n{completed.stdout}\nstderr:\n{completed.stderr}",
        )
        summary_path = output / "reproduction-summary.json"
        self.assertTrue(summary_path.is_file())
        return json.loads(summary_path.read_text(encoding="utf-8"))

    def test_execution_package_is_complete_and_checksum_verified(self):
        package = AUDIT_ROOT / "execution-package"
        markdown_files = sorted(package.glob("[0-1][0-9]_*.md"))
        self.assertEqual(len(markdown_files), 19)
        checksum_file = package / "18_PACKAGE_CHECKSUMS.md"
        self.assertTrue(checksum_file.is_file())

        expected = {}
        for line in checksum_file.read_text(encoding="utf-8").splitlines():
            cells = [cell.strip().strip("`") for cell in line.split("|")]
            if len(cells) >= 4 and len(cells[2]) == 64:
                expected[cells[1]] = {
                    "sha256": cells[2],
                    "bytes": int(cells[3].replace(",", "")),
                }

        self.assertEqual(len(expected), 18)
        for name, declared in expected.items():
            content = (package / name).read_bytes()
            actual = hashlib.sha256(content).hexdigest()
            self.assertEqual(actual, declared["sha256"], msg=name)
            self.assertEqual(len(content), declared["bytes"], msg=name)

        baseline = json.loads(
            (AUDIT_ROOT / "BASELINE.json").read_text(encoding="utf-8")
        )
        self.assertEqual(
            hashlib.sha256(checksum_file.read_bytes()).hexdigest(),
            baseline["package_integrity"]["checksum_ledger_sha256"],
        )

    def test_reproducer_matches_known_failures_and_is_deterministic(self):
        with tempfile.TemporaryDirectory() as first_directory:
            first = self.run_reproducer(Path(first_directory).resolve())
        with tempfile.TemporaryDirectory() as second_directory:
            second = self.run_reproducer(Path(second_directory).resolve())

        self.assertEqual(first["reproduction_status"], "MATCH")
        self.assertEqual(first["audited_subject"]["commit"], EXPECTED_COMMIT)
        self.assertEqual(first["fresh_fuzz"]["seed"], 20260727)
        self.assertEqual(first["fresh_fuzz"]["cases"], 500)
        self.assertEqual(
            sum(first["fresh_fuzz"]["outcomes"].values()),
            first["fresh_fuzz"]["cases"],
        )
        self.assertEqual(
            first["source_fuzz_evidence"],
            {
                "classification": "HISTORICAL_REPORTED",
                "controlled_rejections": 171,
                "unhandled_exceptions": 214,
                "accepted": 115,
                "seed": "NOT_SUPPLIED",
                "raw_corpus": "NOT_SUPPLIED",
                "verification_status": "NOT_VERIFIED",
            },
        )

        findings = {item["id"]: item for item in first["findings"]}
        self.assertEqual(set(findings), EXPECTED_FINDINGS)
        for finding in findings.values():
            self.assertEqual(finding["reproduction_status"], "MATCH")
            self.assertEqual(finding["product_status"], "FAIL")

        self.assertEqual(first["normalized_results"], second["normalized_results"])
        self.assertEqual(first["fresh_fuzz"], second["fresh_fuzz"])
        self.assertEqual(first["audited_inputs"]["status"], "PASS")

    def test_reproducer_rejects_symlinked_evidence_file(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            output = root / "evidence"
            output.mkdir()
            target = root / "outside-target.json"
            sentinel = "AUDIT_SENTINEL\n"
            target.write_text(sentinel, encoding="utf-8")
            (output / "environment.json").symlink_to(target)

            completed = subprocess.run(
                self.reproducer_command(output),
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(completed.returncode, 2)
            self.assertEqual(target.read_text(encoding="utf-8"), sentinel)
            self.assertTrue((output / "environment.json").is_symlink())

    def test_reproducer_rejects_symlinked_parent_component(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            external = root / "external"
            external.mkdir()
            linked_parent = root / "linked-parent"
            linked_parent.symlink_to(external, target_is_directory=True)
            output = linked_parent / "evidence"

            completed = subprocess.run(
                self.reproducer_command(output),
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(completed.returncode, 2)
            self.assertFalse((external / "evidence").exists())

    def test_canonical_baseline_preserves_audited_score_without_rescoring(self):
        baseline = json.loads(
            (AUDIT_ROOT / "BASELINE.json").read_text(encoding="utf-8")
        )
        self.assertEqual(baseline["audited_score"], 5.4)
        self.assertEqual(baseline["audited_score_scale"], 10)
        self.assertEqual(baseline["current_rescore"], "NOT_PERFORMED")
        self.assertEqual(baseline["release_assurance"], "NOT_VERIFIED")
        self.assertEqual(baseline["plan_id"], "GRM-1.0-P0P1-2026-07-27")
        self.assertEqual(baseline["plan_revision"], 1)

    def test_repository_index_registers_audit_baseline(self):
        index = json.loads(
            (ROOT / "REPOSITORY_INDEX.json").read_text(encoding="utf-8")
        )
        self.assertEqual(
            index["artifacts"]["audit_baseline_2026_07_27"],
            "docs/audits/2026-07-27/BASELINE.json",
        )


if __name__ == "__main__":
    unittest.main()
