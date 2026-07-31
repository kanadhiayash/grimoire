"""Executable benchmark evidence contracts."""

from .runner import (
    BenchmarkContractError,
    compare_benchmark_results,
    load_benchmark_suite,
    run_benchmark_suite,
    validate_benchmark_result,
)
from .gold import load_gold_scenarios, run_gold_scenarios
from .trust_boundaries import run_trust_boundary_suite
from .performance import (
    compile_scale_dataset,
    evaluate_scale_results,
    generate_scale_dataset,
    run_scale_benchmark,
    verify_scale_pack,
)
from .release_candidate import (
    compare_release_candidate_runs,
    load_release_candidate_suite,
    run_release_candidate,
    validate_release_candidate_run,
)

__all__ = [
    "BenchmarkContractError",
    "compare_benchmark_results",
    "load_benchmark_suite",
    "load_gold_scenarios",
    "run_benchmark_suite",
    "run_gold_scenarios",
    "run_trust_boundary_suite",
    "compile_scale_dataset",
    "evaluate_scale_results",
    "generate_scale_dataset",
    "run_scale_benchmark",
    "verify_scale_pack",
    "validate_benchmark_result",
    "compare_release_candidate_runs",
    "load_release_candidate_suite",
    "run_release_candidate",
    "validate_release_candidate_run",
]
