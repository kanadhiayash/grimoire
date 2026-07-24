# Cloud, Reliability, Operations, and Cost

## Purpose

Design services that are operable, recoverable, observable, capacity-aware, and financially bounded.

## Expected outcome

Availability, latency, capacity, failure, recovery, observability, environments, infrastructure, vendors, and unit cost have owners and evidence.

## Applicability

Hosted applications, cloud services, third-party platforms, AI APIs, and production infrastructure.

## Non-applicability

Local-only prototypes still document external dependencies and a path to production if production claims are made.

## Required inputs

User-critical journeys, traffic and data assumptions, availability and recovery needs, regions, vendors, security, and budget.

## Unknowns to resolve

Peak demand, failure tolerance, recovery objectives, data residency, vendor limits, support model, and cost ownership.

## Required actions

Define environments, infrastructure as code where appropriate, identity, network, secrets, observability, SLOs, error budgets, capacity, backup, recovery, incident response, vendor exit, and cost controls.

## Required decisions

Region, service, deployment, scaling, redundancy, caching, queueing, monitoring, alerting, backup, recovery, and failover.

## Required details

Service owner, dependency, SLI, SLO, limit, failure mode, alert, runbook, recovery, cost driver, unit metric, and budget.

## Expected documents and artifacts

Environment map, architecture, SLOs, dependency register, capacity model, cost model, runbook, incident plan, backup and recovery evidence, and vendor exit plan.

## Document structure

Each service records purpose, owner, region, data, dependencies, limits, SLO, alerts, failures, recovery, security, and cost.

## Acceptance criteria

- Critical journeys have measurable reliability targets.
- Alerts map to actionable runbooks.
- Recovery is tested where required.
- Resource and API use are bounded.
- Cost has an owner and unit metric.
- Vendor failure and exit paths are documented.

## Verification method

Load and failure tests, restore exercises, alert tests, deployment and rollback checks, cost simulation, and operational review.

## Evidence required

Dashboards, test output, runbooks, cost reports, incident exercises, and approvals.

## Failure conditions

Unbounded retries or model loops, no rollback, alerts without action, unknown backup restore, hidden vendor minimums, or public reliability claims without evidence.

## Risks and abuse cases

Cascading failure, regional outage, quota exhaustion, bill shock, credential leakage, noisy alerts, and vendor termination.

## Guards and limits

Do not add multi-region, microservices, queues, or premium managed services without a requirement and cost analysis. Do not omit resilience for critical operations solely to minimize initial cost.

## Exceptions

Record reduced target, user impact, monitoring, owner, approval, and expiry.

## Cost considerations

Track compute, storage, requests, transfer, observability, backups, support, AI tokens, vendor fees, and human operations.

## Dependencies

Architecture, backend, security, data, legal, AI, release, and incident standards.

## Related standards

Minimum Correct Change and AI Agent Product Engineering.

## Source provenance

Use official provider architecture frameworks and FinOps guidance pinned in the source registry.

## Owner and review cycle

Platform and service owners. Review on traffic, vendor, region, architecture, or budget changes.

## Zeref execution behavior

Route cost-sensitive changes through bounded estimates, prefer the lowest-cost capable service, and stop unbounded loops or external resource creation without approval.

## Examples

A model feature has per-action token ceilings, caching, fallback, anomaly alerts, and a disable switch.

## Anti-patterns

Calling a free tier a production cost model.
