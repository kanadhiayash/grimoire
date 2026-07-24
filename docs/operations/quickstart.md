# Engineering Standards Quickstart

This guide is the shortest human path from repository checkout to a verified operation.

## Technology choices

Engineering Standards deliberately uses a small, portable stack:

- **Python 3.11+ standard library** for policy checks, compilation, installers, and the unified CLI
- **JSON and JSON Schema** for machine-readable contracts
- **Markdown** for human and AI-agent instructions
- **Bash or Zsh** only as thin launchers
- **GitHub Actions YAML** for continuous integration

Do not introduce TypeScript, Go, Rust, a database, or a web framework unless a measured requirement cannot be met by this stack.

## 1. Inspect repository state

```bash
python3 scripts/standards.py status
```

Machine-readable output:

```bash
python3 scripts/standards.py status --json
```

Read the full machine catalog:

```bash
python3 scripts/standards.py catalog --json
```

## 2. Run verification

```bash
python3 scripts/standards.py check
```

Equivalent convenience command:

```bash
make check
```

A valid completion claim requires all reported steps to pass.

Write a JSON check report:

```bash
python3 scripts/standards.py check \
  --json-output artifacts/standards-check.json
```

## 3. Compile a browser project pack

```bash
python3 scripts/standards.py pack compile \
  --surface chatgpt-project \
  --project-name "Example Project" \
  --output ./dist/example-project \
  --engineering-standards-commit <40-character-sha> \
  --zeref-commit <40-character-sha>
```

Supported browser surfaces:

- `chatgpt-project`
- `claude-project`
- `gemini-gem`
- `generic-chat`

Verify the generated pack:

```bash
python3 scripts/standards.py pack verify ./dist/example-project
```

## 4. Manage local harness adapters

Detect current state:

```bash
python3 scripts/standards.py harness detect
```

Preview changes:

```bash
python3 scripts/standards.py harness plan
```

Apply managed blocks:

```bash
python3 scripts/standards.py harness apply
```

Verify installation:

```bash
python3 scripts/standards.py harness verify
```

Remove only managed blocks:

```bash
python3 scripts/standards.py harness uninstall
```

## Operating boundaries

- Engineering Standards may detect, activate, or simulate Zeref operations.
- It does not own or rewrite Zeref runtime internals.
- Browser project simulation is not proof that a local Zeref runtime executed.
- Merge, deploy, publish, send, delete, rename, credentials, and canonical memory promotion require explicit approval.
- Consuming projects should pin released standards versions and reviewed source commits.

## Where to go next

- Humans: [`README.md`](../../README.md)
- AI agents: [`docs/operations/agent-entrypoint.md`](agent-entrypoint.md)
- Repository contract: [`AGENTS.md`](../../AGENTS.md)
- Machine catalog: [`REPOSITORY_INDEX.json`](../../REPOSITORY_INDEX.json)
- Governance: [`GOVERNANCE.md`](../../GOVERNANCE.md)
