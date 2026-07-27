# Security, Privacy, Legal, Accessibility, and AI Plan

## 1. Purpose

These domains are not optional overlays added after implementation. They shape applicability, design, architecture, evidence, and release gates.

## 2. Security baseline

### Authoritative mappings

- NIST SSDF 1.1 for software lifecycle practices;
- OWASP ASVS 5.0.0 for web and application controls;
- OWASP MASVS for mobile applications;
- OWASP AISVS 1.0 for AI-enabled systems;
- SLSA 1.2 for supply-chain provenance;
- OpenSSF Scorecard as a heuristic repository-health input;
- OWASP SAMM for organizational maturity.

### Required control record fields

- external control ID;
- external version;
- Grimoire control ID;
- applicability;
- implementation guidance;
- verification method;
- evidence type;
- requirement level;
- source license;
- review date.

### Security release gates

- no unresolved critical or high findings;
- threat model current;
- authorization tests;
- secret scan;
- dependency and workflow review;
- artifact provenance;
- rollback;
- incident contact;
- evidence tied to release commit.

## 3. Privacy

### Required product facts

- personal data;
- sensitive categories;
- purposes;
- legal role;
- user locations;
- processing locations;
- vendor locations;
- retention;
- deletion;
- tracking;
- advertising;
- children;
- biometrics;
- health;
- finance;
- precise location;
- automated decisions.

### Required outputs where triggered

- data-flow map;
- processing inventory;
- retention schedule;
- deletion verification;
- privacy notice requirements;
- consent and preference requirements;
- rights-request flow;
- transfer questions;
- vendor and subprocessor list;
- impact assessment;
- counsel questions.

### Hard rule

Privacy status must remain `NOT_VERIFIED` until evidence proves the required controls.

## 4. Legal applicability

### Authority classes

- binding law;
- binding regulation;
- court or enforcement decision;
- regulator guidance;
- consensus standard;
- certification scheme;
- industry framework;
- best practice;
- emerging trend;
- proposal;
- draft;
- superseded.

### Allowed automated statuses

- `APPLICABLE`
- `POTENTIALLY_APPLICABLE`
- `NOT_APPLICABLE`
- `INSUFFICIENT_FACTS`
- `COUNSEL_REVIEW_REQUIRED`
- `SOURCE_STALE`
- `SOURCE_CONFLICT`

### Forbidden automated status

- `COMPLIANT`

### Required legal source record

- title;
- jurisdiction;
- authority;
- official source;
- canonical language;
- classification;
- status;
- publication date;
- effective date;
- review date;
- next review;
- territorial triggers;
- regulated roles;
- obligations;
- design controls;
- engineering controls;
- documents;
- counsel validation.

## 5. Accessibility

### Web target

WCAG 2.2 Level AA by default where applicable.

### Required control trace

- WCAG criterion ID;
- conformance level;
- design requirement;
- implementation requirement;
- automated test;
- manual test;
- assistive-technology test;
- evidence;
- exception.

### Hard rules

- automated checks alone cannot produce accessibility conformance `PASS`;
- partial-page checks cannot produce full-product conformance;
- mobile and native products require platform-specific overlays;
- unresolved critical barrier blocks release.

## 6. AI governance

### NIST AI RMF structure

Map Grimoire controls to:

- Govern;
- Map;
- Measure;
- Manage.

Record that AI RMF 1.0 is under revision and source freshness must be monitored.

### Generative AI profile

Map risks and actions from the NIST GenAI profile where generative systems are used.

### AISVS

For AI-enabled systems, include testable requirements for:

- data and model provenance;
- prompt and context injection;
- tool use;
- output handling;
- model access;
- monitoring;
- retirement;
- supply chain.

### Agent controls

- least privilege;
- explicit tools;
- bounded retries;
- approved plan;
- approval gates;
- cost ceiling;
- stop conditions;
- output validation;
- trace retention;
- memory promotion control;
- human review for consequential actions.

## 7. Dark patterns and user protection

Design controls must prevent:

- forced action;
- hidden information;
- obstruction;
- interface interference;
- preselection;
- confirmshaming;
- privacy-hostile defaults;
- difficult cancellation;
- deceptive AI identity;
- irreversible actions without confirmation.

## 8. Source freshness

Source monitor should:

- check official URL;
- detect version change;
- detect supersession;
- detect effective-date change;
- open a review candidate;
- never silently update a normative control;
- require approval and regression tests.

## 9. Counsel and specialist review

Required when:

- jurisdiction trigger is ambiguous and material;
- high-risk automated decision is involved;
- children or vulnerable users are involved;
- biometric, health, financial, or precise-location data is used;
- cross-border transfer rules are uncertain;
- sector-specific regulation may apply;
- a legal source conflicts with another obligation;
- a final external compliance claim is planned.
