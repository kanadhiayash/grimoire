# Manifest Fuzz Benchmark

Run the complete deterministic Phase 1 gate:

```bash
python3 benchmarks/fuzz/manifest_fuzz.py \
  --cases 10000 \
  --seed 20260727 \
  --output artifacts/fuzz/manifest
```

The runner uses only the Python standard library and the Grimoire runtime. It
loads valid immutable corpus fixtures, generates every required mutation class,
and records:

- `cases.jsonl`: case ID, seed, mutation class, source fixture, mutated manifest,
  expected outcome, and input hash
- `results.jsonl`: controlled accept/reject/internal classification, structured
  diagnostics, and diagnostic hash
- `summary.json`: exact counts, hashes, runtime environment, and commit

`summary.json` also records `git_tree_state` and `commit_exact`. A local run
from an uncommitted working tree is valid exploratory evidence but is not
represented as exact-commit proof. Exact-commit evidence requires a clean tree,
which the full CI workflow verifies before execution.

The command requires at least 13 cases so every declared mutation class is
represented. It exits nonzero for any unexpected outcome or classified internal
failure. `unhandled_exceptions=0` means no exception escaped the per-case
classifier in a completed report; classified defects are counted separately as
`internal_failures`. Input strings are never executed or interpreted as
filesystem paths. Generated files use fixed names inside the requested output
directory. Symlinks in the output path are rejected, and case and report hashes
are rechecked immediately before artifacts are written.

The pull-request conformance workflow runs a fast subset. The separate Manifest
Fuzz Gate checks out the exact pull-request head and runs all 10,000 cases.
Scheduled runs repeat the complete suite and upload the raw artifacts.
