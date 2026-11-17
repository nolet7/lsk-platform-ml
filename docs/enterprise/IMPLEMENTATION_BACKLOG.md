# CTO-sponsored implementation backlog

**States:** DONE = code/document present, NOT deployment validation; PARTIAL = skeleton/design; TODO = unimplemented. Priorities P0 block launch, P1 before scaling, P2 optimization. Each task needs a named owner, pull request, test output and acceptance link.

| ID | Priority | Phase | Deliverable | Current | Exit test / acceptance |
|---|---|---|---|---|---|
| DISC-01 | P0 | Discovery | AS-IS workflow, personas, 2 source API contracts, data classifications | PARTIAL | Quality, platform, security approve requirement baseline |
| DISC-02 | P0 | Discovery | C4, SLO/SLI, ADR, RACI and threat model | PARTIAL | Architecture and InfoSec decisions recorded |
| POC-01 | P0 | POC | Synthetic MRO/QMS simulator, prediction/review API | DONE | Contract, authorization, duplicate review, safe-failure tests green |
| POC-02 | P0 | POC | Deterministic dataset/training and SDK | DONE | Two reproducible builds have same dataset and model digest |
| POC-03 | P0 | POC | Runnable CI evidence, security checks and POC walkthrough | PARTIAL | CI, synthetic workflow demo, reviewer gate |
| PIL-01 | P0 | Pilot | Enforced OIDC/JWT, tenant isolation and audit persistence | TODO | Unauthorized and cross-tenant integration tests fail closed |
| PIL-02 | P0 | Pilot | Deployed MLflow/Postgres/S3 and model governance | TODO | Evaluation + registry approval blocks unapproved promotion |
| PIL-03 | P0 | Pilot | KubeRay or Kubernetes Job controller, resource quotas | PARTIAL | Real job lifecycle + budget + namespace isolation |
| PIL-04 | P0 | Pilot | Integrated staging env, data lineage, review evidence | PARTIAL | End-to-end stage run with 2 authorized teams |
| PIL-05 | P1 | Pilot | Dashboards, alerts, trace correlation, load baselines | PARTIAL | Alert firing + operator acknowledgment recorded |
| PRD-01 | P0 | Production | Multi-account Terraform EKS/VPC/IAM, KMS/S3/RDS/ECR, private network | TODO | Terraform plan+policy review and live infrastructure verification |
| PRD-02 | P0 | Production | On-prem hybrid connectivity, residency-approved data flow | TODO | Routing, RBAC, encryption and partition failure tests |
| PRD-03 | P0 | Production | Immutable OCI/model artifacts, release approvals, GitOps canary | PARTIAL | Signed digest + rollback exercise and CAB |
| PRD-04 | P0 | Production | Threat testing, secret rotation and supply chain verification | TODO | Security signoff, zero critical blockers |
| PRD-05 | P0 | Production | SLO burn-rate, capacity/GPU tests, backup restoration, DR | PARTIAL | Actual measured SLO, RPO/RTO, cost and 3-AZ scenario |
| OPS-01 | P0 | Handover | Runbooks, service catalog, incident escalation and paging | PARTIAL | SRE dry run, named owner, rota and 7/30/90-day reviews |
| OPS-02 | P0 | Handover | Formal quality/security/CTO/SRE signoffs and adoption handoff | TODO | Gate manifest references real externally verified approvals |
| OPT-01 | P2 | Optimize | GPU throughput and training cost optimization | TODO | Baseline and before/after benchmarking with hardware details |

## Dependency chain
`DISC-01 → DISC-02 → POC-03 → PIL-01/02/03/04 → PIL-05 → PRD-01/02/03/04/05 → OPS-01/02`. Never treat a design or static manifest as proof of installation.

## Definition of done
An owner, reproducible steps, passing contract/security tests, a clean source-controlled change, traceable immutable artifact, rollback plan, monitoring and updated documentation; the phase approvers accept evidence in an audited external system. Record real results; do not manufacture signoff evidence.
