"""Deterministic synthetic control-scale compiler and verifier benchmark."""

from __future__ import annotations

import hashlib
import json
import math
import platform
import statistics
import sys
import time
import tracemalloc
from pathlib import Path
from typing import Any, Mapping, Sequence

from grimoire.benchmarks.runner import BenchmarkContractError

ALLOWED_SIZES = {100, 1000, 10000, 50000}


def _canonical_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n"
    ).encode("utf-8")


def generate_scale_dataset(
    count: int,
    *,
    seed: int,
) -> tuple[dict[str, str], ...]:
    if count not in ALLOWED_SIZES:
        raise BenchmarkContractError("unsupported_scale_size")
    if not isinstance(seed, int) or seed < 0:
        raise BenchmarkContractError("invalid_scale_seed")
    return tuple(
        {
            "id": f"GRIM-SCALE-{index:05d}",
            "version": "1.0.0",
            "requirement_level": ("must", "should", "may")[index % 3],
            "source_id": "SRC-SCALE-"
            + hashlib.sha256(f"{seed}:{index}".encode("utf-8")).hexdigest()[:16],
        }
        for index in range(1, count + 1)
    )


def compile_scale_dataset(
    dataset: Sequence[Mapping[str, str]],
) -> bytes:
    controls = [dict(item) for item in dataset]
    controls.sort(key=lambda item: item["id"])
    return _canonical_bytes(
        {
            "schema_version": 1,
            "control_count": len(controls),
            "controls_sha256": hashlib.sha256(
                _canonical_bytes(controls)
            ).hexdigest(),
            "controls": controls,
        }
    )


def verify_scale_pack(pack: bytes) -> dict[str, Any]:
    reasons: list[str] = []
    try:
        value = json.loads(pack)
    except (UnicodeDecodeError, json.JSONDecodeError):
        return {"status": "FAIL", "reason_codes": ["invalid_json"]}
    if not isinstance(value, dict) or set(value) != {
        "schema_version",
        "control_count",
        "controls_sha256",
        "controls",
    }:
        return {"status": "FAIL", "reason_codes": ["invalid_pack_shape"]}
    controls = value.get("controls")
    if (
        value.get("schema_version") != 1
        or not isinstance(controls, list)
        or value.get("control_count") != len(controls)
    ):
        reasons.append("invalid_pack_contract")
    ids = [
        item.get("id")
        for item in controls
        if isinstance(item, dict) and isinstance(item.get("id"), str)
    ]
    if len(ids) != len(controls) or ids != sorted(ids) or len(set(ids)) != len(ids):
        reasons.append("invalid_control_ids")
    observed_hash = hashlib.sha256(_canonical_bytes(controls)).hexdigest()
    if value.get("controls_sha256") != observed_hash:
        reasons.append("hash_mismatch")
    return {
        "status": "FAIL" if reasons else "PASS",
        "reason_codes": sorted(set(reasons)),
        "control_count": len(controls),
    }


def _milliseconds(start: int, end: int) -> float:
    return (end - start) / 1_000_000


def _p95(values: Sequence[float]) -> float:
    ordered = sorted(values)
    index = max(0, math.ceil(len(ordered) * 0.95) - 1)
    return ordered[index]


def evaluate_scale_results(
    datasets: list[dict[str, Any]],
    thresholds: Mapping[str, Any],
) -> dict[str, Any]:
    required = {
        "target_control_count",
        "compile_median_max_ms",
        "compile_p95_max_ms",
        "verify_max_ms",
        "memory_max_bytes",
        "context_token_ceiling",
    }
    if set(thresholds) != required:
        raise BenchmarkContractError("invalid_scale_thresholds")
    target_count = thresholds["target_control_count"]
    target = next(
        (item for item in datasets if item["control_count"] == target_count),
        None,
    )
    if target is None:
        raise BenchmarkContractError("target_dataset_missing")
    regressions: list[str] = []
    for metric, threshold_key in (
        ("compile_median_ms", "compile_median_max_ms"),
        ("compile_p95_ms", "compile_p95_max_ms"),
        ("verify_median_ms", "verify_max_ms"),
    ):
        if target[metric] > thresholds[threshold_key]:
            regressions.append(metric)
    memory_limit = thresholds["memory_max_bytes"]
    token_limit = thresholds["context_token_ceiling"]
    memory_gate = (
        "NOT_VERIFIED"
        if memory_limit is None
        else ("PASS" if target["memory_peak_bytes"] <= memory_limit else "FAIL")
    )
    token_gate = (
        "NOT_VERIFIED"
        if token_limit is None
        else (
            "PASS"
            if target["estimated_context_tokens"] <= token_limit
            else "FAIL"
        )
    )
    if memory_gate == "FAIL":
        regressions.append("memory_peak_bytes")
    if token_gate == "FAIL":
        regressions.append("estimated_context_tokens")
    verdict = (
        "FAIL"
        if regressions
        else (
            "PARTIAL"
            if "NOT_VERIFIED" in {memory_gate, token_gate}
            else "PASS"
        )
    )
    return {
        "verdict": verdict,
        "target_control_count": target_count,
        "regressions": sorted(regressions),
        "memory_gate": memory_gate,
        "context_token_gate": token_gate,
    }


def _safe_output(path: Path) -> Path:
    output = path.expanduser().absolute()
    current = output
    while True:
        if current.is_symlink():
            raise BenchmarkContractError("unsafe_performance_output")
        if current.exists():
            break
        if current.parent == current:
            break
        current = current.parent
    output.mkdir(parents=True, exist_ok=True)
    if any(output.iterdir()):
        raise BenchmarkContractError("performance_output_not_empty")
    return output


def run_scale_benchmark(
    *,
    sizes: Sequence[int],
    seed: int,
    repeats: int,
    thresholds: Mapping[str, Any],
    output: Path,
) -> dict[str, Any]:
    if (
        not sizes
        or any(size not in ALLOWED_SIZES for size in sizes)
        or len(set(sizes)) != len(sizes)
    ):
        raise BenchmarkContractError("invalid_scale_sizes")
    if not isinstance(repeats, int) or repeats < 2 or repeats > 30:
        raise BenchmarkContractError("invalid_scale_repeats")
    destination = _safe_output(output)
    datasets: list[dict[str, Any]] = []
    raw_samples: dict[str, Any] = {}
    for count in sorted(sizes):
        dataset = generate_scale_dataset(count, seed=seed)
        tracemalloc.start()
        pack = compile_scale_dataset(dataset)
        _, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        compile_samples: list[float] = []
        verify_samples: list[float] = []
        for _ in range(repeats):
            started = time.perf_counter_ns()
            candidate = compile_scale_dataset(dataset)
            finished = time.perf_counter_ns()
            compile_samples.append(_milliseconds(started, finished))
            started = time.perf_counter_ns()
            verification = verify_scale_pack(candidate)
            finished = time.perf_counter_ns()
            verify_samples.append(_milliseconds(started, finished))
            if verification["status"] != "PASS" or candidate != pack:
                raise BenchmarkContractError("scale_verification_failed")
        profile = (
            "STRESS_OBSERVATION"
            if count == 50000
            else ("RELEASE_TARGET" if count == 10000 else "SUPPORTING_DATASET")
        )
        datasets.append(
            {
                "control_count": count,
                "profile": profile,
                "eligible_release_target": count == 10000,
                "compile_median_ms": statistics.median(compile_samples),
                "compile_p95_ms": _p95(compile_samples),
                "verify_median_ms": statistics.median(verify_samples),
                "verify_p95_ms": _p95(verify_samples),
                "memory_peak_bytes": peak,
                "pack_size_bytes": len(pack),
                "estimated_context_tokens": math.ceil(len(pack) / 4),
                "dataset_sha256": hashlib.sha256(
                    _canonical_bytes(dataset)
                ).hexdigest(),
                "pack_sha256": hashlib.sha256(pack).hexdigest(),
            }
        )
        raw_samples[str(count)] = {
            "compile_ms": compile_samples,
            "verify_ms": verify_samples,
        }
    evaluation = evaluate_scale_results(datasets, thresholds)
    environment = {
        "python": platform.python_version(),
        "implementation": platform.python_implementation(),
        "platform": platform.platform(),
        "executable": sys.executable,
    }
    report = {
        "schema_version": 1,
        "benchmark_kind": "synthetic_control_scale_kernel",
        "full_product_compiler_claim": "NOT_VERIFIED",
        "seed": seed,
        "repeats": repeats,
        "datasets": datasets,
        "environment": environment,
        **evaluation,
    }
    for name, value in (
        ("PERFORMANCE_RESULTS.json", report),
        ("RAW_SAMPLES.json", raw_samples),
        ("ENVIRONMENT.json", environment),
        ("THRESHOLDS.json", dict(thresholds)),
    ):
        (destination / name).write_bytes(_canonical_bytes(value))
    return report
