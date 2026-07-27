# Test Matrix and Fixture Catalog

## 1. Test taxonomy

| Layer | Purpose |
|---|---|
| Unit | Prove one pure behavior |
| Schema | Prove contracts accept and reject exact shapes |
| Property | Prove invariants across generated inputs |
| Fuzz | Find crashes and unsafe behavior |
| Mutation | Prove tests detect incorrect logic |
| Integration | Prove modules work together |
| Golden | Prove stable expected pack output |
| Metamorphic | Prove equivalent inputs produce equivalent decisions |
| Security | Prove trust boundaries fail closed |
| Performance | Prove latency, memory, and size targets |
| Compatibility | Prove migrations and deprecated inputs |
| End to end | Prove Grimoire, Zeref, and project evidence round trip |

## 2. Manifest fixtures

### Valid

- minimum valid;
- full consumer mobile;
- B2B SaaS;
- fintech;
- healthcare;
- child-directed;
- public sector;
- AI assistant;
- agentic automation;
- connected product;
- multi-market;
- no-AI product;
- critical-risk product.

### Invalid types

- strings instead of arrays;
- arrays instead of objects;
- booleans as strings;
- integers as strings;
- null required objects;
- null optional arrays;
- nested unknown keys;
- empty required arrays;
- unsupported enums;
- unsupported schema versions.

### Hostile text

- prompt injection;
- Markdown headings;
- HTML;
- Unicode bidi controls;
- null bytes;
- terminal escape codes;
- very long strings;
- path payloads;
- URL payloads.

## 3. Status fixtures

- no evidence;
- partial evidence;
- expired evidence;
- invalid evidence;
- waived control;
- failed critical control;
- unresolved unknown;
- unresolved conflict;
- counsel required;
- pack generation failed;
- Zeref receipt missing;
- Zeref receipt valid;
- release evidence complete.

Expected rule:

No fixture with a missing release-blocking evidence item may produce release assurance `PASS`.

## 4. Applicability fixtures

For every standard:

- clearly applicable;
- clearly not applicable;
- insufficient facts;
- conflicting facts;
- exception active;
- exception expired;
- source stale;
- source superseded.

## 5. Filesystem security fixtures

- output path is symlink;
- child file is symlink;
- parent component is symlink;
- path traversal;
- read-only directory;
- dirty directory;
- unexpected file;
- interrupted write;
- same target compiled concurrently;
- temporary directory collision;
- hard link where supported;
- zip slip if pack import is added.

## 6. Source verification fixtures

- valid local commit;
- nonexistent 40-character commit;
- valid commit in wrong repository;
- moved tag;
- future timestamp;
- stale source;
- superseded source;
- source hash mismatch;
- offline mode;
- connected mode timeout;
- source URL redirect;
- revoked or removed source.

## 7. Standard registry fixtures

- duplicate ID;
- duplicate version;
- missing source;
- missing applicability;
- invalid predicate;
- circular dependency;
- superseded standard selected;
- draft standard selected;
- non-normative guidance selected;
- unresolved crosswalk;
- conflicting control requirement levels.

## 8. Predicate engine properties

- deterministic;
- no side effects;
- no code execution;
- commutative operations behave correctly;
- `all` and `any` identity rules;
- missing fields produce explicit uncertainty;
- type mismatch never crashes;
- trace includes every evaluated input;
- normalized equivalent values match.

## 9. Context-rendering fixtures

- manifest field says to ignore instructions;
- manifest field includes fake system prompt;
- manifest field includes fenced code;
- manifest field includes links;
- manifest field includes headings;
- manifest field includes repeated large content.

Expected:

All are rendered as labeled untrusted data, never as governing instructions.

## 10. Pack verifier fixtures

- missing file;
- extra file;
- wrong hash;
- wrong schema;
- wrong pack version;
- mismatched plan;
- mismatched source commit;
- future generation time;
- expired evidence;
- invalid signature;
- valid offline pack;
- valid connected pack;
- valid release pack.

## 11. Zeref receipt fixtures

- correct receipt;
- mismatched plan ID;
- mismatched revision;
- mismatched pack hash;
- mismatched project commit;
- missing approval;
- unauthorized merge;
- unauthorized deploy;
- cost ceiling exceeded;
- retry ceiling exceeded;
- memory write without approval;
- browser simulation mislabeled;
- evidence paths missing;
- completion status unsupported.

## 12. Gold scenario fixtures

Each scenario folder:

```text
benchmarks/scenarios/<scenario-id>/
  manifest.json
  project-records/
  expected-controls.json
  expected-exclusions.json
  expected-conflicts.json
  expected-documents.json
  expected-status.json
  notes.md
```

## 13. Coverage targets

| Module | Line | Branch | Mutation |
|---|---:|---:|---:|
| Manifest validation | 95% | 90% | 90% |
| Predicate engine | 95% | 95% | 90% |
| Applicability engine | 95% | 90% | 90% |
| Status engine | 100% | 100% | 95% |
| Safe filesystem | 95% | 95% | 90% |
| Pack verifier | 95% | 90% | 90% |
| Zeref receipt verifier | 95% | 95% | 90% |
| CLI routing | 90% | 85% | 80% |

## 14. CI tiers

### Pull request

- focused unit and schema tests;
- fast fuzz subset;
- gold smoke scenarios;
- security boundary smoke;
- Python matrix;
- exact-head result.

### Main

- full unit and integration;
- 10,000-case fuzz;
- all gold scenarios;
- full security suite;
- compatibility suite;
- benchmark comparison.

### Scheduled

- 50,000-control performance;
- external source freshness;
- connected commit verification;
- OpenSSF and supply-chain checks;
- flaky test detection;
- historical trend report.

## 15. Evidence retention

- PR artifacts: at least 30 days;
- release evidence: permanent;
- benchmark history: permanent;
- raw security evidence: retention based on sensitivity;
- no secret-bearing logs.
