# Zeref Runtime Integration Plan

## 1. Boundary

Grimoire defines what must be true.

Zeref decides how to execute within the approved constraints.

The project repository contains actual changes and evidence.

## 2. Grimoire output to Zeref

`ZEREF_EXECUTION_PROFILE.json` must include:

- profile schema version;
- Grimoire version;
- pack hash;
- project repository;
- project commit;
- plan ID;
- plan revision;
- approved scope;
- excluded scope;
- lifecycle stage;
- risk level;
- required controls;
- required documents;
- acceptance criteria;
- stop conditions;
- permitted tools;
- prohibited tools;
- approval-required actions;
- autonomy level;
- model-routing constraints;
- support-role maximum;
- cost ceiling;
- retry ceiling;
- memory policy;
- expected receipt schema;
- receipt expiry.

## 3. Zeref execution behavior

Zeref must:

1. verify the profile before execution;
2. confirm plan and revision;
3. confirm repository commit;
4. load only required controls;
5. select one lead and up to three support roles;
6. choose the lowest-cost capable model;
7. execute within approved scope;
8. stop on control conflict;
9. record commands and changes;
10. collect evidence;
11. require approval for external actions;
12. return a signed or integrity-protected receipt.

## 4. Zeref receipt

Required fields:

- receipt schema version;
- profile hash;
- pack hash;
- plan ID;
- revision;
- project commit before;
- project commit after;
- branch;
- roles used;
- models used when observable;
- tools used;
- commands;
- files changed;
- tests;
- evidence records;
- approvals;
- retries;
- cost;
- stop events;
- completion status;
- memory proposals;
- external actions;
- timestamp;
- integrity record.

## 5. Grimoire receipt verification

Reject when:

- profile hash mismatch;
- pack hash mismatch;
- plan mismatch;
- revision mismatch;
- base commit mismatch;
- unauthorized file scope;
- unauthorized external action;
- missing required test;
- failed release-blocking control;
- unsupported completion status;
- expired receipt;
- evidence missing;
- memory write not approved;
- cost ceiling exceeded without approval.

## 6. Memory boundary

Grimoire may propose:

- decision records;
- assumption updates;
- risk updates;
- evidence records;
- changelog entries;
- memory candidates.

Only Zeref's approved single-writer process may promote canonical Zeref memory.

## 7. Execution modes

### Advisory

- no code changes;
- recommendations and plans only.

### Standard

- bounded implementation;
- normal verification;
- approval for external actions.

### Strict

- high-risk controls;
- independent quality gate;
- enhanced evidence;
- no unresolved unknowns.

### Off

- no Zeref execution;
- Grimoire pack remains usable by humans and other agents.

## 8. End-to-end benchmark

Pilot requirements:

- one real project;
- one approved plan;
- one clean branch;
- generated Grimoire pack;
- actual Zeref execution;
- code changes;
- tests;
- evidence;
- receipt;
- Grimoire verification;
- human review;
- rollback test.

Success:

- all hashes and revisions match;
- no out-of-scope changes;
- all required evidence present;
- final status agrees with actual control evidence;
- independent rerun reaches the same verdict.
