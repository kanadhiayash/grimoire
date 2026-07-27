# Source and Evidence Manifest

## 1. Repository evidence

| ID | Evidence | Value |
|---|---|---|
| EVD-REPO-001 | Repository | `kanadhiayash/grimoire` |
| EVD-REPO-002 | Merge commit | `72015acac8a57146ad8b00a6c7b4725b8d86a9c8` |
| EVD-REPO-003 | Audited release | `0.5.0` |
| EVD-REPO-004 | Built-in tests | 60 passing in sandbox |
| EVD-REPO-005 | Top-level check | PASS in sandbox |
| EVD-REPO-006 | Audit date | July 27, 2026 |

## 2. Sandbox evidence

- baseline check;
- performance run;
- harness lifecycle;
- browser pack compile and verify;
- manifest fuzz;
- false status;
- prompt injection;
- symlink overwrite;
- dirty output;
- policy schema validation;
- normative self-compliance;
- line coverage snapshot.

Exact results are in `03_SANDBOX_TEST_EVIDENCE.md`.

## 3. Authoritative external sources

Use these as versioned source records. Verify again during implementation because standards change.

### NIST SSDF 1.1

Title:

`Secure Software Development Framework Version 1.1, NIST SP 800-218`

Official URL:

```text
https://csrc.nist.gov/pubs/sp/800/218/final
```

Status:

- 1.1 final;
- 1.2 draft exists as of the audit date.

### OWASP ASVS 5.0.0

Official URL:

```text
https://owasp.org/www-project-application-security-verification-standard/
```

Use versioned IDs such as `v5.0.0-1.2.5`.

### OWASP AISVS 1.0

Official URL:

```text
https://owasp.org/www-project-artificial-intelligence-security-verification-standard-aisvs-docs/
```

Status:

- version 1.0 released June 24, 2026.

### WCAG 2.2

Official URL:

```text
https://www.w3.org/TR/WCAG22/
```

Status:

- W3C Recommendation;
- success criteria are testable and technology-independent;
- use criterion IDs and levels.

### OWASP MASVS

Official URL:

```text
https://mas.owasp.org/MASVS/
```

Use for mobile application profiles.

### SLSA 1.2

Official URL:

```text
https://slsa.dev/spec/v1.2/
```

Status:

- approved specification;
- includes build and source tracks and provenance guidance.

### OpenSSF Scorecard

Official URL:

```text
https://github.com/ossf/scorecard
```

Boundary:

- heuristic measurement;
- not a definitive security certification;
- individual checks matter more than aggregate score.

### OWASP SAMM

Official URL:

```text
https://owaspsamm.org/model/
```

Use for organizational software-assurance maturity, not individual application control certification.

### NIST AI RMF 1.0

Official URL:

```text
https://www.nist.gov/itl/ai-risk-management-framework
```

Status:

- AI RMF 1.0 is being revised;
- freshness must be tracked.

### NIST Generative AI Profile

Official URL:

```text
https://www.nist.gov/publications/artificial-intelligence-risk-management-framework-generative-artificial-intelligence
```

Publication:

- NIST AI 600-1.

## 4. Source-handling rules

- official sources first;
- source version required;
- source classification required;
- effective date where relevant;
- review date required;
- no silent source update;
- no draft treated as final;
- no copied external standard beyond permitted licensing;
- mappings must cite versioned IDs;
- human legal review remains separate.

## 5. Audit limitations

- no fresh network clone in the original sandbox;
- no separately visible CI result on the final merge commit;
- no verified Zeref end-to-end run;
- no qualified legal review of jurisdiction mappings;
- no full Windows runtime test;
- no executable Grimoire benchmark runner in 0.5.0.
