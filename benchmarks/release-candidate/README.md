# Release-Candidate Benchmark

This benchmark runs the complete Grimoire release-candidate contract against one
clean, exact Git commit. It retains raw command output, environment facts, input
hashes, timestamps, exit codes, and conservative status results.

Run one package only from a clean checkout:

```bash
commit="$(git rev-parse HEAD)"
python3 benchmarks/release-candidate/run.py run \
  --suite benchmarks/release-candidate/suite.json \
  --output artifacts/release-candidate/run-1 \
  --expected-commit "$commit" \
  --run-id run-1
```

Compare three independently produced packages:

```bash
python3 benchmarks/release-candidate/run.py compare \
  --run artifacts/release-candidate/run-1 \
  --run artifacts/release-candidate/run-2 \
  --run artifacts/release-candidate/run-3 \
  --expected-commit "$commit" \
  --output artifacts/release-candidate/comparison.json
```

The GitHub workflow is the canonical clean-environment reproduction. It checks
out the exact pull-request head in three separate jobs, rejects dirty state,
uploads every package, and compares the downloaded evidence.

`NOT_VERIFIED` is a valid evidence result, not a passing substitute. The current
suite deliberately reports the external Zeref runtime gate as `NOT_VERIFIED`
until an independently trusted runtime receipt exists. The runner never emits
an aggregate product score or a 10/10 claim.
