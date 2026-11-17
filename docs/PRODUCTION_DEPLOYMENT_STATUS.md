# Production deployment readiness — verified vs pending

This repository contains a reusable ML deployment control plane and a separate aerospace synthetic inference example. **It has not been deployed to an authorized AWS production account.** The source and CI pipeline are an engineering deliverable, not production acceptance evidence.

## Implemented as reviewed code
- Tenant-scoped FastAPI model registration, MLflow run/evaluation checks, independent approval, deployment revisions and rollback request.
- PostgreSQL registry/audit schema and parameterized tenant filtering.
- OIDC/JWT scope enforcement; demo key not accepted in the platform.
- Immutable ECR image digest binding, account/region allowlist, model-specific Kubernetes Deployments/Services.
- Kubernetes namespaces/serviceaccounts/RoleBindings generated for explicit bootstrap approval.
- Separate control-plane and sample inference OCI Dockerfiles, SDK and CI.
- Private 3-AZ EKS/VPC, ECR, S3 and Multi-AZ RDS Terraform configurations; migration and deploy scripts.

## Not demonstrated and release blockers
- AWS authorized account Terraform plan/apply, cluster health, ECR publication, protected GitHub OIDC runner configuration.
- Database migrations and actual least-privileged database identities.
- MLflow server deployment, authenticated run ingestion, image/run provenance verification with actual signed release pipeline.
- Verified integration with chosen OIDC provider and tenant scope issuance.
- Ongoing Kubernetes rollout reconciliation: API returns 'submitted' only; pod health/canary verification not yet integrated in platform status.
- Kubernetes security policy/network egress enforcement, external secrets rotation, image signing/attestation, supply chain scanning.
- Ray/GPU training orchestration, quotas, experiment submission API and full ML lifecycle beyond deployment.
- Load tests, HA, backups/restore, failure injection, DR, paging, SLO, model drift monitoring, audit retention, FinOps.
- Authorized data residency/security/Quality approval and formal SRE operational handover.

## Important boundaries
- ML platform deploys previously approved inference **images**; it does not dynamically execute arbitrary code from MLflow runs.
- An evaluation reference or mutable tag alone cannot grant approval.
- Aerospace inspection is synthetic. No flight-critical disposition is automated.
- `production` branch remains a baseline; new feature branch requires review and merge, CI alone is not permission to apply resources.

See `docs/ML_PLATFORM_DEPLOYMENT.md`, `docs/enterprise/PHASE_GATES.md`, `production/terraform/DEPLOY.md`.
