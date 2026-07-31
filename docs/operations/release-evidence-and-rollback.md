# Release Evidence and Rollback

Generate a private test evidence package from existing exact-commit artifacts:

```bash
COMMIT="$(git rev-parse HEAD)"
python3 scripts/release_evidence.py generate \
  --artifact artifacts/release-inputs/grimoire-check.json \
  --benchmark artifacts/release-inputs/grimoire-check.json \
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
owner-approved gates are satisfied.
