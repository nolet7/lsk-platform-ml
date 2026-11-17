# LSK ML Platform — enterprise deployment execution guide

## System roles and scope

The repository delivers a **multi-tenant model lifecycle platform**, not only a
single classifier. ML engineers may submit training jobs, register model images,
request deployment and invoke approved inference versions via the SDK. ML
reviewers independently approve/revoke models. SRE/platform teams control EKS,
network access, encryption, runtime quotas, releases and on-call operations.

**Never run an AWS apply on a production account without explicit account-owner
authorization and written cost/security signoff.** This repository is synthetic
and the deployment described here has not been executed in AWS from this chat.

## 0. Agree environments and design

- Use separated AWS accounts for staging and production with private networking.
- Approve AWS region and data residency, VPC CIDR, S3 bucket names, EKS release,
  PostgreSQL engine version, budget, SNS escalation and approved access principals.
- Keep remote Terraform state in a separately owned encrypted, versioned S3
  bucket with lockfile enabled and tight IAM. Do not commit tfstate or tfvars.
- Ensure MLflow endpoint/metadata store and identity provider have appropriate
  TLS trust, tenant access checks and audit trails.
- Approve KubeRay and Kubernetes versions against the official compatibility
  documentation, plus the NVIDIA device plugin and GPU instance quota.

## 1. Provision infrastructure — privileged platform administrator

```bash
cd production/terraform
cp terraform.tfvars.example terraform.tfvars
# Replace every example value with approved account-specific settings.
terraform fmt -check
terraform init -backend-config="bucket=<approved-state-bucket>" \
  -backend-config="key=lsk-platform-ml/prod/terraform.tfstate" \
  -backend-config="region=<approved-region>" \
  -backend-config="use_lockfile=true"
terraform validate
terraform plan -var-file=terraform.tfvars -out=tfplan
# Human reviews IAM, KMS, EKS nodes, RDS, budgets and expected costs.
terraform apply tfplan
```

Infrastructure modules include VPC/3 AZs, private EKS, ECR, encrypted S3,
rotating KMS, Multi-AZ RDS, TLS enforcement, alarms, FinOps notifications and
optional GPU nodes (disabled by default). Budget alerts are not a cost cap.

## 2. Bootstrap cluster and identities — separate from application CI

- Confirm cluster-admin role access through private network.
- Install/verify CNI NetworkPolicy enforcement, metrics-server, Prometheus
  Operator, alert routing, KubeRay CRDs and approved NVIDIA GPU device plugin
  when GPU training is enabled.
- Create `ml-quality` namespace via `production/k8s/namespace.yaml`.
- Create separate read-only API and write-capable worker ServiceAccounts.
- Configure AWS Pod Identity and least-privilege tenant S3 access; bind training
  identities only to their data prefixes.
- Use an approved tenant/environment JSON map and review generated resources:

```bash
python production/scripts/render_tenant_bootstrap.py \
  --mapping configs/tenant-namespaces.example.json > /tmp/tenant-bootstrap.json
# Example config is NOT production authorization.
# Platform admin reviews namespaces, labels, quotas and RBAC, then:
kubectl apply -f /tmp/tenant-bootstrap.json
```

The generated tenant default-deny egress policy intentionally blocks all
unapproved external connections. **Before training**, deploy an additional
approved egress policy for internal DNS, MLflow and the private S3/data endpoint
paths. Do not replace it with unrestricted `0.0.0.0/0` egress. The inference
gateway has a narrowly scoped ingress allowance for model-serving pods.

## 3. Migrate PostgreSQL under privileged DB migration identity

Run these files **in numeric order** against the managed PostgreSQL database
using an identity that can apply DDL:

```text
production/db/001_init.sql
production/db/002_platform_control_plane.sql
production/db/003_reconciliation.sql
production/db/004_training_jobs.sql
production/db/005_inference_audit.sql
production/db/006_model_revocation.sql
```

Use a separate application DB identity with scoped SELECT/INSERT/UPDATE grants,
no schema DDL, no DELETE on audit tables, and certificate-validated TLS.
Verify persistence through `tests/integration/test_postgres_registry.py` in an
isolated test database. RDS encryption/PITR and restore are not complete until
a recorded restore drill succeeds.

## 4. Configure protected GitHub production environment

Require human reviewers and repository/ref-scoped OIDC trust policies. Supply
environment variables:

```text
AWS_ACCOUNT_ID, AWS_REGION, AWS_BUILD_ROLE_ARN, AWS_DEPLOY_ROLE_ARN,
EKS_CLUSTER_NAME, ML_PLATFORM_ECR_REPOSITORY,
ML_PLATFORM_WORKER_ECR_REPOSITORY, TENANT_NAMESPACE_MAP,
MODEL_EVALUATION_POLICIES, OIDC_ISSUER, OIDC_AUDIENCE, OIDC_JWKS_URL,
MLFLOW_TRACKING_URI, TRAINING_DATASET_BUCKET, RAY_RUNTIME_VERSION
```

Provide secured environment secrets `DATABASE_URL` and
`MLFLOW_TRACKING_TOKEN`. Confirm the database DSN validates TLS server certs.
The release workflow currently materializes Kubernetes Secrets; migration to
External Secrets/Secrets Manager and automated rotation is an open production
security control requiring a separate privileged controller.

Run `.github/workflows/aws-mlplatform-release.yml` with the approved
**protected production branch head SHA**. GitHub OIDC builds and pushes separate
immutable control-plane and worker images to ECR and the private runner deploys
their digest-pinned manifests. The workflow does **not** auto-provision EKS,
migrate database schemas or install KubeRay/Prometheus.

## 5. Exercise an actual ML engineer deployment

1. Build a Ray-compatible image for `python -m lsk_training.entrypoint` and
   publish it as an immutable approved ECR digest.
2. Submit `MLPlatformClient.train_model()` to an approved tenant dataset
   URI and inspect `training_status()`. Verify actual RayJob completion,
   dataset lineage, GPU allocation and MLflow run output.
3. Log MLflow run and authorized evaluation metrics; produce image with
   `GET /healthz`, `GET /readyz`, `POST /predict` at port 8080.
4. Register model through `register_model()`, with exact image digest bound to
   MLflow metadata; a different actor approves it.
5. Request deployment with `deploy_model()`; API returns pending while worker
   processes durable queue. Verify the status API reports observed image,
   revision and fully available replicas.
6. Call `predict()` through the scoped inference gateway; verify unauthorized,
   cross-tenant, over-limit, unhealthy and revoked model requests are rejected.
7. Exercise rollback and model revocation. Confirm audit metadata and deny path.

## 6. Validate production operation and formal handover

- Demonstrate Multi-AZ resiliency, load tests, SLO/error-budget dashboards,
  authentication failures, HTTP request/latency alerts and worker retry alerts.
- Run vulnerability scans, model image signature verification, tenant network
  isolation tests, IAM reviews, prompt/input security where applicable,
  secrets rotation and production backups/restores.
- Test RPO/RTO, failed Kubernetes upgrades, version rollbacks, DNS/network
  dependency loss, MLflow outage and delayed Ray jobs.
- Approve Quality/security/CTO/Platform/SRE operational ownership and record
  real signed change and handover evidence.

## Current status

Code and CI are present; infrastructure and operators require an authorized
AWS deployment. Model admission image attestation, External Secrets rotation,
full Ray GPU integration, progressive canary, full model monitoring and live
security/DR exercises remain release gates—not silently completed work.

See [release gates](PRODUCTION_RELEASE_GATES.md), [capability matrix](CAPABILITY_MATRIX.md)
and [operations runbook](OPERATIONS_RUNBOOK.md).
