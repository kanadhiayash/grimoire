# AI Agent Entrypoint

This document routes AI agents through Grimoire without requiring a full-repository scan.

## Boot protocol

Before material work:

1. Read root `AGENTS.md`.
2. Read `REPOSITORY_INDEX.json`.
3. Run `python3 scripts/grimoire.py status --json` when command execution is available.
4. Read only the canonical sources and task-specific files selected below.
5. Inspect existing implementation patterns before editing.
6. Define verification before changing behavior.

If the repository index conflicts with the filesystem, report the drift. Do not invent the missing file or silently trust the stale index.

## Task routing

| Task | Required sources |
|---|---|
| Change universal behavior | `AGENTS.md`, `policies/baseline.json`, relevant standard, tests |
| Change AI command semantics | `policies/ai-operations.json`, its schema, governance standard, adapter contract, tests |
| Change activation behavior | `policies/surface-activation.json`, its schema, cross-surface standard, capability matrix, tests |
| Change an adapter | Canonical policy, adapter contract, target adapter, matching tests |
| Change browser packs | Source-pack standard, templates, compiler, verifier, browser-pack tests |
| Change installer behavior | Installer, activation policy, installer tests, privacy and approval boundaries |
| Change repository navigation | `REPOSITORY_INDEX.json`, schema, index checker, CLI, agent and human guides |
| Prepare a release | `GOVERNANCE.md`, `CHANGELOG.md`, `VERSION`, compatibility and migration evidence |

## Source authority

Use the canonical precedence in `policies/ai-operations.json`:

1. Platform, law, and safety requirements
2. Current explicit user instruction
3. Approved plan and revision
4. Repository contract, including `AGENTS.md`, security, privacy, governance, and active profile
5. Project instructions
6. Global instructions
7. Verified canonical memory
8. Historical handoffs
9. External references
10. General knowledge

Same-level conflicts require arbitration. Never resolve them silently.

## Operational commands

Machine status:

```bash
python3 scripts/grimoire.py status --json
```

Machine catalog:

```bash
python3 scripts/grimoire.py catalog --json
```

Full verification:

```bash
python3 scripts/grimoire.py check
```

Use `REPOSITORY_INDEX.json` for the complete command catalog and supported-surface map.

## Change discipline

- Make the smallest complete change.
- Preserve exact paths, keys, commands, and error messages.
- Add or update tests before or with behavior changes.
- Do not weaken a gate to obtain a pass.
- Do not add another policy source, command registry, autonomy scale, or memory lifecycle.
- Do not claim a council ran unless independent work actually ran.
- Do not claim browser simulation is local runtime execution.
- Do not modify `kanadhiayash/zeref-memory-engine` under an Grimoire task unless the user separately approves that repository and scope.

## Required completion evidence

Report:

- objective;
- files changed;
- behavior changed;
- commands run;
- exact verification results;
- untouched scope;
- remaining risks and unknowns;
- recommended next action.

Use only `PASS`, `PARTIAL`, `BLOCKED`, or `NOT_VERIFIED` as machine completion states.
