# Inert Trust-Boundary Benchmark

This suite exercises controlled local rejection paths only. It uses temporary directories and does not perform network access, target probing, credential use, exploit development, external scanning, or offensive operations.

It covers benchmark output symlinks and replay, instruction-like manifest data, oversized and path-like manifest values, project-pack hash and receipt substitution, future timestamps, unexpected files, crosswalk substitution, and malformed or duplicate standard records.

Run:

```bash
python3 benchmarks/trust-boundaries/run.py \
  --output artifacts/trust-boundaries
```

A PASS applies only to the listed inert fixtures. It is not a security certification or proof about deployed systems.
