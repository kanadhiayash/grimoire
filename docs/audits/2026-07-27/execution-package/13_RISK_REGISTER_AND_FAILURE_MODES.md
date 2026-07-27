# Risk Register and Failure Modes

## Risk scale

- Probability: Low, Medium, High
- Impact: Low, Medium, High, Critical
- Priority: P0 through P3

## Register

| ID | Risk | Probability | Impact | Priority | Trigger | Mitigation |
|---|---|---|---|---|---|---|
| RSK-001 | False project `PASS` | High | Critical | P0 | Assurance ignores evidence | Multidimensional status and hard gates |
| RSK-002 | Manifest crash | High | High | P0 | Wrong nested type | Strict schema and 10,000-case fuzz |
| RSK-003 | Prompt injection | High | High | P0 | Project text enters AI context | Untrusted-data renderer |
| RSK-004 | Filesystem overwrite | Medium | Critical | P0 | Symlinked output | Safe atomic filesystem layer |
| RSK-005 | Standards not actually selected | High | Critical | P0 | Generic pack output | Registry and applicability engine |
| RSK-006 | Source appears valid but is fake | Medium | High | P1 | Format-only commit validation | Connected source verification |
| RSK-007 | Stale legal source | High | High | P1 | Review date expires | Freshness and supersession monitor |
| RSK-008 | Self-inconsistent standards | High | High | P1 | Legacy prose compiles | Normative classification gate |
| RSK-009 | Benchmark gaming | Medium | Critical | P0 | Fixture changed to pass code | Benchmark governance and independent review |
| RSK-010 | Aggregate score hides failure | Medium | Critical | P0 | Weighted score passes | Non-bypassable hard gates |
| RSK-011 | Zeref receipt spoofing | Medium | Critical | P1 | Unbound receipt | Hash, plan, commit, approval binding |
| RSK-012 | Overgrown context pack | Medium | Medium | P2 | Too many controls | Token budget and selection precision |
| RSK-013 | Standards sprawl | High | Medium | P2 | Duplicate controls | Registry ownership and deduplication |
| RSK-014 | Dependency drift | Medium | High | P1 | CI tools update | Pinning, lock, source review |
| RSK-015 | Legal automation overreach | Medium | Critical | P0 | Compliance claim | Forbidden status and counsel gate |
| RSK-016 | Accessibility false pass | Medium | High | P1 | Automated tests only | Manual evidence requirement |
| RSK-017 | Compatibility break | Medium | High | P1 | Pack or CLI format changes | Migration fixtures and version negotiation |
| RSK-018 | Performance collapse at scale | Medium | Medium | P2 | Registry grows | Scale benchmarks and indexes |
| RSK-019 | Flaky benchmark | Medium | Medium | P2 | Environment variance | Repeated runs and variance thresholds |
| RSK-020 | Private data in evidence | Medium | High | P1 | Logs capture secrets | Redaction, sensitivity classes, retention |
| RSK-021 | Council ceremony without independent analysis | High | Medium | P2 | Role names only | Role-specific outputs and dissent record |
| RSK-022 | Giant PR becomes unreviewable | High | High | P1 | Multi-domain rewrite | Phased PR program |
| RSK-023 | Tests optimized for coverage only | Medium | High | P1 | High line coverage, weak assertions | Mutation and adversarial testing |
| RSK-024 | Source licenses violated | Low | High | P1 | Full external standards copied | Metadata, links, permitted mappings, license review |

## P0 failure modes

### False assurance

System reports a positive status unsupported by evidence.

Required response:

- block release;
- preserve failing fixture;
- fix status engine;
- add hard-gate test;
- audit historical packs.

### Unsafe filesystem behavior

Compiler writes outside intended output.

Required response:

- treat as security incident;
- disable affected release;
- add boundary tests;
- review all filesystem operations.

### Benchmark manipulation

Expected outputs changed to hide a regression.

Required response:

- revert fixture;
- require independent approval;
- preserve old and proposed expected behavior;
- record ADR if requirement truly changed.

### Legal certification

Automated output says a product is compliant.

Required response:

- remove claim;
- mark affected releases;
- replace with applicability and review status;
- require counsel review.

## Residual-risk rule

No P0 residual risk may remain open for Grimoire 1.0.
