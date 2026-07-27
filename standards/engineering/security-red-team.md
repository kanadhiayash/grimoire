# Security, Red Team, and Abuse Resistance

## Purpose

Build security and abuse resistance into product, design, architecture, implementation, release, and operations.

## Expected outcome

Assets, actors, trust boundaries, threats, abuse cases, controls, residual risk, detection, response, and verification are explicit.

## Applicability

All products. Depth increases with data sensitivity, external exposure, user harm, automation, and regulatory impact.

## Non-applicability

No product is exempt from basic threat and secret handling.

## Required inputs

Architecture, data flows, identities, permissions, assets, vendors, AI tools, user groups, and operational environment.

## Unknowns to resolve

Threat actors, administrative access, vendor controls, incident ownership, key rotation, and recovery.

## Required actions

Threat model, abuse-case review, least privilege, secure defaults, dependency and supply-chain review, secret management, input and output controls, logging, detection, incident response, and remediation verification.

## Required decisions

Authentication, authorization, session, key management, encryption, trust boundaries, isolation, administrative access, logging, disclosure, and red-team scope.

## Required details

Asset, actor, capability, entry point, precondition, attack path, impact, control, detection, response, owner, and residual risk.

## Expected documents and artifacts

Threat model, abuse-case register, access matrix, security test plan, dependency or SBOM record, incident plan, vulnerability disclosure process, and release security evidence.

## Document structure

Each finding records evidence, source to impact path, exploit preconditions, affected assets and users, severity, likelihood, remediation, verification, owner, and status.

## Acceptance criteria

- Trust boundaries and privileged actions are documented.
- Sensitive operations enforce authorization server-side.
- Secrets are absent from code, logs, examples, and public artifacts.
- Critical findings block release.
- Remediation is verified independently from implementation claims.

## Verification method

Static and dynamic tests, dependency review, authorization tests, adversarial scenarios, manual review, and incident exercises according to risk.

## Evidence required

Threat model, test output, findings, remediation commits, verification results, and residual-risk approval.

## Failure conditions

Security by UI only, hidden critical finding, disabled gate, unverified remediation, unrestricted agent tools, or production secrets in test or documentation.

## Risks and abuse cases

Account takeover, privilege escalation, injection, data exfiltration, denial of service, fraud, stalking, harassment, model manipulation, prompt injection, and excessive agency.

## Guards and limits

Do not perform destructive or live external testing without explicit scope and approval. Do not publish exploitable detail without a disclosure decision.

## Exceptions

Critical security exceptions require named risk acceptance, compensating control, deadline, and authorized approver.

## Cost considerations

Budget security review and monitoring proportional to exposure and harm. Cost does not justify bypassing critical controls.

## Dependencies

Architecture, data, AI, cloud, legal, incident, and release standards.

## Related standards

Global Legal Control Plane and Zeref Integration.

## Source provenance

Use reviewed NIST, OWASP, CISA, MITRE, platform, and regulator sources.

## Owner and review cycle

Security owner. Review on architecture, permission, data, vendor, AI, or threat changes.

## Zeref execution behavior

Use least privilege, bounded test scope, evidence-backed findings, and independent validation for critical findings. Stop before live exploitation without approval.

## Examples

An AI agent cannot call payment or deletion tools without scoped authorization and confirmation.

## Anti-patterns

Calling a dependency scan a complete security review.
