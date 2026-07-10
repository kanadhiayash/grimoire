# Context Loading

Do not ask every harness to read the full standards repository on every task.

Projects should expose a compact local bootstrap plus a manifest that selects:

- Standards version
- Enforcement profile
- Relevant stack overlays
- Project-specific instructions
- Approved exceptions

Load detailed standards only when relevant to the task.
