# Production architecture and deployment sequence
1. Discovery: approve business workflows, bounded contexts, RACI, export-control and data map, quality authority.
2. Landing zone: organization accounts, VPC/subnets, transit/on-prem connectivity, KMS, IAM/SSO, audit retention.
3. Data foundation: synthetic-to-authorized migration, schema/lineage checks, data catalog, encrypted S3, backup and immutability policies.
4. EKS: cluster private endpoint, system and workload node groups in 3 AZ, GPU scheduling via operator/device plugin, ECR, ingress, networking, quotas.
5. Control plane: OIDC gateway, project-scoped API, per-team identities, workflow admission, MLflow registry/artifact backend and cost attribution.
6. Data plane: training Jobs/Ray where benchmark supports it; images pinned and signed; dedicated GPU storage/networking paths.
7. Release: stage canary, contract and model evaluation, human model approval, artifact provenance, GitOps change review, progressive rollout.
8. Operations: OTel collectors, Prometheus/Grafana dashboards, audit routing, alerts, backup and restore, SLO, autoscaler and GPU budgets.
9. DR and security: penetration tests, token rotation, IAM least-privilege checks, restore point, AZ injection, rollback and compromised model response.
10. Handover: team ownership, escalation, runbook evidence, capacity forecast, monthly business/ML KPI review.

## Reference target nonfunctional constraints
Platform API 99.9% per rolling 30d; p95 inference <400ms for agreed payload+hardware; RTO <=4h and RPO <=1h pending signoff. No model may release a physical component without QMS human signoff. Availability alone does not establish aviation compliance.

## Rollout criteria
- No shipping with placeholder OCI image, raw demo credentials or unimplemented OIDC.
- All database/object-store backups restored in a separate environment at least once.
- Security architecture approval plus policy-as-code and signed artifacts.
- Load tests and cost benchmark matched to production profile.
- Synthetic and later authorized real data are kept segregated.
