# Production target architecture — gated, not deployed

This branch inherits `poc` and `pilot`. Production **is not complete** because live corporate infrastructure, approved images, identity, real MLflow/Argo integration, security signoff and operational testing are not available in this public portfolio.

## Deployment model
- AWS organization: distinct accounts for sandbox, staging, production, security/logging.
- Private EKS 3-AZ compute, system/CPU/GPU pools isolated using nodes, taints, quotas.
- S3 versioned/KMS-encrypted dataset and model artifacts, RDS PostgreSQL Multi-AZ, ECR signed images.
- Workload identity, scoped IAM, private endpoints, zero public training nodes, central OIDC.
- On-prem restricted Kubernetes clusters for residency-sensitive data; no default transfer to AWS.
- GitOps for platform/workloads; model release via signed artifact digest, evaluation evidence and two-person manual authorization.
- OpenTelemetry/Prometheus/Grafana plus event logs with project labels and privacy filters.
- Canary metrics/rollback, multi-AZ, backup/restore, DR, budget caps, documented on-call.

## Promotion path
`feature → POC → pilot stage → production`, with CI checks, approval evidence and immutable image references. Environments must be in **distinct accounts**, not simply Kubernetes namespaces. Registry approval must be distinct from model evaluation. Manual QMS decisions remain authoritative.

## Required external prerequisites
Account landing zone, corporate DNS/PKI, AWS organization guardrails, GitHub environments/reviewers, artifact signing keys, approved ECR image, MLflow service, Argo CD, Kubernetes, OIDC, S3, IAM, observability and validated secrets. Never apply reference configs verbatim into a corporate account.

## Documents
- `production/docs/DEPLOYMENT_PLAN.md`
- `production/docs/THREAT_MODEL.md`
- `production/docs/RUNBOOK.md`
- `production/docs/HANDOVER.md`
- `production/docs/RELEASE_AND_DR.md`
- `production/k8s/` example protected runtime manifests
- `production/gitops/` example Argo CD app
- `production/terraform/` baseline encrypted versioned artifact bucket sample (not full EKS)
