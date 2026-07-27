# Cross-Surface Zeref Activation

Grimoire owns activation portability. Zeref Memory Engine owns its runtime, memory, agents, skills, permissions, and canonical boot contract.

## One-way dependency

```text
Grimoire detects, activates, or simulates Zeref.
Zeref does not depend on Grimoire.
```

Do not modify the Zeref repository from this control plane.

## Surface classes

### Local harnesses

Claude Code, Codex, Gemini CLI, Cursor, Windsurf, Copilot, and compatible agents may use the real Zeref runtime when both runtime capability and the applicable project contract are verified.

### Browser projects

ChatGPT Projects, Claude Projects, Gemini Gems, and comparable knowledge workspaces use `PROJECT_SIMULATION` when a complete source pack is loaded. They may reproduce Zeref-style operating discipline but must not claim that local plugins, hooks, CLI commands, snapshots, or the canonical memory writer ran.

### Browser chats

Ordinary chats with a complete attached pack use `CHAT_SIMULATION`. The state is session-bound until an approved source file is saved or re-uploaded.

## Activation state machine

Use exactly one state:

- `RUNTIME_FULL`
- `RUNTIME_PARTIAL`
- `PROJECT_SIMULATION`
- `CHAT_SIMULATION`
- `INSTRUCTION_ONLY`
- `UNAVAILABLE`
- `NOT_VERIFIED`

Every session reports an activation receipt:

```text
[zeref] status=<STATUS> source=<SOURCE> runtime=<RUNTIME>
```

## Detection

1. Identify the surface.
2. Inspect applicable instructions and source files.
3. Verify runtime capability when the surface can access the local environment.
4. Validate source-pack completeness and hashes on browser surfaces.
5. Classify one activation state.
6. Defer to Zeref only when the real runtime contract is applicable.
7. Fall back to Grimoire without inventing Zeref state.

## Power controls

- Source manifests pin both canonical repositories and hash every managed file.
- Freshness budgets surface stale packs without silently replacing them.
- Activation, verification, writeback, and external actions produce receipts.
- Browser memory remains staged until an approved writeback is persisted.
- Adapters never duplicate Zeref internals or command registries.
- Unsupported surfaces report `NOT_VERIFIED`.

## Hard boundaries

Do not:

- claim full runtime from links or uploaded instructions alone;
- claim canonical memory on browser surfaces;
- silently refresh to a newer live policy revision;
- copy Zeref's internal agents, skills, model routing, or memory implementation;
- modify the Zeref repository;
- weaken approval, privacy, security, or verification controls.
