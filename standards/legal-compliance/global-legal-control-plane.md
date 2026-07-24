# Global Legal and Compliance Control Plane

## Purpose

Identify legal and regulatory issues, route authoritative sources, compile applicable design and engineering controls, and prepare evidence and escalation without making false global-compliance claims.

## Expected outcome

The project knows which laws, regulations, regulator guidance, consensus standards, industry frameworks, proposals, and trends may apply, which facts remain unknown, what controls and documents are required, and where qualified legal review is mandatory.

## Authority classes

`BINDING_LAW`, `BINDING_REGULATION`, `COURT_OR_ENFORCEMENT_DECISION`, `REGULATOR_GUIDANCE`, `CONSENSUS_STANDARD`, `CERTIFICATION_SCHEME`, `INDUSTRY_FRAMEWORK`, `BEST_PRACTICE`, `EMERGING_TREND`, `PROPOSAL`, `DRAFT`, `SUPERSEDED`.

Never silently promote guidance, a trend, or a proposal to binding law.

## Applicability inputs

- Organization establishment and operating locations
- Markets intentionally offered or targeted
- User and data-subject locations
- Product and industry type
- Public or private sector role
- User age and vulnerable-user context
- Personal, sensitive, biometric, health, financial, location, employment, education, or communications data
- Payments, subscriptions, advertising, tracking, marketplaces, user-generated content, connected products, and AI
- Vendors, subprocessors, storage, transfers, and cloud regions

## Allowed applicability statuses

`APPLICABLE`, `POTENTIALLY_APPLICABLE`, `NOT_APPLICABLE`, `INSUFFICIENT_FACTS`, `COUNSEL_REVIEW_REQUIRED`, `SOURCE_STALE`, `SOURCE_CONFLICT`.

Automated output must never use `COMPLIANT` as a final legal status.

## Required controls

- Privacy and data protection by design and default
- Data minimization, retention, deletion, access, and security
- Consent and choice where required
- Accessible and non-manipulative interaction
- Children and vulnerable-user safeguards
- Consumer, subscription, cancellation, and refund transparency
- AI risk, disclosure, human oversight, evaluation, and incident controls
- Vendor, transfer, open-source, intellectual-property, and recordkeeping controls
- Incident, complaint, rights-request, and regulatory-change processes

## Required documents where triggered

Privacy notice, cookie notice, terms, accessibility statement, AI disclosure, data inventory, processing record, retention schedule, privacy or data-protection impact assessment, AI impact assessment, threat model, vendor assessment, transfer assessment, accessibility conformance record, incident plan, business continuity plan, open-source notices, software bill of materials, and release attestation.

## Guards

- Use official sources as canonical authority.
- Preserve original-language authority and label translations.
- Store publication, effective, retrieval, review, and supersession dates.
- Treat legal templates as drafts requiring jurisdiction-specific review.
- Escalate conflicts, high-risk processing, consequential automation, children, biometrics, health, finance, employment, public-sector, or uncertain territorial scope.
