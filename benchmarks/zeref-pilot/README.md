# Zeref Boundary Pilot

This pilot exercises the operational boundary:

```text
project manifest
-> deterministic Grimoire pack
-> plan-bound profile v2
-> bounded Codex harness execution with the installed Zeref continuity layer
-> receipt v1
-> Grimoire receipt verification
-> separate reproduction attestation
```

The primary run cannot prove itself. It remains `PARTIAL` with
`ZEREF_EXECUTION_STATUS=NOT_VERIFIED`. A separate reviewer must rerun the same
exact-commit inputs and produce a detached attestation before the scoped pilot
can report `PASS`.

The attestation is an audit record. It does not provide cryptographic reviewer
identity, change Zeref internals, promote memory, use credentials, deploy,
publish, or claim that Zeref is a standalone harness.

## Run

```bash
PILOT_TIMESTAMP="$(python3 -c \
  'from datetime import datetime, timezone; print(datetime.now(timezone.utc).isoformat())')"

python3 benchmarks/zeref-pilot/run.py run \
  --output artifacts/zeref-pilot/primary \
  --commit-after "$(git rev-parse HEAD)" \
  --timestamp "$PILOT_TIMESTAMP"
```

Run the same command into a separate output directory from a clean checkout,
then attest and verify:

```bash
python3 benchmarks/zeref-pilot/run.py run \
  --output artifacts/zeref-pilot/reproduction \
  --commit-after "$(git rev-parse HEAD)" \
  --timestamp "$PILOT_TIMESTAMP"

python3 benchmarks/zeref-pilot/run.py attest \
  --primary artifacts/zeref-pilot/primary \
  --reproduction artifacts/zeref-pilot/reproduction \
  --output artifacts/zeref-pilot/attestation.json \
  --reviewer independent-reviewer \
  --producer primary-agent

python3 benchmarks/zeref-pilot/run.py verify \
  --primary artifacts/zeref-pilot/primary \
  --reproduction artifacts/zeref-pilot/reproduction \
  --attestation artifacts/zeref-pilot/attestation.json
```

Both runs must use the same recorded timestamp for byte-comparable pack hashes.
If `--timestamp` is omitted, the command records its actual UTC execution time,
which is useful for a primary run but is not an exact deterministic replay.
