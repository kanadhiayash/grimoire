# Release Evidence and Rollback

Create a complete benchmark package and generate private evidence from
exact-commit inputs:

```bash
COMMIT="$(git rev-parse HEAD)"
python3 scripts/grimoire.py check \
  --json-output artifacts/release-inputs/grimoire-check.json

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

Run the final non-mutating preflight only after producing exactly three clean
release-candidate runs and their checked comparison:

```bash
python3 scripts/release_preflight.py preflight \
  --candidate-run artifacts/release-candidate/run-1 \
  --candidate-run artifacts/release-candidate/run-2 \
  --candidate-run artifacts/release-candidate/run-3 \
  --comparison artifacts/release-candidate/comparison.json \
  --release-evidence artifacts/release/evidence.json \
  --expected-sha "$COMMIT" \
  --version 1.0.0 \
  --tag v1.0.0
```

The current `BLOCKER_REPORT_V1` contract returns exit code `1` and status
`BLOCKED`; its stable reason codes identify the unsatisfied boundaries. Exit
code `0` is reserved for a future approved eligibility contract and is not
reachable in v1. Exit code `2` means the input package is malformed or
unreadable. Use `--require-tag` only for post-tag reporting, or run:

```bash
python3 scripts/release_preflight.py verify-tag \
  --expected-sha "$COMMIT" \
  --tag v1.0.0
```

The evidence command cannot sign, publish, deploy, create a tag, or create a
GitHub release. A successful evidence verification is not release approval.
Signature and release assurance remain `NOT_VERIFIED` until their separate
owner-approved gates are satisfied. Benchmark evidence must be a complete
Grimoire benchmark package bound to the same commit. Symlinked release inputs
are rejected.

The final preflight is also non-mutating. It requires the repository version,
baseline, index, dated changelog entry, and final release document to move as
one reviewed commit. It binds all three packages to the checked-in canonical
suite and source tree, recomputes the comparison rather than trusting the
supplied summary, rejects any hard gate below `PASS`, reports approval and
self-attested timestamp gaps, and can independently verify the tag binding.
External identity signature and trusted freshness are not configured inputs,
so v1 cannot authorize the release.
