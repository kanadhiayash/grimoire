#!/usr/bin/env python3
"""Run the deterministic 500-case strict manifest acceptance benchmark."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import random
import sys
from pathlib import Path
from typing import Any, Callable


ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from grimoire.errors import ManifestValidationError  # noqa: E402
from grimoire.validation.manifest import (  # noqa: E402
    supported_standards_versions,
    validate_manifest,
)


Mutation = Callable[[dict[str, Any], int], None]
EXPECTED_DIAGNOSTICS = {
    "ai_null": ("type_mismatch", "$.ai"),
    "ai_string": ("type_mismatch", "$.ai"),
    "ai_unknown": ("unknown_property", "$.ai.unexpected_{index}"),
    "control_character": ("control_character", "$.project.name"),
    "data_null": ("type_mismatch", "$.data"),
    "lifecycle_invalid": ("unsupported_value", "$.project.lifecycle_stage"),
    "markets_null": ("type_mismatch", "$.markets"),
    "missing_project": ("missing_required", "$.project"),
    "missing_risk": ("missing_required", "$.risk"),
    "missing_standards": ("missing_required", "$.standards"),
    "missing_zeref": ("missing_required", "$.zeref"),
    "personal_data_string": ("type_mismatch", "$.data.personal_data"),
    "product_name_oversized": ("string_too_long", "$.project.name"),
    "project_name_empty": ("string_too_short", "$.project.name"),
    "product_types_empty": ("empty_collection", "$.project.product_types"),
    "product_types_string": ("type_mismatch", "$.project.product_types"),
    "project_string": ("type_mismatch", "$.project"),
    "risk_string": ("type_mismatch", "$.risk"),
    "schema_version_string": ("type_mismatch", "$.schema_version"),
    "standards_string": ("type_mismatch", "$.standards"),
    "unknown_property": ("unknown_property", "$.unexpected_{index}"),
    "unknowns_null": ("type_mismatch", "$.unknowns"),
    "unknowns_string": ("type_mismatch", "$.unknowns"),
    "unsupported_version": ("unsupported_version", "$.standards.version"),
    "users_string": ("type_mismatch", "$.users"),
    "zeref_string": ("type_mismatch", "$.zeref"),
}


def _sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _base_manifest() -> dict[str, Any]:
    value = json.loads(
        (ROOT / "templates" / "project" / "project.json").read_text(
            encoding="utf-8"
        )
    )
    if not isinstance(value, dict):
        raise RuntimeError("project template must contain a JSON object")
    return value


def _mutations() -> dict[str, Mutation]:
    return {
        "ai_null": lambda value, index: value.__setitem__("ai", None),
        "ai_string": lambda value, index: value.__setitem__(
            "ai", f"enabled-{index}"
        ),
        "ai_unknown": lambda value, index: value["ai"].__setitem__(
            f"unexpected_{index}", True
        ),
        "control_character": lambda value, index: value["project"].__setitem__(
            "name", f"product\u0000{index}"
        ),
        "data_null": lambda value, index: value.__setitem__("data", None),
        "lifecycle_invalid": lambda value, index: value["project"].__setitem__(
            "lifecycle_stage", f"INVALID_{index}"
        ),
        "markets_null": lambda value, index: value.__setitem__("markets", None),
        "missing_project": lambda value, index: value.pop("project"),
        "missing_risk": lambda value, index: value.pop("risk"),
        "missing_standards": lambda value, index: value.pop("standards"),
        "missing_zeref": lambda value, index: value.pop("zeref"),
        "personal_data_string": lambda value, index: value["data"].__setitem__(
            "personal_data", "false"
        ),
        "product_name_oversized": lambda value, index: value["project"].__setitem__(
            "name", "x" * 201
        ),
        "project_name_empty": lambda value, index: value["project"].__setitem__(
            "name", ""
        ),
        "product_types_empty": lambda value, index: value["project"].__setitem__(
            "product_types", []
        ),
        "product_types_string": lambda value, index: value["project"].__setitem__(
            "product_types", f"type-{index}"
        ),
        "project_string": lambda value, index: value.__setitem__(
            "project", f"project-{index}"
        ),
        "risk_string": lambda value, index: value.__setitem__("risk", "critical"),
        "schema_version_string": lambda value, index: value.__setitem__(
            "schema_version", "1"
        ),
        "standards_string": lambda value, index: value.__setitem__(
            "standards", f"standards-{index}"
        ),
        "unknown_property": lambda value, index: value.__setitem__(
            f"unexpected_{index}", True
        ),
        "unknowns_null": lambda value, index: value.__setitem__("unknowns", None),
        "unknowns_string": lambda value, index: value.__setitem__("unknowns", "none"),
        "unsupported_version": lambda value, index: value["standards"].__setitem__(
            "version", f"99.0.{index}"
        ),
        "users_string": lambda value, index: value.__setitem__(
            "users", f"users-{index}"
        ),
        "zeref_string": lambda value, index: value.__setitem__(
            "zeref", f"zeref-{index}"
        ),
    }


def run_strict_500(*, cases: int, seed: int) -> dict[str, Any]:
    if cases <= 0:
        raise ValueError("cases must be positive")
    rng = random.Random(seed)
    mutations = _mutations()
    names = sorted(mutations)
    if set(names) != set(EXPECTED_DIAGNOSTICS):
        raise RuntimeError("every strict mutation requires one expected diagnostic")
    supported = supported_standards_versions(ROOT)
    base_manifest = _base_manifest()
    validate_manifest(copy.deepcopy(base_manifest), supported)
    corpus_hash = hashlib.sha256()
    normalized: list[dict[str, Any]] = []
    unexpected_accepts = 0
    unexpected_diagnostics = 0
    unhandled_exceptions = 0

    for index in range(cases):
        mutation = rng.choice(names)
        manifest = copy.deepcopy(base_manifest)
        mutations[mutation](manifest, index)
        case_id = f"GRM-STRICT-{seed}-{index:04d}"
        encoded = json.dumps(
            manifest,
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode("utf-8")
        corpus_hash.update(case_id.encode("ascii"))
        corpus_hash.update(b"\0")
        corpus_hash.update(encoded)
        try:
            validate_manifest(manifest, supported)
        except ManifestValidationError as exc:
            diagnostic_pairs = {
                (issue.code, issue.path) for issue in exc.issues
            }
            expected_code, expected_path_template = (
                EXPECTED_DIAGNOSTICS[mutation]
            )
            expected_path = expected_path_template.format(index=index)
            expected_observed = (
                expected_code,
                expected_path,
            ) in diagnostic_pairs
            if not expected_observed:
                unexpected_diagnostics += 1
            result = {
                "case_id": case_id,
                "input_sha256": _sha256(encoded),
                "mutation": mutation,
                "outcome": (
                    "CONTROLLED_REJECTION"
                    if expected_observed
                    else "UNEXPECTED_DIAGNOSTIC"
                ),
                "expected_code": expected_code,
                "expected_path": expected_path,
                "diagnostic_codes": sorted({issue.code for issue in exc.issues}),
                "diagnostic_paths": sorted({issue.path for issue in exc.issues}),
            }
        except Exception as exc:  # The benchmark must expose implementation defects.
            unhandled_exceptions += 1
            result = {
                "case_id": case_id,
                "input_sha256": _sha256(encoded),
                "mutation": mutation,
                "outcome": "UNHANDLED_EXCEPTION",
                "exception_type": type(exc).__name__,
            }
        else:
            unexpected_accepts += 1
            result = {
                "case_id": case_id,
                "input_sha256": _sha256(encoded),
                "mutation": mutation,
                "outcome": "UNEXPECTED_ACCEPT",
            }
        normalized.append(result)

    normalized_bytes = json.dumps(
        normalized,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    return {
        "schema_version": 1,
        "generator": "strict-manifest-500-v1",
        "cases": cases,
        "seed": seed,
        "corpus_sha256": corpus_hash.hexdigest(),
        "normalized_results_sha256": _sha256(normalized_bytes),
        "controlled_rejections": (
            cases
            - unexpected_accepts
            - unexpected_diagnostics
            - unhandled_exceptions
        ),
        "unexpected_accepts": unexpected_accepts,
        "unexpected_diagnostics": unexpected_diagnostics,
        "unhandled_exceptions": unhandled_exceptions,
        "results": normalized,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cases", type=int, default=500)
    parser.add_argument("--seed", type=int, default=20260727)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = run_strict_500(cases=args.cases, seed=args.seed)
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return 0 if (
        result["unhandled_exceptions"] == 0
        and result["unexpected_accepts"] == 0
        and result["unexpected_diagnostics"] == 0
    ) else 1


if __name__ == "__main__":
    raise SystemExit(main())
