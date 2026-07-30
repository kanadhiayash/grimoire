# Performance and Scale Benchmark

This benchmark generates deterministic synthetic control records at 100, 1,000, 10,000, and 50,000 controls. It measures canonical scale-kernel compilation, offline pack verification, peak traced memory, pack bytes, and a clearly labeled byte-based context-token estimate.

Run the full matrix:

```bash
python3 benchmarks/performance/run.py \
  --sizes 100 1000 10000 50000 \
  --seed 20260730 \
  --repeats 7 \
  --output artifacts/performance/full
```

The 10,000-control thresholds come from the canonical benchmark standard. No memory budget or context-token ceiling has been approved, so those gates remain `NOT_VERIFIED`. The 50,000-control dataset is always `STRESS_OBSERVATION` and is never eligible to be labeled a release target.

Warning: these results measure the synthetic scale kernel, not the full project compiler, deployment, or production environment. Environment variance is expected. They do not create release-readiness or overall product assurance.
