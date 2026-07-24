# Priority, Severity, Risk, Evidence, and Gate Taxonomy

## Purpose

Prevent urgency, impact, uncertainty, effort, and release blocking from being collapsed into one label.

## Priority

- `P0`: active incident, safety risk, data loss, exploitable security exposure, regulatory breach, or critical service unavailable.
- `P1`: release blocker or major user or business harm requiring the next active work window.
- `P2`: planned product or engineering work.
- `P3`: valid backlog, research, or low-impact optimization.

A P0 requires owner, reason, timestamp, next action, and review or expiry time.

## Severity

- `S0`: catastrophic or irreversible harm.
- `S1`: critical harm or complete core-function loss.
- `S2`: major degradation or material user harm.
- `S3`: limited degradation with a viable workaround.
- `S4`: cosmetic or negligible impact.

## Risk

Risk is recorded as probability, impact, exposure, mitigation, owner, trigger, and residual risk. Allowed summary levels are `critical`, `high`, `moderate`, and `low`.

## Evidence confidence

- `VERIFIED`
- `SUPPORTED`
- `ASSUMPTION`
- `UNKNOWN`
- `CONFLICTED`

## Gate effect

- `BLOCKING`
- `WARNING`
- `ADVISORY`

Priority changes belong in issue or record metadata, not filenames.
