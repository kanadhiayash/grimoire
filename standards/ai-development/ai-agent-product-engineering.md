# AI and Agent Product Engineering

## Purpose

Design and operate AI features and agents with bounded authority, measurable quality, secure tools, human control, and cost limits.

## Expected outcome

Model behavior, context, tools, data, evaluation, oversight, failure, security, cost, and change management are explicit and verified.

## Applicability

User-facing AI, internal copilots, retrieval systems, automated decisions, generative features, tool-using agents, and multi-agent workflows.

## Non-applicability

Non-AI deterministic automation uses ordinary engineering standards but still requires permissions and verification.

## Required inputs

User need, task risk, model and vendor options, data sources, tools, permissions, evaluation set, latency, cost, and legal controls.

## Unknowns to resolve

Training and retention terms, data provenance, model failure modes, tool authority, human review, fallback, and disable behavior.

## Required actions

Define model routing, prompt and context ownership, retrieval provenance, tool schemas, least privilege, output validation, evaluation, prompt-injection defense, human oversight, memory, versioning, monitoring, fallback, and shutdown.

## Required decisions

Model, vendor, data use, context budget, tools, autonomy, approvals, memory, evaluation thresholds, escalation, and incident ownership.

## Required details

Task, actor, input, source, model, tool, permission, output contract, validator, confidence or uncertainty behavior, failure, cost, and owner.

## Expected documents and artifacts

AI product brief, model and data card, threat model, tool-permission matrix, evaluation plan and report, human-oversight plan, cost budget, incident plan, and change log.

## Document structure

Each capability records purpose, user, data, model, tools, authority, constraints, evaluations, failures, fallback, monitoring, cost, and owner.

## Acceptance criteria

- A deterministic solution was considered.
- Tool access is least privilege and scope-bound.
- Critical outputs are validated or reviewed.
- Evaluation covers quality, safety, security, accessibility, bias, and cost according to risk.
- Model, prompt, retrieval, and tool versions are traceable.
- Users can correct, appeal, or exit where appropriate.

## Verification method

Gold-set evaluation, adversarial evaluation, prompt-injection tests, tool-authorization tests, hallucination and source tests, load and cost tests, and human review.

## Evidence required

Evaluation data and results, traces without prohibited sensitive data, source records, tool receipts, cost report, and residual risks.

## Failure conditions

Unbounded agency, hidden model use, invented sources, unverified consequential output, unrestricted tools, silent model changes, or cost without limits.

## Risks and abuse cases

Prompt injection, data leakage, model denial of service, excessive agency, hallucination, biased decisions, automation bias, memory poisoning, and vendor drift.

## Guards and limits

Do not claim a council unless independent work occurred. Do not use expensive models for deterministic tasks without evidence. Do not let model output directly authorize sensitive external action.

## Exceptions

Record capability, risk, compensating control, approver, review date, and kill condition.

## Cost considerations

Track input, output, retrieval, cache, tool, vendor, evaluation, latency, and human-review cost per useful outcome.

## Dependencies

AI Operations, security, privacy, legal, accessibility, cloud, data, and product-design standards.

## Related standards

Zeref Integration and Minimum Correct Change.

## Source provenance

Use official model-provider terms and reviewed NIST, ISO, OWASP, MITRE, OECD, and regulator sources.

## Owner and review cycle

AI product and engineering owners. Review on model, prompt, tool, data, vendor, or risk changes.

## Zeref execution behavior

Use the lowest-cost sufficient model, smallest context, bounded roles and loops, explicit tool permissions, evaluation gates, and truthful receipts.

## Examples

A finance assistant drafts a plan with cited user data but requires confirmation before any external action.

## Anti-patterns

A general-purpose agent with broad credentials and no evaluation, budget, or stop condition.
