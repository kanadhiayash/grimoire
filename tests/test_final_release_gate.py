from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from grimoire.benchmarks.release_candidate import (  # noqa: E402
    compare_release_candidate_runs,
    load_release_candidate_suite,
    run_release_candidate,
)
from grimoire.benchmarks.runner import run_benchmark_suite  # noqa: E402
from grimoire.release.evidence import build_release_evidence  # noqa: E402
from grimoire.release.gate import (  # noqa: E402
    evaluate_final_release,
    verify_release_tag,
)


class FinalReleaseGateTests(unittest.TestCase):
    @staticmethod
    def _head(repository: Path) -> str:
        return subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=repository,
            text=True,
            capture_output=True,
            check=True,
        ).stdout.strip()

    def _repository(self, directory: Path) -> Path:
        repository = directory / "repository"
        (repository / "policies").mkdir(parents=True)
        (repository / "docs" / "releases").mkdir(parents=True)
        (repository / "benchmarks" / "release-candidate").mkdir(parents=True)
        (repository / "artifacts").mkdir()
        (repository / ".gitignore").write_text("artifacts/\n", encoding="utf-8")
        (repository / "VERSION").write_text("0.5.0\n", encoding="utf-8")
        (repository / "policies" / "baseline.json").write_text(
            '{"standard_version":"0.5.0"}\n',
            encoding="utf-8",
        )
        (repository / "REPOSITORY_INDEX.json").write_text(
            '{"standard_version":"0.5.0"}\n',
            encoding="utf-8",
        )
        (repository / "CHANGELOG.md").write_text(
            "# Changelog\n\n## [Unreleased]\n",
            encoding="utf-8",
        )
        (repository / "docs" / "releases" / "1.0.0.md").write_text(
            "# Grimoire 1.0.0 Release Candidate\n\nStatus: NOT RELEASED\n",
            encoding="utf-8",
        )
        (repository / "benchmarks" / "release-candidate" / "suite.json").write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "suite_id": "final-release-test",
                    "sources": [
                        "VERSION",
                        "benchmarks/release-candidate/suite.json",
                    ],
                    "gates": [
                        {
                            "id": "executable-evidence",
                            "category": "release",
                            "hard_gate": True,
                            "command": ["{python}", "-c", "print('pass')"],
                        }
                    ],
                },
                indent=2,
                sort_keys=True,
            )
            + "\n",
            encoding="utf-8",
        )
        subprocess.run(["git", "init", "-q"], cwd=repository, check=True)
        subprocess.run(
            ["git", "config", "user.email", "test@example.com"],
            cwd=repository,
            check=True,
        )
        subprocess.run(
            ["git", "config", "user.name", "Test"],
            cwd=repository,
            check=True,
        )
        subprocess.run(["git", "add", "."], cwd=repository, check=True)
        subprocess.run(
            ["git", "commit", "-qm", "fixture"],
            cwd=repository,
            check=True,
        )
        return repository

    def _candidate_runs(
        self,
        repository: Path,
        directory: Path,
        *,
        declared_status: str | None = None,
        reduced: bool = False,
    ) -> tuple[list[Path], dict]:
        suite_path = repository / "benchmarks/release-candidate/suite.json"
        suite = load_release_candidate_suite(suite_path)
        gates = list(suite["gates"])
        if declared_status is not None:
            gates.append(
                {
                    "id": "declared-boundary",
                    "category": "release",
                    "hard_gate": True,
                    "declared_status": declared_status,
                    "reason_codes": ["external_evidence_missing"],
                }
            )
        if reduced:
            gates = gates[:-1]
        suite = {**suite, "gates": gates}
        paths = []
        for index in range(1, 4):
            output = directory / f"run-{index}"
            run_release_candidate(
                suite,
                root=repository,
                output=output,
                expected_commit=self._head(repository),
                run_id=f"run-{index}",
            )
            result_path = output / "RELEASE_CANDIDATE_RESULTS.json"
            result = json.loads(result_path.read_text(encoding="utf-8"))
            for item in result["gates"]:
                if "command" in item:
                    item["started_at"] = "2026-08-01T07:00:00+00:00"
                    item["finished_at"] = "2026-08-01T07:01:00+00:00"
            result_path.write_text(
                json.dumps(result, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
            paths.append(output)
        comparison = compare_release_candidate_runs(
            paths,
            expected_commit=self._head(repository),
        )
        return paths, comparison

    def _release_evidence(
        self,
        repository: Path,
        directory: Path,
        *,
        timestamp: str = "2026-08-01T07:00:00+00:00",
        approvals: tuple[dict, ...] = (),
        private_release_approval: bool = False,
    ) -> dict:
        directory = repository / "artifacts" / directory.name
        directory.mkdir(parents=True)
        artifact = directory / "artifact.json"
        artifact.write_text('{"status":"PASS"}\n', encoding="utf-8")
        benchmark_root = directory / "benchmark"
        run_benchmark_suite(
            {
                "schema_version": 1,
                "suite_id": "final-release-evidence-test",
                "sources": [str(artifact.relative_to(repository))],
                "cases": [
                    {
                        "id": "controlled-pass",
                        "command": [sys.executable, "-c", "print('pass')"],
                        "hard_gate": True,
                    }
                ],
            },
            root=repository,
            output=benchmark_root,
            commit=self._head(repository),
        )
        return build_release_evidence(
            repository,
            artifacts=[artifact],
            benchmarks=[benchmark_root / "BENCHMARK_RESULTS.json"],
            expected_commit=self._head(repository),
            timestamp=timestamp,
            approvals=approvals,
            private_release_approval=private_release_approval,
        )

    def _promote_release_contract(self, repository: Path) -> str:
        (repository / "VERSION").write_text("1.0.0\n", encoding="utf-8")
        (repository / "policies" / "baseline.json").write_text(
            '{"standard_version":"1.0.0"}\n',
            encoding="utf-8",
        )
        (repository / "REPOSITORY_INDEX.json").write_text(
            '{"standard_version":"1.0.0"}\n',
            encoding="utf-8",
        )
        (repository / "CHANGELOG.md").write_text(
            "# Changelog\n\n## [1.0.0] - 2026-08-01\n",
            encoding="utf-8",
        )
        (repository / "README.md").write_text(
            "# Fixture\n\nCurrent release: `1.0.0`\n",
            encoding="utf-8",
        )
        (repository / "docs" / "releases" / "1.0.0.md").write_text(
            "# Grimoire 1.0.0 Release\n\n**Status: RELEASED**\n",
            encoding="utf-8",
        )
        subprocess.run(["git", "add", "."], cwd=repository, check=True)
        subprocess.run(
            ["git", "commit", "-qm", "release fixture"],
            cwd=repository,
            check=True,
        )
        return self._head(repository)

    def test_not_verified_hard_gate_blocks_release(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            repository = self._repository(root)
            runs, comparison = self._candidate_runs(
                repository,
                root,
                declared_status="NOT_VERIFIED",
            )
            evidence = self._release_evidence(repository, root)
            result = evaluate_final_release(
                root=repository,
                expected_commit=self._head(repository),
                intended_version="1.0.0",
                intended_tag="v1.0.0",
                candidate_runs=runs,
                candidate_comparison=comparison,
                release_evidence=evidence,
                now=datetime(2026, 8, 1, 8, tzinfo=timezone.utc),
            )

        self.assertEqual("BLOCKED", result["status"])
        self.assertFalse(result["eligible"])
        self.assertIn(
            "release_candidate_hard_gate_not_pass",
            result["reason_codes"],
        )

    def test_missing_approval_and_signature_block_release(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            repository = self._repository(root)
            runs, comparison = self._candidate_runs(repository, root)
            evidence = self._release_evidence(repository, root)
            result = evaluate_final_release(
                root=repository,
                expected_commit=self._head(repository),
                intended_version="1.0.0",
                intended_tag="v1.0.0",
                candidate_runs=runs,
                candidate_comparison=comparison,
                release_evidence=evidence,
                now=datetime(2026, 8, 1, 8, tzinfo=timezone.utc),
            )

        self.assertEqual("BLOCKED", result["status"])
        self.assertIn("release_approval_missing", result["reason_codes"])
        self.assertIn("signature_not_verified", result["reason_codes"])
        self.assertNotIn(
            "release_candidate_not_canonical",
            result["reason_codes"],
        )
        self.assertEqual("FINAL_RELEASE_DECISION_V1", result["decision_contract"])
        self.assertTrue(result["pass_supported"])

    def test_version_contract_must_change_atomically(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            repository = self._repository(root)
            runs, comparison = self._candidate_runs(repository, root)
            evidence = self._release_evidence(repository, root)
            result = evaluate_final_release(
                root=repository,
                expected_commit=self._head(repository),
                intended_version="1.0.0",
                intended_tag="v1.0.0",
                candidate_runs=runs,
                candidate_comparison=comparison,
                release_evidence=evidence,
                now=datetime(2026, 8, 1, 8, tzinfo=timezone.utc),
            )

        self.assertIn("version_file_mismatch", result["reason_codes"])
        self.assertIn("baseline_version_mismatch", result["reason_codes"])
        self.assertIn(
            "repository_index_version_mismatch",
            result["reason_codes"],
        )
        self.assertIn("changelog_version_missing", result["reason_codes"])
        self.assertIn("readme_version_mismatch", result["reason_codes"])
        self.assertIn(
            "release_document_version_mismatch",
            result["reason_codes"],
        )

    def test_reduced_suite_cannot_substitute_for_canonical_candidate(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            repository = self._repository(root)
            suite_path = (
                repository / "benchmarks" / "release-candidate" / "suite.json"
            )
            canonical = {
                "schema_version": 1,
                "suite_id": "canonical-final-release-test",
                "sources": ["VERSION", "benchmarks/release-candidate/suite.json"],
                "gates": [
                    {
                        "id": "executable-evidence",
                        "category": "release",
                        "hard_gate": True,
                        "command": ["{python}", "-c", "print('pass')"],
                    },
                    {
                        "id": "declared-boundary",
                        "category": "release",
                        "hard_gate": True,
                        "declared_status": "NOT_VERIFIED",
                        "reason_codes": ["external_evidence_missing"],
                    },
                ],
            }
            suite_path.write_text(
                json.dumps(canonical, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
            subprocess.run(
                ["git", "add", "benchmarks/release-candidate/suite.json"],
                cwd=repository,
                check=True,
            )
            subprocess.run(
                ["git", "commit", "-qm", "add canonical suite"],
                cwd=repository,
                check=True,
            )
            runs, comparison = self._candidate_runs(
                repository,
                root,
                reduced=True,
            )
            evidence = self._release_evidence(repository, root)
            result = evaluate_final_release(
                root=repository,
                expected_commit=self._head(repository),
                intended_version="1.0.0",
                intended_tag="v1.0.0",
                candidate_runs=runs,
                candidate_comparison=comparison,
                release_evidence=evidence,
                now=datetime(2026, 8, 1, 8, tzinfo=timezone.utc),
            )

        self.assertIn(
            "release_candidate_not_canonical",
            result["reason_codes"],
        )

    def test_substituted_canonical_source_hash_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            repository = self._repository(root)
            runs, _ = self._candidate_runs(repository, root)
            for path in runs:
                source_path = path / "SOURCE_MANIFEST.json"
                result_path = path / "RELEASE_CANDIDATE_RESULTS.json"
                source = json.loads(source_path.read_text(encoding="utf-8"))
                source["sources"][0]["sha256"] = "0" * 64
                source_path.write_text(
                    json.dumps(source, indent=2, sort_keys=True) + "\n",
                    encoding="utf-8",
                )
                result = json.loads(result_path.read_text(encoding="utf-8"))
                result["source_manifest"] = source
                result_path.write_text(
                    json.dumps(result, indent=2, sort_keys=True) + "\n",
                    encoding="utf-8",
                )
            comparison = compare_release_candidate_runs(
                runs,
                expected_commit=self._head(repository),
            )
            evidence = self._release_evidence(repository, root)
            result = evaluate_final_release(
                root=repository,
                expected_commit=self._head(repository),
                intended_version="1.0.0",
                intended_tag="v1.0.0",
                candidate_runs=runs,
                candidate_comparison=comparison,
                release_evidence=evidence,
                now=datetime(2026, 8, 1, 8, tzinfo=timezone.utc),
            )

        self.assertIn(
            "release_candidate_not_canonical",
            result["reason_codes"],
        )

    def test_stale_candidate_and_release_evidence_block_release(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            repository = self._repository(root)
            runs, _ = self._candidate_runs(repository, root)
            for path in runs:
                result_path = path / "RELEASE_CANDIDATE_RESULTS.json"
                result = json.loads(result_path.read_text(encoding="utf-8"))
                result["gates"][0]["started_at"] = "2026-07-29T06:00:00+00:00"
                result["gates"][0]["finished_at"] = "2026-07-29T06:01:00+00:00"
                result_path.write_text(
                    json.dumps(result, indent=2, sort_keys=True) + "\n",
                    encoding="utf-8",
                )
            comparison = compare_release_candidate_runs(
                runs,
                expected_commit=self._head(repository),
            )
            evidence = self._release_evidence(
                repository,
                root,
                timestamp="2026-07-29T07:00:00+00:00",
            )
            result = evaluate_final_release(
                root=repository,
                expected_commit=self._head(repository),
                intended_version="1.0.0",
                intended_tag="v1.0.0",
                candidate_runs=runs,
                candidate_comparison=comparison,
                release_evidence=evidence,
                now=datetime(2026, 8, 1, 8, tzinfo=timezone.utc),
            )

        self.assertIn("release_candidate_stale", result["reason_codes"])
        self.assertIn("release_evidence_stale", result["reason_codes"])

    def test_fresh_exact_commit_approval_satisfies_approval_boundary(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            repository = self._repository(root)
            commit = self._head(repository)
            runs, comparison = self._candidate_runs(repository, root)
            evidence = self._release_evidence(
                repository,
                root,
                approvals=(
                    {
                        "action": "release",
                        "commit": commit,
                        "approver": "release-owner",
                        "approved_at": "2026-08-01T07:30:00+00:00",
                        "scope": "exact-commit-release",
                    },
                ),
            )
            result = evaluate_final_release(
                root=repository,
                expected_commit=commit,
                intended_version="1.0.0",
                intended_tag="v1.0.0",
                candidate_runs=runs,
                candidate_comparison=comparison,
                release_evidence=evidence,
                now=datetime(2026, 8, 1, 8, tzinfo=timezone.utc),
            )

        self.assertNotIn("release_approval_missing", result["reason_codes"])
        self.assertNotIn("release_approval_stale", result["reason_codes"])

    def test_complete_private_release_evidence_is_eligible(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            repository = self._repository(root)
            commit = self._promote_release_contract(repository)
            runs, comparison = self._candidate_runs(repository, root)
            evidence = self._release_evidence(
                repository,
                root,
                approvals=(
                    {
                        "action": "release",
                        "commit": commit,
                        "approver": "release-owner",
                        "approved_at": "2026-08-01T07:30:00+00:00",
                        "scope": "exact-commit-release",
                    },
                ),
                private_release_approval=True,
            )
            result = evaluate_final_release(
                root=repository,
                expected_commit=commit,
                intended_version="1.0.0",
                intended_tag="v1.0.0",
                candidate_runs=runs,
                candidate_comparison=comparison,
                release_evidence=evidence,
                now=datetime(2026, 8, 1, 8, tzinfo=timezone.utc),
            )

        self.assertEqual("PASS", result["status"])
        self.assertTrue(result["eligible"])
        self.assertEqual([], result["reason_codes"])

    def test_tag_source_commit_mismatch_fails(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repository = Path(directory)
            subprocess.run(["git", "init", "-q"], cwd=repository, check=True)
            subprocess.run(
                ["git", "config", "user.email", "test@example.com"],
                cwd=repository,
                check=True,
            )
            subprocess.run(
                ["git", "config", "user.name", "Test"],
                cwd=repository,
                check=True,
            )
            tracked = repository / "tracked.txt"
            tracked.write_text("one\n", encoding="utf-8")
            subprocess.run(["git", "add", "tracked.txt"], cwd=repository, check=True)
            subprocess.run(["git", "commit", "-qm", "one"], cwd=repository, check=True)
            first = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=repository,
                text=True,
                capture_output=True,
                check=True,
            ).stdout.strip()
            subprocess.run(["git", "tag", "v1.0.0", first], cwd=repository, check=True)
            tracked.write_text("two\n", encoding="utf-8")
            subprocess.run(["git", "commit", "-qam", "two"], cwd=repository, check=True)
            second = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=repository,
                text=True,
                capture_output=True,
                check=True,
            ).stdout.strip()

            result = verify_release_tag(
                repository,
                tag="v1.0.0",
                expected_commit=second,
            )

        self.assertEqual("BLOCKED", result["status"])
        self.assertEqual(["release_tag_commit_mismatch"], result["reason_codes"])

    def test_cli_rejects_missing_inputs_with_machine_error(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                "scripts/release_preflight.py",
                "preflight",
                "--candidate-run",
                "artifacts/missing-run-1",
                "--candidate-run",
                "artifacts/missing-run-2",
                "--candidate-run",
                "artifacts/missing-run-3",
                "--comparison",
                "artifacts/missing-comparison.json",
                "--release-evidence",
                "artifacts/missing-evidence.json",
                "--expected-sha",
                "0" * 40,
                "--version",
                "1.0.0",
                "--tag",
                "v1.0.0",
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

        self.assertEqual(2, completed.returncode)
        result = json.loads(completed.stderr)
        self.assertEqual("BLOCKED", result["status"])
        self.assertFalse(result["eligible"])
        self.assertEqual(
            ["final_release_input_invalid"],
            result["reason_codes"],
        )

    def test_release_document_declares_source_release_without_publication_overclaim(self) -> None:
        release = (ROOT / "docs/releases/1.0.0.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("Status: RELEASED", release)
        self.assertIn("source release contract", release)
        self.assertIn("bounded gold-scenario quality metrics", release.lower())
        self.assertIn("resource budgets", release.lower())
        self.assertIn("pinned public Shiroe source trust contract", release)
        self.assertIn("not a cryptographic identity signature", release)

    def test_repository_routes_the_non_mutating_preflight(self) -> None:
        index = json.loads(
            (ROOT / "REPOSITORY_INDEX.json").read_text(encoding="utf-8")
        )
        command = index["commands"]["release_preflight"]
        self.assertEqual("scripts/release_preflight.py", command["entrypoint"])
        self.assertEqual("preflight", command["argv"][2])
        self.assertEqual(
            "scripts/release_preflight.py",
            index["artifacts"]["final_release_preflight"],
        )
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        runbook = (
            ROOT / "docs/operations/release-evidence-and-rollback.md"
        ).read_text(encoding="utf-8")
        decision = (
            ROOT / "docs/architecture/0025-final-release-preflight.md"
        )
        self.assertIn("scripts/release_preflight.py preflight", readme)
        self.assertIn("scripts/release_preflight.py preflight", runbook)
        self.assertTrue(decision.is_file())


if __name__ == "__main__":
    unittest.main()
