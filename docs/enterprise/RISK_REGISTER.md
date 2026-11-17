# Enterprise delivery risk and architecture decisions

| Risk ID | Severity | Failure mode | Mitigation | Accountable role | Status |
|---|---|---|---|---|---|
| R-01 | Critical | AI prediction accidentally approves a flight-critical component | QMS human-only disposition, distinct auth scope, negative test and quality approval | Quality Lead | OPEN |
| R-02 | Critical | Proprietary/export-controlled inspection data in wrong region | Synthetic-only baseline, legal classification, residency-admitted scheduling and deny-by-default egress | Legal/Security | OPEN |
| R-03 | High | API demo key used in production | Mandatory OIDC/JWT and scoped project authorization; block promotion until removed | Security | OPEN |
| R-04 | High | Cross-team inference or training data leak | Project-scoped access, network policies, external negative cross-tenant tests | Security/Platform | OPEN |
| R-05 | High | Drifted model introduced without review | Evaluation threshold, approval workflow, signed immutable artifacts, rollback | ML/Quality | OPEN |
| R-06 | High | Unrestorable S3/RDS backups | Encrypted PITR, isolated restore and digest checks; record achieved RPO/RTO | SRE/Data | OPEN |
| R-07 | High | GPU bill explosion or resource exhaustion | Per-team quotas, admission budgets, queue metrics and load tests | FinOps/Platform | OPEN |
| R-08 | High | Blueprint mistaken for deployed system | Explicit status banner, evidence gate and truthful README/traceability | Delivery Lead | MITIGATED IN DOCUMENTATION |
| R-09 | High | K8s workload identity or supply-chain compromise | Signed artifacts, pod identity, image policies, least privilege, periodic threat tests | Security | OPEN |

## ADRs to secure before production
1. Approved AWS account/region and on-prem data residency design.
2. OIDC issuer and principal propagation to API, jobs and audit.
3. MLflow registry ownership and multi-person promotion policy.
4. Ray/GPU decision backed by measured workload benefit.
5. SLO/RTO/RPO and service continuity when inference is down.
6. Controlled change management for model versions and quality authorization.

Do not mark a risk closed based on the existence of a Markdown file.
