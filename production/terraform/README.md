# AWS infrastructure for LSK ML deployment platform

Terraform configuration defines:
- Private EKS across three available AZs, managed system/API worker group
- Multi-AZ VPC with NAT per AZ
- Versioned encrypted synthetic-only S3 artifact bucket
- Private encrypted Multi-AZ RDS PostgreSQL metadata database
- Immutable ECR repositories for aerospace inference example and reusable ML platform control plane
- EKS access entries separating bootstrap cluster admin from namespace-scoped application deploy role

**This is unprovisioned IaC.** No IAM trust policy or environment costs are automatically authorized. Additional components required for actual enterprise ML deployments include OIDC issuer, MLflow deployment, tenant namespace isolation, model image build/approval, network-policy enforcement, monitoring, operational tests and GPU/Ray infrastructure.

Before provisioning, approve AWS account/network CIDR, region, budget/quotas, remote state and GitHub OIDC permissions; confirm EKS and Kubernetes compatibility. See `DEPLOY.md` and `docs/ML_PLATFORM_DEPLOYMENT.md`.

Static checks:
```bash
terraform fmt -check
terraform init -backend=false
terraform validate
```
Actual plan/apply must run under authorized AWS credentials, with external state backend and reviewed real variable values.
