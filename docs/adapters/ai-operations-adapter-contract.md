# AI Operations Adapter Contract

Harness adapters translate Engineering Standards into the smallest instruction set a surface can reliably consume.

## Authority

Adapters are not canonical policy. They defer to:

1. Repository security and privacy policy
2. Root `AGENTS.md`
3. Active standards profile
4. `policies/ai-operations.json`
5. Relevant stack overlays

An approved task plan operates inside these boundaries. It cannot weaken them.

## Required semantics

Every adapter that supports material work must preserve:

- Read before editing
- Smallest complete change
- Facts, assumptions, unknowns, risks, and conflicts when material
- Present-day verification for current or unstable claims
- Bounded autonomy
- Approval binding for external or destructive actions
- Exact verification reporting
- Honest tool and council claims
- Staged memory promotion
- Stop conditions
- Completion statuses: `PASS`, `PARTIAL`, `BLOCKED`, `NOT_VERIFIED`

## Surface-specific content

Adapters may add:

- Tool names and availability
- File-discovery behavior
- Context limits
- Local project boot order
- Artifact or connector rules
- Platform-specific safety requirements

Adapters must not add:

- A second command registry
- A different autonomy scale
- Looser approval rules
- A different memory lifecycle
- Unsupported tool or model claims
- Personal or project facts that belong in project configuration

## Drift review

Before release, compare adapters against `policies/ai-operations.json`.

A drift finding is any adapter that:

- silently escalates autonomy
- changes command meaning
- treats vague agreement as approval
- claims independent agents that did not run
- permits canonical memory writes without validation
- changes completion status semantics
- omits a hard stop required by policy
