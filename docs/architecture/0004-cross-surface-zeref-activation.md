# ADR-0004: Activate Zeref across local and browser surfaces

- Status: Accepted
- Date: 2026-07-23
- Owner: Yash Kanadhia

## Context

Yash works across coding harnesses and browser chat or project surfaces. Local harnesses can inspect files and execute a real Zeref installation. Browser surfaces can load instructions and sources but cannot prove that local Zeref plugins, hooks, CLI commands, or the canonical memory writer ran.

Treating both surfaces as full runtime activation would create false capability and persistence claims.

## Decision

Grimoire will own a cross-surface activation policy and compile surface-specific adapters.

- Local harnesses detect and defer to the real Zeref runtime.
- Browser projects use source-backed `PROJECT_SIMULATION`.
- Browser chats use source-backed `CHAT_SIMULATION`.
- Links provide provenance, while uploaded snapshots provide active context.
- Every activation produces a truthful status receipt.
- Zeref Memory Engine remains unchanged and owns all runtime internals.

## Consequences

- One portable control plane supports coding and browser surfaces.
- Browser projects gain durable, reviewable state without false runtime claims.
- Source hashes and commit pins make packs reproducible.
- Stale or incomplete packs degrade explicitly.
- The Zeref repository has no reverse dependency on Grimoire.
