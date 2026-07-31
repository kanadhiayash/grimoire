from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from grimoire.benchmarks.runner import run_benchmark_suite  # noqa: E402
from grimoire.release.evidence import (  # noqa: E402
    ReleaseEvidenceError,
    build_release_evidence,
    release_evidence_digest,
    rollback_dry_run,
    verify_release_evidence,
)


class ReleaseEvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        (ROOT / "artifacts").mkdir(exist_ok=True)

    @staticmethod
    def _head() -> str:
        return subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        ).stdout.strip()

    def _inputs(self, directory: Path) -> tuple[Path, Path]:
        artifact = directory / "artifact.json"
        artifact.write_text('{"status":"PASS"}\n', encoding="utf-8")
        benchmark_root = directory / "benchmark"
        run_benchmark_suite(
            {
                "schema_version": 1,
                "suite_id": "release-evidence-test",
                "sources": [str(artifact.relative_to(ROOT))],
                "cases": [
                    {
                        "id": "controlled-pass",
                        "command": [
                            sys.executable,
                            "-c",
                            "print('release evidence benchmark')",
                        ],
                        "hard_gate": True,
                    }
                ],
            },
            root=ROOT,
            output=benchmark_root,
            commit=self._head(),
        )
        return artifact, benchmark_root / "BENCHMARK_RESULTS.json"

    def test_reproducible_evidence_is_bound_but_release_not_verified(self) -> None:
        with tempfile.TemporaryDirectory(dir=ROOT / "artifacts") as directory:
            artifact, benchmark = self._inputs(Path(directory))
            first = build_release_evidence(
                ROOT,
                artifacts=[artifact],
                benchmarks=[benchmark],
                expected_commit=self._head(),
                timestamp="2026-07-31T02:00:00+00:00",
            )
            second = build_release_evidence(
                ROOT,
                artifacts=[artifact],
                benchmarks=[benchmark],
                expected_commit=self._head(),
                timestamp="2026-07-31T02:00:00+00:00",
            )
            result = verify_release_evidence(
                first,
                root=ROOT,
                expected_commit=self._head(),
            )

        self.assertEqual(first, second)
        self.assertEqual(result["verification_status"], "PASS")
        self.assertEqual(result["release_assurance_status"], "NOT_VERIFIED")
        self.assertIn("release_approval_missing", result["reason_codes"])
        self.assertIn("signature_not_verified", result["reason_codes"])

    def test_commit_artifact_signature_and_benchmark_mismatch_fail(self) -> None:
        with tempfile.TemporaryDirectory(dir=ROOT / "artifacts") as directory:
            artifact, benchmark = self._inputs(Path(directory))
            evidence = build_release_evidence(
                ROOT,
                artifacts=[artifact],
                benchmarks=[benchmark],
                expected_commit=self._head(),
                timestamp="2026-07-31T02:00:00+00:00",
            )
            artifact.write_text('{"status":"FAIL"}\n', encoding="utf-8")
            result = verify_release_evidence(
                evidence,
                root=ROOT,
                expected_commit="f" * 40,
            )
            self.assertEqual(result["verification_status"], "FAIL")
            self.assertIn("source_commit_mismatch", result["reason_codes"])
            self.assertIn("artifact_hash_mismatch", result["reason_codes"])

            artifact.write_text('{"status":"PASS"}\n', encoding="utf-8")
            benchmark.write_text('{"verdict":"FAIL"}\n', encoding="utf-8")
            result = verify_release_evidence(
                evidence,
                root=ROOT,
                expected_commit=self._head(),
            )
            self.assertIn("benchmark_record_invalid", result["reason_codes"])

            evidence["signature"]["status"] = "PASS"
            evidence["integrity"]["digest"] = release_evidence_digest(evidence)
            result = verify_release_evidence(
                evidence,
                root=ROOT,
                expected_commit=self._head(),
            )
        self.assertIn("unsupported_signature_claim", result["reason_codes"])

    def test_permission_scope_forbids_sign_publish_and_deploy(self) -> None:
        with tempfile.TemporaryDirectory(dir=ROOT / "artifacts") as directory:
            artifact, benchmark = self._inputs(Path(directory))
            evidence = build_release_evidence(
                ROOT,
                artifacts=[artifact],
                benchmarks=[benchmark],
                expected_commit=self._head(),
                timestamp="2026-07-31T02:00:00+00:00",
            )

        self.assertEqual(
            evidence["permissions"]["allowed"],
            ["generate-evidence", "rollback-dry-run", "verify-evidence"],
        )
        self.assertEqual(
            evidence["permissions"]["prohibited"],
            ["deploy", "publish", "release", "sign"],
        )

    def test_private_rollback_dry_run_is_non_mutating(self) -> None:
        with tempfile.TemporaryDirectory(dir=ROOT / "artifacts") as directory:
            artifact, benchmark = self._inputs(Path(directory))
            evidence = build_release_evidence(
                ROOT,
                artifacts=[artifact],
                benchmarks=[benchmark],
                expected_commit=self._head(),
                timestamp="2026-07-31T02:00:00+00:00",
            )
            before = artifact.read_bytes()
            result = rollback_dry_run(
                evidence,
                root=ROOT,
                expected_commit=self._head(),
            )
            after = artifact.read_bytes()

        self.assertEqual(result["status"], "PASS")
        self.assertFalse(result["executed"])
        self.assertEqual(before, after)
        self.assertNotIn("git reset", " ".join(result["steps"]))

    def test_malformed_or_empty_records_fail_with_controlled_reasons(self) -> None:
        with tempfile.TemporaryDirectory(dir=ROOT / "artifacts") as directory:
            artifact, benchmark = self._inputs(Path(directory))
            evidence = build_release_evidence(
                ROOT,
                artifacts=[artifact],
                benchmarks=[benchmark],
                expected_commit=self._head(),
                timestamp="2026-07-31T02:00:00+00:00",
            )

            cases = (
                ("schema_id", "not-grimoire", "release_schema_mismatch"),
                ("created_at", "not-a-timestamp", "release_timestamp_invalid"),
                ("environment", None, "environment_record_invalid"),
                ("artifacts", None, "artifact_records_invalid"),
                ("artifacts", [], "artifact_records_missing"),
                ("benchmarks", None, "benchmark_records_invalid"),
                ("benchmarks", [], "benchmark_records_missing"),
                ("approvals", None, "approval_records_invalid"),
            )
            for key, value, reason in cases:
                with self.subTest(key=key, value=value):
                    malformed = json.loads(json.dumps(evidence))
                    malformed[key] = value
                    malformed["integrity"]["digest"] = release_evidence_digest(
                        malformed
                    )
                    result = verify_release_evidence(
                        malformed,
                        root=ROOT,
                        expected_commit=self._head(),
                    )
                    self.assertEqual(result["verification_status"], "FAIL")
                    self.assertIn(reason, result["reason_codes"])

    def test_schema_closes_every_nested_release_record(self) -> None:
        schema = json.loads(
            (ROOT / "policies/schemas/release-evidence.schema.json").read_text(
                encoding="utf-8"
            )
        )
        for name in (
            "environment",
            "artifact",
            "benchmark",
            "approval",
            "permissions",
            "signature",
            "integrity",
        ):
            with self.subTest(definition=name):
                definition = schema["$defs"][name]
                self.assertFalse(definition["additionalProperties"])
                self.assertTrue(definition["required"])

    def test_cli_rejects_symlinked_output_ancestor(self) -> None:
        with (
            tempfile.TemporaryDirectory(dir=ROOT / "artifacts") as directory,
            tempfile.TemporaryDirectory() as outside,
        ):
            working = Path(directory)
            artifact, benchmark = self._inputs(working)
            link = working / "outside"
            link.symlink_to(outside, target_is_directory=True)
            output = link / "nested" / "evidence.json"
            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/release_evidence.py",
                    "generate",
                    "--artifact",
                    str(artifact.relative_to(ROOT)),
                    "--benchmark",
                    str(benchmark.relative_to(ROOT)),
                    "--expected-sha",
                    self._head(),
                    "--timestamp",
                    "2026-07-31T02:00:00+00:00",
                    "--output",
                    str(output),
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )

        self.assertEqual(completed.returncode, 2)
        self.assertIn("unsafe_release_evidence_output", completed.stderr)
        self.assertFalse(Path(outside, "nested", "evidence.json").exists())

    def test_stale_benchmark_commit_cannot_build_or_verify(self) -> None:
        with tempfile.TemporaryDirectory(dir=ROOT / "artifacts") as directory:
            artifact, benchmark = self._inputs(Path(directory))
            value = json.loads(benchmark.read_text(encoding="utf-8"))
            value["commit"] = "0" * 40
            value["source_manifest"]["commit"] = "0" * 40
            benchmark.write_text(
                json.dumps(value, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )

            with self.assertRaisesRegex(
                ReleaseEvidenceError,
                "benchmark_commit_mismatch",
            ):
                build_release_evidence(
                    ROOT,
                    artifacts=[artifact],
                    benchmarks=[benchmark],
                    expected_commit=self._head(),
                    timestamp="2026-07-31T02:00:00+00:00",
                )

    def test_symlinked_release_input_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory(dir=ROOT / "artifacts") as directory:
            artifact, benchmark = self._inputs(Path(directory))
            alias = Path(directory) / "artifact-alias.json"
            alias.symlink_to(artifact)

            with self.assertRaisesRegex(
                ReleaseEvidenceError,
                "release_input_not_regular_file",
            ):
                build_release_evidence(
                    ROOT,
                    artifacts=[alias],
                    benchmarks=[benchmark],
                    expected_commit=self._head(),
                    timestamp="2026-07-31T02:00:00+00:00",
                )


if __name__ == "__main__":
    unittest.main()
