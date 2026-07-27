# AI Operations Adapter Contract

Harness and browser-surface adapters translate Grimoire into the smallest instruction set a surface can reliably consume.

## Authority

Adapters are not canonical policy. They defer to:

1. Applicable platform and safety requirements
2. The current explicit user instruction
3. The approved task plan and revision
4. The repository contract, including security, privacy, governance, active profile, and root `AGENTS.md`
5. Project instructions and configuration
6. `policies/ai-operations.json`
7. `policies/surface-activation.json`
8. Relevant stack overlays

An approved task plan operates inside these boundaries. It cannot weaken them. Same-level conflicts stop the affected action for arbitration.

## Required semantics

Every adapter that supports material work must preserve:

- Read before editing
- Smallest complete change
- Facts, assumptions, unknowns, risks, and conflicts when material
- Present-day verification for current or unstable claims
- Bounded autonomy
- Approval binding for external or destructive actions
- Exact verification reporting
- Honest tool, runtime, and council claims
- Staged memory promotion
- Stop conditions
- Completion statuses: `PASS`, `PARTIAL`, `BLOCKED`, `NOT_VERIFIED`

## Cross-surface activation

Every adapter must identify its surface class and select one activation state:

- `RUNTIME_FULL`
- `RUNTIME_PARTIAL`
- `PROJECT_SIMULATION`
- `CHAT_SIMULATION`
- `INSTRUCTION_ONLY`
- `UNAVAILABLE`
- `NOT_VERIFIED`

The adapter must emit an activation receipt and state its limitations.

Browser surfaces may simulate the operating workflow from a complete source pack. They may not claim local Zeref runtime execution, plugin or hook execution, canonical memory promotion, or automatic persistence.

## Surface-specific content

Adapters may add:

- Tool names and availability
- File-discovery behavior
- Context limits
- Local project boot order
- Artifact or connector rules
- Platform-specific safety requirements
- Project-source save or re-upload mechanics
- Diagnostics for loaded instruction sources

Adapters must not add:

- A second command registry
- A different autonomy scale
- Looser approval rules
- A different memory lifecycle
- Unsupported tool, runtime, or model claims
- Personal or project facts that belong in project configuration
- Zeref internal agents, skills, model routing, permissions, or boot details

## Source-pack requirements

A browser adapter must use the canonical browser source-pack read order, pinned commits, SHA-256 file hashes, generation timestamp, freshness budget, and memory disclaimer.

Links identify provenance. Uploaded snapshots are the active operating context. A live link must not silently replace the reviewed snapshot.

## Drift review

Before release, compare adapters against both machine policies.

A drift finding is any adapter that:

- silently escalates autonomy
- changes command meaning
- treats vague agreement as approval
- claims independent agents that did not run
- permits canonical memory writes without validation
- changes completion status semantics
- omits a hard stop required by policy
- claims full Zeref runtime from instructions or links alone
- changes source-pack activation state without evidence
- duplicates Zeref internals
