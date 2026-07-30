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

__all__ = [
    "BenchmarkContractError",
    "compare_benchmark_results",
    "load_benchmark_suite",
    "load_gold_scenarios",
    "run_benchmark_suite",
    "run_gold_scenarios",
    "run_trust_boundary_suite",
    "validate_benchmark_result",
]
