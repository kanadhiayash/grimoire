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
  --approval-approver kanadhiayash \
  --approval-timestamp "$(python3 - <<'PY'
from datetime import datetime, timezone
print(datetime.now(timezone.utc).isoformat())
PY
)" \
  --private-release-approval \
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

The `FINAL_RELEASE_DECISION_V1` contract returns exit code `0` only when the
exact commit, three candidate runs, comparison, release evidence, version
files, freshness, approval, and every hard gate agree. It returns exit code `1`
and status `BLOCKED` with stable reason codes when a boundary is unsatisfied.
Exit code `2` means the input package is malformed or unreadable. Use
`--require-tag` only for post-tag reporting, or run:

```bash
python3 scripts/release_preflight.py verify-tag \
  --expected-sha "$COMMIT" \
  --tag v1.0.0
```

The evidence command cannot sign, publish, deploy, create a tag, or create a
GitHub release. A successful evidence verification is not release approval
unless the exact-commit approval record is present and current. The
`APPROVED_NOT_CRYPTOGRAPHIC` marker is private release assurance, not a
cryptographic identity signature. Benchmark evidence must be a complete
Grimoire benchmark package bound to the same commit. Symlinked release inputs
are rejected.

The final preflight is also non-mutating. It requires the repository version,
baseline, index, dated changelog entry, and final release document to move as
one reviewed commit. It binds all three packages to the checked-in canonical
suite and source tree, recomputes the comparison rather than trusting the
supplied summary, rejects any hard gate below `PASS`, reports approval and
self-attested timestamp gaps, and can independently verify the tag binding.
It does not create a tag, release object, package, deployment, publication, or
cryptographic signature.
