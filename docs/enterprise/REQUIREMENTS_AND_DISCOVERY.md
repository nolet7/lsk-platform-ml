# Discovery and requirements baseline — fictional aerospace customer

## CTO directive and scope
Build an internal ML infrastructure product to help Quality/Repair engineers inspect turbine components, without transferring part acceptance authority to an ML model. Integrate into existing ERP/MRO and QMS workflows instead of replacing them. Begin with synthetic data and secure approval from legal/export-control, quality and security before using actual customer records.

## Personas / customer discovery plan
| Persona | What they need | How to validate |
|---|---|---|
| Inspector / Quality lead | Prediction with explanation and linked inspection; manual final decision | 5 task walkthroughs; reject unauthorized disposition |
| ML engineer | Submit a reproducible training run without authoring K8s YAML | SDK task demo, artifact hash/lineage test |
| Repair engineer | Trace an inspection decision to model/version and repair order | Audit log and correlation ID drill |
| Security / legal | Isolation, data geography, least privilege, no export-controlled leakage | Threat model, access tests, data-handling approval |
| Platform SRE | Safe deployments, capacity, observable failures, rollback, backup | Runbooks, telemetry, failover/restore drill |
| CTO / product owner | Adoption, measured quality and support costs | Monthly scorecard and exit-gate approval |

The people above are **roles**, not interviewed individuals; no real discovery meetings have been recorded.

## Functional requirements (IDs support acceptance traceability)
- **FR-01** Read-only versioned connector to repair orders and inspection records; isolate upstream outages.
- **FR-02** Versioned dataset manifests: schema, permitted source, tenant, digest, split seed and retention.
- **FR-03** Authenticated project-scoped API and typed Python SDK for job submission, status and lineage.
- **FR-04** Repeatable CPU jobs first; Ray/GPU opt-in only with benchmark and quota evidence.
- **FR-05** MLflow tracking, private registry, evaluation policy and dual human approval of production promotion.
- **FR-06** Online/batch prediction always non-authoritative; disposition requires qualified human review.
- **FR-07** Immutable audit events linking inspection → dataset → training → model → inference → reviewer.
- **FR-08** Dashboards, alerts, cost attribution, runbooks, tickets, on-call and handover evidence.

## Nonfunctional candidate targets — not measured
- **NFR-01:** Availability 99.9% rolling 30 days for platform API (business/SRE must approve exclusions).
- **NFR-02:** p95 inference below 400 ms for agreed synthetic request sizes and provisioned hardware.
- **NFR-03:** RPO at most 1h and RTO at most 4h, contingent on restore exercises and approval.
- **NFR-04:** Encrypted storage and transport, least privilege, private nodes, workload identity and no secrets in Git.
- **NFR-05:** Multi-AZ fault resilience and business-approved regional/data-residency policies.
- **NFR-06:** Model approval auditability, zero unapproved production promotions and safe failure to manual review.

## Open discovery decisions
- Determine actual source ERPs/QMS API contracts and schemas; no real ERP integration exists.
- Identify export-control and contractual restrictions before any real-data onboarding.
- Agree tenant model, retention/audit obligations, SLO measurement windows, peak concurrency and budgets.
- Choose model registries, external identity provider, incident ticketing, recovery region and on-prem connectivity with actual stakeholders.
- Record all approvals in an external system; this repository supplies templates only.
