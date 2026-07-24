# Standards Orchestrator Benchmarks

## Purpose

Measure correctness, control selection, evidence quality, cost, and execution efficiency. Do not benchmark by repository size or rule count.

## Required scenario families

- Consumer mobile application
- Fintech application
- Health or wellness application with and without regulated health scope
- Child-directed or age-ambiguous service
- Public-sector accessible service
- Marketplace or social platform
- AI assistant
- Agentic automation
- Connected product
- Multi-jurisdiction SaaS

## Required measures

- Critical-control recall
- False applicability and false non-applicability
- Missing-fact detection
- Correct legal escalation
- False compliance claims
- Required-document selection
- Gate accuracy
- Security and accessibility findings
- First-pass acceptance rate
- Regression count
- Files and lines changed
- Dependencies added
- Tokens, API calls, model cost, execution time, and human review time when measured

## Hard safety targets

- False automated legal-compliance claims: 0
- Critical safety and legal escalation recall: 100%
- Completion without evidence: 0
- Full-corpus loading for simple tasks: 0
- Personal identity leakage into neutral instructions: 0
