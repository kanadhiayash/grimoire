# Acceptance Criteria and Release Gates

## 1. PR gate

Every implementation PR requires:

- approved issue or plan;
- one mission;
- tests defined first;
- red evidence;
- green focused tests;
- full Grimoire check;
- security review where relevant;
- compatibility statement;
- benchmark effect;
- no unresolved review thread;
- exact-head CI;
- explicit merge approval.

## 2. Compiler gate

- strict manifest validation;
- zero uncaught exceptions;
- no symlink following;
- no path escape;
- atomic output;
- deterministic mode;
- actual standards selected;
- selection reasons;
- exclusions;
- conflicts;
- source manifest;
- pack verifier pass.

## 3. Status gate

A project readiness `PASS` requires:

- valid pack;
- no critical unknown;
- no unresolved conflict;
- every release-blocking control verified or approved waiver;
- current evidence;
- plan and commit binding;
- valid approvals;
- legal review status acceptable for the declared release;
- Zeref receipt valid when Zeref executed.

## 4. Normative standards gate

Before a standard becomes enforceable:

- valid standard schema;
- unique ID;
- version;
- owner;
- source provenance;
- applicability;
- acceptance;
- verification;
- evidence;
- failure behavior;
- exception process;
- tests;
- review date.

## 5. Security gate

- threat model current;
- hostile-input tests;
- filesystem boundary tests;
- no critical or high findings;
- pinned CI actions;
- schema validation;
- secret scan;
- static analysis;
- SBOM;
- provenance;
- release evidence.

## 6. Accessibility gate

Where applicable:

- WCAG 2.2 criterion mapping;
- automated tests;
- manual checks;
- assistive-technology evidence;
- unresolved barriers documented;
- no false conformance claim.

## 7. Legal and privacy gate

- project markets and processing facts declared;
- official sources;
- source freshness;
- applicability status;
- missing facts;
- required documents;
- counsel review where triggered;
- no automated final compliance certification.

## 8. AI gate

- AI capability declared;
- risk assessment;
- evaluation plan;
- AISVS mapping where applicable;
- prompt and context injection tests;
- output validation;
- human oversight;
- model and tool permissions;
- monitoring;
- retirement or fallback.

## 9. Zeref gate

- profile valid;
- plan bound;
- commit bound;
- approvals valid;
- receipt valid;
- evidence complete;
- no unauthorized action;
- memory boundary respected;
- cost ceiling respected.

## 10. Benchmark gate

- all hard gates pass;
- no regression above threshold;
- raw evidence retained;
- exact commit recorded;
- environment recorded;
- repeated runs where needed;
- independent reviewer confirms final score.

## 11. Release candidate gate

- clean clone or equivalent clean checkout;
- Python 3.11, 3.12, and 3.13;
- supported operating systems;
- all tests;
- full fuzz;
- all gold scenarios;
- security suite;
- performance suite;
- compatibility suite;
- documentation;
- migration;
- rollback;
- signed release evidence.

## 12. Grimoire 1.0 gate

Required:

- weighted score at least 9.7;
- every domain at least 9.5;
- all hard gates pass;
- no critical or high finding;
- zero false assurance;
- 100% enforced-standard self-compliance;
- Zeref pilot verified;
- explicit human approval.

Final release status before approval:

```text
NOT_VERIFIED
```

Only fresh release-candidate evidence may change that status.
