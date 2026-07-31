# Grimoire Quickstart

This guide is the shortest human path from repository checkout to a verified operation.

## Technology choices

Grimoire deliberately uses a small, portable stack:

- **Python 3.11+ standard library** for policy checks, compilation, installers, and the unified CLI
- **JSON and JSON Schema** for machine-readable contracts
- **Markdown** for human and AI-agent instructions
- **Bash or Zsh** only as thin launchers
- **GitHub Actions YAML** for continuous integration

Do not introduce TypeScript, Go, Rust, a database, or a web framework unless a measured requirement cannot be met by this stack.

## 1. Inspect repository state

```bash
python3 scripts/grimoire.py status
```

Machine-readable output:

```bash
python3 scripts/grimoire.py status --json
```

Read the full machine catalog:

```bash
python3 scripts/grimoire.py catalog --json
```

## 2. Run verification

```bash
python3 scripts/grimoire.py check
```

Equivalent convenience command:

```bash
make check
```

A valid completion claim requires all reported steps to pass.

Write a JSON check report:

```bash
python3 scripts/grimoire.py check \
  --json-output artifacts/grimoire-check.json
```

Run the public, non-mutating command smoke:

```bash
python3 scripts/verify_documented_commands.py --json
```

## 3. Compile and verify a project pack

```bash
python3 scripts/grimoire.py project boot \
  --manifest templates/project/project.json \
  --output artifacts/example-project-pack \
  --deterministic \
  --generated-at 2026-01-01T00:00:00+00:00

python3 scripts/grimoire.py project verify \
  --directory artifacts/example-project-pack \
  --mode offline
```

This path is executable and covered by the command smoke. Structural
verification does not raise project readiness, release assurance, legal review,
or Zeref execution.

## 4. Compile a browser project pack

```bash
python3 scripts/grimoire.py pack compile \
  --surface chatgpt-project \
  --project-name "Example Project" \
  --output ./dist/example-project \
  --grimoire-commit <40-character-sha> \
  --zeref-commit <40-character-sha>
```

Supported browser surfaces:

- `chatgpt-project`
- `claude-project`
- `gemini-gem`
- `generic-chat`

Verify the generated pack:

```bash
python3 scripts/grimoire.py pack verify ./dist/example-project
```

The browser-pack command contract is tested. A real pack remains
`NOT_VERIFIED` until both 40-character source commits are replaced with reviewed
values and the generated pack is independently verified.

## 5. Manage local harness adapters

Detect current state:

```bash
python3 scripts/grimoire.py harness detect
```

Preview changes:

```bash
python3 scripts/grimoire.py harness plan
```

Apply managed blocks:

```bash
python3 scripts/grimoire.py harness apply
```

Verify installation:

```bash
python3 scripts/grimoire.py harness verify
```

Remove only managed blocks:

```bash
python3 scripts/grimoire.py harness uninstall
```

`detect` and `plan` are read-only. `apply` and `uninstall` modify user-level
harness files and remain `NOT_VERIFIED` in the public command smoke; run them
only with explicit approval and a reviewed plan.

## 6. Run a benchmark

```bash
COMMIT="$(git rev-parse HEAD)"
python3 scripts/grimoire.py benchmark run \
  --suite benchmarks/suites/runner-smoke.json \
  --output artifacts/benchmark-smoke \
  --commit "$COMMIT"
```

The output retains raw stdout, stderr, environment, sources, hashes, hard-gate
status, and a scorecard without awarding an overall product score.

## 7. Review release evidence

See [`release-evidence-and-rollback.md`](release-evidence-and-rollback.md).
Release evidence generation and structural verification are executable.
Signing, publication, deployment, and release creation remain
`NOT_VERIFIED` until their separate approval gates are satisfied.

## Operating boundaries

- Grimoire compiles and verifies Zeref boundary contracts.
- It does not own or rewrite Zeref runtime internals.
- Browser project simulation is not proof that a local Zeref runtime executed.
- Merge, deploy, publish, send, delete, rename, credentials, and canonical memory promotion require explicit approval.
- Consuming projects should pin released standards versions and reviewed source commits.
- The repository release version and manifest standards policy version are
  independent. The current manifest policy pin is `0.4.0`.
- Windows and external Zeref runtime execution remain `NOT_VERIFIED`.

## Where to go next

- Humans: [`README.md`](../../README.md)
- AI agents: [`docs/operations/agent-entrypoint.md`](agent-entrypoint.md)
- Repository contract: [`AGENTS.md`](../../AGENTS.md)
- Machine catalog: [`REPOSITORY_INDEX.json`](../../REPOSITORY_INDEX.json)
- Governance: [`GOVERNANCE.md`](../../GOVERNANCE.md)
- Migration: [`docs/migrations/0.5.x-to-1.0.md`](../migrations/0.5.x-to-1.0.md)
- Command contract: [`command-verification.json`](command-verification.json)
