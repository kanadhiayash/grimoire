# Gold Product Scenarios

This fixture contains 16 product scenarios covering the minimum matrix in the benchmark standard, including both regulated-health and non-regulated wellness variants.

Each scenario pins:

- a strictly validated project manifest;
- the exact 45-control state vector through a canonical digest and state counts;
- required documents;
- the derived evidence-set digest and count;
- critical controls;
- counsel questions;
- the conservative expected status.

Run:

```bash
python3 benchmarks/scenarios/gold/run.py
```

The runner compiles and offline-verifies every pack. It reports overall recall, precision, and counsel-routing accuracy as `NOT_VERIFIED` until reviewed engines produce those measures. It never treats fixture presence as compliance, accessibility, security, release, or legal proof.

`SOURCE_MANIFEST.json` makes fixture changes visible. Update it only with a separately reviewed expectation change.
