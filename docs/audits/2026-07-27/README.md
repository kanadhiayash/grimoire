# Grimoire 0.5.0 audit baseline

This directory freezes the July 27, 2026 audit of Grimoire `0.5.0` at commit
`72015acac8a57146ad8b00a6c7b4725b8d86a9c8`.

The imported package is evidence, not a current score. The audited score remains
`5.4/10`. This pull request performs no current re-score and makes no production
behavior change.

## Evidence classes

- `HISTORICAL_AUDITED_BASELINE`: a claim preserved from the supplied audit.
- `HISTORICAL_REPORTED`: a supplied result whose original raw inputs or runner
  were not available.
- `FRESH_DETERMINISTIC_BASELINE`: a new run using the committed runner,
  fixtures, and seed.
- `MATCH`: the fresh observation matches the expected audited failure.
- `FAIL`: the product behavior is still incorrect.
- `NOT_VERIFIED`: current evidence cannot prove the claim.

A reproduced failure is recorded as product `FAIL` and reproduction `MATCH`.
`MATCH` never converts a product failure into `PASS`.

## Locked subject

| Field | Value |
|---|---|
| Repository | `kanadhiayash/grimoire` |
| Release | `0.5.0` |
| Audited commit | `72015acac8a57146ad8b00a6c7b4725b8d86a9c8` |
| Plan | `GRM-1.0-P0P1-2026-07-27`, revision `1` |
| Imported package | `execution-package/` |
| Machine baseline | `BASELINE.json` |

The package contains files `00` through `18`. The checksum ledger verifies files
`00` through `17`; the ledger itself is pinned by SHA-256
`f13730c67915095d8c2488cfb30236661200a5839218a2d13353efb1e7bd6264`.

## Reproduction

Run from the repository root:

```bash
python3 scripts/grimoire.py check \
  --json-output artifacts/audit/2026-07-27/grimoire-check.json

python3 benchmarks/audit/2026-07-27/reproduce.py \
  --expected-commit 72015acac8a57146ad8b00a6c7b4725b8d86a9c8 \
  --seed 20260727 \
  --output artifacts/audit/2026-07-27
```

The reproducer requires the audited commit to be the current branch head or an
ancestor. It verifies the imported package and fixture hashes before running.
It also pins the exact compiler, AI policy, and AI schema bytes used by the
reproduction so working-tree drift cannot be attributed to the audited commit.
All compiler outputs, including the symlink target used by the adversarial
case, stay inside a fresh temporary directory.

The fresh deterministic 500-case run produced:

| Outcome | Count |
|---|---:|
| Controlled rejection | 160 |
| Unhandled exception | 171 |
| Accepted | 169 |

Fresh corpus SHA-256:
`cc67f1ee239f7c332c89389077f05efcbcb18b90f87ab622a365af9ca5bff3f6`.

The original audit reported `171` controlled rejections, `214` unhandled
exceptions, and `115` accepted cases. Its generator, seed, 500 inputs, and raw
logs were not supplied. Those numbers remain `HISTORICAL_REPORTED` and
`NOT_VERIFIED`; the new run does not claim to reproduce them.

## Finding coverage

| Finding | Product status | Reproduction | Evidence |
|---|---|---|---|
| False project readiness | `FAIL` | `MATCH` | `false-project-readiness.json` |
| AI Operations schema contradiction | `FAIL` | `MATCH` | `ai-schema-contradiction.json` |
| Malformed manifest acceptance and crashes | `FAIL` | `MATCH` | six `manifest-*.json` fixtures |
| Prompt injection in AI context | `FAIL` | `MATCH` | `prompt-injection.json` |
| Symlink overwrite | `FAIL` | `MATCH` | `symlink-overwrite.json` |
| Dirty output retention | `FAIL` | `MATCH` | `dirty-output.json` |
| No actual standards resolution | `FAIL` | Documented limitation | Current compiler emits general principles; Phase 3 owns the fix |
| Normative self-compliance at 20.8% | `FAIL` | `HISTORICAL_REPORTED` | Original audit script was not supplied |
| Original performance and coverage values | `NOT_VERIFIED` | `HISTORICAL_REPORTED` | Original raw harness outputs were not supplied |
| Executable full benchmark runner | `FAIL` | Source inspection | Only this bounded audit reproducer exists in Phase 0 |
| Zeref round trip | `NOT_VERIFIED` | Documented limitation | No verified end-to-end receipt was supplied |

## Raw evidence

| Path | Content |
|---|---|
| `raw/grimoire-check.json` | Fresh clean-clone check at the audited commit, 60 tests |
| `raw/github-run.json` | Safe selected output from merge-commit CI run `30236282784` |
| `raw/reproduction-summary.json` | Finding observations and normalized result |
| `raw/fresh-fuzz-cases.json` | All 500 generated case IDs, input hashes, and classifications |
| `raw/environment.json` | Allowlisted OS and Python metadata |
| `raw/reproducer-stdout.txt` | Exact reproducer standard output |
| `raw/reproducer-stderr.txt` | Exact reproducer standard error |
| `raw/reproducer-hashes.json` | SHA-256 values for generated runner evidence |

The environment record includes only an allowlist. It does not capture tokens,
credentials, unrestricted environment variables, or manifest payload values.

## Known conflicts and boundaries

- The repository README says the repository will later be renamed. Locked
  decision DEC-002 says Grimoire is the permanent repository name and Standards
  Orchestrator is the capability. This conflict is reported only; it is outside
  PR 0.1.
- Production fixes begin in later focused pull requests.
- No merge, release, deployment, publication, Zeref change, plugin change, or
  runtime dependency is authorized by this baseline.
