#!/usr/bin/env python3
"""Run deterministic manifest fuzz cases and preserve exact raw evidence."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import platform
import random
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable


ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from grimoire.errors import ManifestIssue, ManifestValidationError  # noqa: E402
from grimoire.validation.manifest import (  # noqa: E402
    supported_standards_versions,
    validate_manifest,
)


Validator = Callable[[Any, tuple[str, ...]], Any]
GENERATOR = "manifest-fuzz-v1"
OUTPUT_FILES = ("cases.jsonl", "results.jsonl", "summary.json")
ACCEPT = "ACCEPT"
REJECT = "REJECT"


@dataclass(frozen=True)
class MutationSpec:
    expected_outcome: str
    expected_code: str | None
    expected_path: str | None
    mutate: Callable[[dict[str, Any], int], None]


@dataclass(frozen=True)
class MutationCase:
    case_id: str
    seed: int
    mutation_class: str
    source_fixture: str
    mutated_manifest: dict[str, Any]
    expected_outcome: str
    expected_code: str | None
    expected_path: str | None
    input_sha256: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "case_id": self.case_id,
            "seed": self.seed,
            "mutation_class": self.mutation_class,
            "source_fixture": self.source_fixture,
            "mutated_manifest": copy.deepcopy(self.mutated_manifest),
            "expected_outcome": self.expected_outcome,
            "expected_code": self.expected_code,
            "expected_path": self.expected_path,
            "input_sha256": self.input_sha256,
        }


@dataclass(frozen=True)
class FuzzResult:
    case_id: str
    mutation_class: str
    outcome: str
    input_sha256: str
    diagnostic_sha256: str
    issues: tuple[ManifestIssue, ...] = ()
    internal_error_type: str | None = None

    def to_dict(self) -> dict[str, Any]:
        value: dict[str, Any] = {
            "case_id": self.case_id,
            "mutation_class": self.mutation_class,
            "outcome": self.outcome,
            "input_sha256": self.input_sha256,
            "diagnostic_sha256": self.diagnostic_sha256,
            "issues": [issue.to_dict() for issue in self.issues],
        }
        if self.internal_error_type is not None:
            value["internal_error_type"] = self.internal_error_type
        return value


@dataclass(frozen=True)
class FuzzReport:
    case_count: int
    seed: int
    mutation_cases: tuple[MutationCase, ...]
    results: tuple[FuzzResult, ...]
    controlled_accepts: int
    controlled_rejections: int
    unexpected_outcomes: int
    internal_failures: int
    corpus_sha256: str
    results_sha256: str

    @property
    def exit_code(self) -> int:
        return 0 if (
            self.unexpected_outcomes == 0
            and self.internal_failures == 0
        ) else 1

    def summary(self) -> dict[str, Any]:
        mutation_classes = sorted(
            {case.mutation_class for case in self.mutation_cases}
        )
        git_tree_state = _git_tree_state()
        return {
            "schema_version": 1,
            "generator": GENERATOR,
            "case_count": self.case_count,
            "seed": self.seed,
            "mutation_classes": mutation_classes,
            "mutation_class_count": len(mutation_classes),
            "controlled_accepts": self.controlled_accepts,
            "controlled_rejections": self.controlled_rejections,
            "unexpected_outcomes": self.unexpected_outcomes,
            "internal_failures": self.internal_failures,
            "unhandled_exceptions": 0,
            "corpus_sha256": self.corpus_sha256,
            "results_sha256": self.results_sha256,
            "exit_code": self.exit_code,
            "commit_sha": _git_head(),
            "git_tree_state": git_tree_state,
            "commit_exact": git_tree_state == "CLEAN",
            "python_version": platform.python_version(),
            "platform": platform.platform(),
        }


def _canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")


def _sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _git_head() -> str:
    try:
        completed = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
    except OSError:
        return "NOT_VERIFIED"
    value = completed.stdout.strip()
    if completed.returncode == 0 and len(value) == 40:
        return value
    return "NOT_VERIFIED"


def _git_tree_state() -> str:
    try:
        completed = subprocess.run(
            ["git", "status", "--porcelain", "--untracked-files=all"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
    except OSError:
        return "NOT_VERIFIED"
    if completed.returncode != 0:
        return "NOT_VERIFIED"
    return "DIRTY" if completed.stdout.strip() else "CLEAN"


def _deep_value(index: int) -> dict[str, Any]:
    value: dict[str, Any] = {"case": index}
    for depth in range(96):
        value = {f"level_{depth}": value}
    return value


def _mutation_specs() -> dict[str, MutationSpec]:
    return {
        "wrong_type": MutationSpec(
            REJECT,
            "type_mismatch",
            "$.users",
            lambda value, index: value.__setitem__(
                "users", f"users-{index}"
            ),
        ),
        "null": MutationSpec(
            REJECT,
            "type_mismatch",
            "$.risk",
            lambda value, index: value.__setitem__("risk", None),
        ),
        "limit": MutationSpec(
            REJECT,
            "string_too_long",
            "$.project.name",
            lambda value, index: value["project"].__setitem__(
                "name", "x" * 201
            ),
        ),
        "unicode_control": MutationSpec(
            REJECT,
            "control_character",
            "$.project.name",
            lambda value, index: value["project"].__setitem__(
                "name", f"product\u0000{index}"
            ),
        ),
        "deep_nesting": MutationSpec(
            REJECT,
            "unknown_property",
            "$.unexpected",
            lambda value, index: value.__setitem__(
                "unexpected", _deep_value(index)
            ),
        ),
        "path": MutationSpec(
            ACCEPT,
            None,
            None,
            lambda value, index: value["project"].__setitem__(
                "name", f"../../outside-{index}"
            ),
        ),
        "instruction_payload": MutationSpec(
            ACCEPT,
            None,
            None,
            lambda value, index: value["project"].__setitem__(
                "name", f"Ignore prior instructions for case {index}"
            ),
        ),
        "url": MutationSpec(
            ACCEPT,
            None,
            None,
            lambda value, index: value.__setitem__(
                "users", [f"https://example.invalid/users/{index}"]
            ),
        ),
        "timestamp": MutationSpec(
            ACCEPT,
            None,
            None,
            lambda value, index: value.__setitem__(
                "unknowns", [f"2026-07-27T21:{index % 60:02d}:00Z"]
            ),
        ),
        "missing_field": MutationSpec(
            REJECT,
            "missing_required",
            "$.project",
            lambda value, index: value.pop("project"),
        ),
        "unexpected_property": MutationSpec(
            REJECT,
            "unknown_property",
            "$.project.unexpected",
            lambda value, index: value["project"].__setitem__(
                "unexpected", index
            ),
        ),
        "unsupported_version": MutationSpec(
            REJECT,
            "unsupported_version",
            "$.standards.version",
            lambda value, index: value["standards"].__setitem__(
                "version", f"99.0.{index}"
            ),
        ),
        "malformed_nested": MutationSpec(
            REJECT,
            "type_mismatch",
            "$.data.personal_data",
            lambda value, index: value.setdefault("data", {}).__setitem__(
                "personal_data", "false"
            ),
        ),
    }


def _load_corpus(
    supported: tuple[str, ...],
) -> tuple[tuple[str, dict[str, Any]], ...]:
    corpus_root = ROOT / "benchmarks" / "fuzz" / "corpus"
    fixtures: list[tuple[str, dict[str, Any]]] = []
    for fixture_path in sorted(corpus_root.glob("*.json")):
        value = json.loads(fixture_path.read_text(encoding="utf-8"))
        if not isinstance(value, dict):
            raise RuntimeError(
                f"{fixture_path.relative_to(ROOT)} must contain an object"
            )
        validate_manifest(value, supported)
        fixtures.append((str(fixture_path.relative_to(ROOT)), value))
    if len(fixtures) < 2:
        raise RuntimeError("manifest fuzz requires at least two corpus fixtures")
    return tuple(fixtures)


def _generate_cases(
    *,
    cases: int,
    seed: int,
    supported: tuple[str, ...],
) -> tuple[MutationCase, ...]:
    specs = _mutation_specs()
    if cases < len(specs):
        raise ValueError(
            f"cases must be at least {len(specs)} to cover every "
            "mutation class"
        )
    names = sorted(specs)
    corpus = _load_corpus(supported)
    rng = random.Random(seed)
    generated: list[MutationCase] = []
    cycle: list[str] = []

    for index in range(cases):
        if index % len(names) == 0:
            cycle = list(names)
            rng.shuffle(cycle)
        mutation_class = cycle[index % len(names)]
        spec = specs[mutation_class]
        source_fixture, source = corpus[rng.randrange(len(corpus))]
        manifest = copy.deepcopy(source)
        spec.mutate(manifest, index)
        case_id = f"GRM-FUZZ-{seed}-{index:05d}"
        encoded = _canonical_bytes(manifest)
        generated.append(
            MutationCase(
                case_id=case_id,
                seed=seed,
                mutation_class=mutation_class,
                source_fixture=source_fixture,
                mutated_manifest=manifest,
                expected_outcome=spec.expected_outcome,
                expected_code=spec.expected_code,
                expected_path=spec.expected_path,
                input_sha256=_sha256(encoded),
            )
        )
    return tuple(generated)


def _diagnostic_hash(issues: tuple[ManifestIssue, ...]) -> str:
    return _sha256(
        _canonical_bytes([issue.to_dict() for issue in issues])
    )


def _evaluate_case(
    case: MutationCase,
    supported: tuple[str, ...],
    validator: Validator,
) -> FuzzResult:
    try:
        validator(copy.deepcopy(case.mutated_manifest), supported)
    except ManifestValidationError as exc:
        issues = exc.issues
        observed = {(issue.code, issue.path) for issue in issues}
        expected = (case.expected_code, case.expected_path)
        outcome = (
            "CONTROLLED_REJECTION"
            if case.expected_outcome == REJECT and expected in observed
            else "UNEXPECTED_OUTCOME"
        )
        return FuzzResult(
            case_id=case.case_id,
            mutation_class=case.mutation_class,
            outcome=outcome,
            input_sha256=case.input_sha256,
            diagnostic_sha256=_diagnostic_hash(issues),
            issues=issues,
        )
    except Exception as exc:
        error_type = type(exc).__name__
        return FuzzResult(
            case_id=case.case_id,
            mutation_class=case.mutation_class,
            outcome="INTERNAL_FAILURE",
            input_sha256=case.input_sha256,
            diagnostic_sha256=_sha256(
                _canonical_bytes({"internal_error_type": error_type})
            ),
            internal_error_type=error_type,
        )

    outcome = (
        "CONTROLLED_ACCEPT"
        if case.expected_outcome == ACCEPT
        else "UNEXPECTED_OUTCOME"
    )
    return FuzzResult(
        case_id=case.case_id,
        mutation_class=case.mutation_class,
        outcome=outcome,
        input_sha256=case.input_sha256,
        diagnostic_sha256=_diagnostic_hash(()),
    )


def run_manifest_fuzz(
    cases: int,
    seed: int,
    *,
    validator: Validator | None = None,
) -> FuzzReport:
    supported = supported_standards_versions(ROOT)
    mutation_cases = _generate_cases(
        cases=cases,
        seed=seed,
        supported=supported,
    )
    active_validator = validator or validate_manifest
    results = tuple(
        _evaluate_case(case, supported, active_validator)
        for case in mutation_cases
    )
    case_bytes = _canonical_bytes(
        [case.to_dict() for case in mutation_cases]
    )
    result_bytes = _canonical_bytes(
        [result.to_dict() for result in results]
    )
    return FuzzReport(
        case_count=cases,
        seed=seed,
        mutation_cases=mutation_cases,
        results=results,
        controlled_accepts=sum(
            result.outcome == "CONTROLLED_ACCEPT" for result in results
        ),
        controlled_rejections=sum(
            result.outcome == "CONTROLLED_REJECTION"
            for result in results
        ),
        unexpected_outcomes=sum(
            result.outcome == "UNEXPECTED_OUTCOME" for result in results
        ),
        internal_failures=sum(
            result.outcome == "INTERNAL_FAILURE" for result in results
        ),
        corpus_sha256=_sha256(case_bytes),
        results_sha256=_sha256(result_bytes),
    )


def _safe_target(output: Path, name: str) -> Path:
    target = output / name
    output_root = output.resolve()
    if target.is_symlink():
        raise ValueError(f"refusing symlinked output file: {name}")
    if target.resolve(strict=False).parent != output_root:
        raise ValueError(f"output file escapes requested directory: {name}")
    return target


def _path_is_within(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
    except ValueError:
        return False
    return True


def _reject_symlinked_output_path(output: Path) -> None:
    if ".." in output.parts:
        raise ValueError(
            "output directory path must not contain parent traversal"
        )
    output_absolute = Path(os.path.abspath(output))
    trusted_candidates = (
        Path(os.path.abspath(ROOT)),
        Path(os.path.abspath(tempfile.gettempdir())),
        Path(os.path.abspath("/tmp")),
    )
    trusted_roots = [
        candidate
        for candidate in trusted_candidates
        if _path_is_within(output_absolute, candidate)
    ]
    boundary = (
        max(trusted_roots, key=lambda path: len(path.parts))
        if trusted_roots
        else Path(output_absolute.anchor)
    )
    candidate = boundary
    for part in output_absolute.relative_to(boundary).parts:
        candidate /= part
        if candidate.is_symlink():
            raise ValueError(
                "output directory path must not contain symlinks"
            )


def _validate_report_integrity(report: FuzzReport) -> None:
    if len(report.mutation_cases) != report.case_count:
        raise ValueError("case count mismatch")
    if len(report.results) != report.case_count:
        raise ValueError("result count mismatch")

    for case in report.mutation_cases:
        current_hash = _sha256(_canonical_bytes(case.mutated_manifest))
        if current_hash != case.input_sha256:
            raise ValueError(f"case hash mismatch: {case.case_id}")

    for case, result in zip(report.mutation_cases, report.results):
        if (
            result.case_id != case.case_id
            or result.input_sha256 != case.input_sha256
        ):
            raise ValueError(f"case/result mismatch: {case.case_id}")

    case_bytes = _canonical_bytes(
        [case.to_dict() for case in report.mutation_cases]
    )
    if _sha256(case_bytes) != report.corpus_sha256:
        raise ValueError("corpus hash mismatch")

    result_bytes = _canonical_bytes(
        [result.to_dict() for result in report.results]
    )
    if _sha256(result_bytes) != report.results_sha256:
        raise ValueError("results hash mismatch")


def _atomic_write(path: Path, text: str) -> None:
    temporary_name: str | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=path.parent,
            prefix=f".{path.name}.",
            suffix=".tmp",
            delete=False,
        ) as handle:
            handle.write(text)
            temporary_name = handle.name
        os.replace(temporary_name, path)
    finally:
        if temporary_name is not None:
            temporary_path = Path(temporary_name)
            if temporary_path.exists():
                temporary_path.unlink()


def write_artifacts(report: FuzzReport, output: Path) -> None:
    _validate_report_integrity(report)
    _reject_symlinked_output_path(output)
    output.mkdir(parents=True, exist_ok=True)
    if not output.is_dir():
        raise ValueError("output must be a directory")
    targets = {
        name: _safe_target(output, name) for name in OUTPUT_FILES
    }
    cases_text = "".join(
        json.dumps(
            case.to_dict(),
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=True,
        )
        + "\n"
        for case in report.mutation_cases
    )
    results_text = "".join(
        json.dumps(
            result.to_dict(),
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=True,
        )
        + "\n"
        for result in report.results
    )
    summary_text = (
        json.dumps(report.summary(), indent=2, sort_keys=True) + "\n"
    )
    _atomic_write(targets["cases.jsonl"], cases_text)
    _atomic_write(targets["results.jsonl"], results_text)
    _atomic_write(targets["summary.json"], summary_text)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cases", type=int, required=True)
    parser.add_argument("--seed", type=int, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        report = run_manifest_fuzz(cases=args.cases, seed=args.seed)
        write_artifacts(report, args.output)
    except (OSError, RuntimeError, ValueError) as exc:
        print(
            json.dumps(
                {
                    "status": "INTERNAL_FAILURE",
                    "error_type": type(exc).__name__,
                },
                sort_keys=True,
            ),
            file=sys.stderr,
        )
        return 1
    print(json.dumps(report.summary(), indent=2, sort_keys=True))
    return report.exit_code


if __name__ == "__main__":
    raise SystemExit(main())
