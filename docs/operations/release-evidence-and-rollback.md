# Release Evidence and Rollback

Create a complete benchmark package and generate private evidence from
exact-commit inputs:

```bash
COMMIT="$(git rev-parse HEAD)"
python3 scripts/benchmark_runner.py run \
  --suite benchmarks/suites/runner-smoke.json \
  --output artifacts/release-inputs/benchmark \
  --commit "$COMMIT"

python3 scripts/release_evidence.py generate \
  --artifact artifacts/release-inputs/grimoire-check.json \
  --benchmark artifacts/release-inputs/benchmark/BENCHMARK_RESULTS.json \
  --expected-sha "$COMMIT" \
  --output artifacts/release/evidence.json
```

Verify and rehearse rollback without mutating Git or GitHub:

```bash
python3 scripts/release_evidence.py verify \
  --evidence artifacts/release/evidence.json \
  --expected-sha "$COMMIT"

python3 scripts/release_evidence.py rollback-dry-run \
  --evidence artifacts/release/evidence.json \
  --expected-sha "$COMMIT"
```

The evidence command cannot sign, publish, deploy, create a tag, or create a
GitHub release. A successful evidence verification is not release approval.
Signature and release assurance remain `NOT_VERIFIED` until their separate
owner-approved gates are satisfied. Benchmark evidence must be a complete
Grimoire benchmark package bound to the same commit. Symlinked release inputs
are rejected.
