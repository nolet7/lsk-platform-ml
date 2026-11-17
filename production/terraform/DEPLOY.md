# AWS EKS production deployment — execution playbook

**Current state:** deployable source and Terraform are prepared, but no AWS resources were created from this chat. No production implementation is certified by this file. The project uses synthetic repair orders, not live aerospace customer data.

## Account prerequisites

1. Confirm the production AWS account owner, cost limit and region; apply only with explicit authorization.
2. Bootstrap a separately protected remote S3 Terraform state bucket and per-environment key, encryption, versioning, lockfile and access controls.
3. Establish two short-lived GitHub OIDC IAM roles: one ECR image publisher and one restricted EKS deployment identity. Restrict trust policy to this repository and the GitHub production environment.
4. Approve three-AZ VPC cost (three NAT gateways), EKS worker instances, Multi-AZ RDS, logging, and quotas. Separate prod and stage accounts.
5. Deploy a private self-hosted GitHub Actions runner within the trusted AWS VPC, labeled aws-private, equipped with AWS CLI v2, kubectl, Python 3 and private cluster network reachability.
6. Configure the GitHub production environment with required human reviewers and variables AWS_ACCOUNT_ID, AWS_REGION, AWS_BUILD_ROLE_ARN, AWS_DEPLOY_ROLE_ARN, EKS_CLUSTER_NAME, ECR_REPOSITORY, OIDC_ISSUER, OIDC_AUDIENCE and OIDC_JWKS_URL; set environment secret DATABASE_URL.
7. Initialize DB using production/db/001_init.sql via approved migration identity; app DB user gets SELECT/INSERT only and TLS certificate validation.

## Terraform sequence

Copy terraform.tfvars.example to terraform.tfvars and supply real approved values (never commit this file). Set up S3 backend, then:

    cd production/terraform
    terraform fmt -check
    terraform init -backend-config="bucket=<STATE_BUCKET>" -backend-config="key=lsk-platform-ml/prod/terraform.tfstate" -backend-config="region=<AWS_REGION>" -backend-config="use_lockfile=true"
    terraform validate
    terraform plan -var-file=terraform.tfvars -out=tfplan
    terraform apply tfplan

Terraform apply requires authorized AWS credentials and prior review. No cost-bearing infrastructure provisioning has occurred here.

## Application release

After merging the workflow to the repository default branch and configuring production environment protections, dispatch Production AWS EKS release with an approved full source SHA. The workflow checks the AWS account, pushes to immutable ECR, resolves a SHA256 digest, deploys through a private runner, verifies readiness and verifies the demo key is rejected. Inspect workflow logs and Kubernetes rollout for success before advertising any deployed service.

## Remaining enterprise controls

This synthetic single-service deployment is not the complete enterprise ML platform. MLflow, Ray, GPU pools, signed images, fully integrated ERP/QMS, external identity and least-privileged tenant partitioning, ingress TLS and audited real user flows, policy-enforced egress, secret rotation, production model evaluation/promotions, backup restore proof, canary rollback, monitoring dashboards and signed operational handover are still required. The example Kubernetes NetworkPolicy needs CNI enforcement validation and is not automatically applied. Service is ClusterIP only: network access is internal, not public.

**Production is NOT VERIFIED until cloud resources, application workload and controls are demonstrated in the authorized account with real evidence.**

One-time bootstrap: a separate cluster-admin identity must run `kubectl apply -f production/k8s/namespace.yaml` after EKS provisioning. The routine CI deployment role is restricted to namespace ml-quality; it only applies `production/k8s/serviceaccount.yaml` within that namespace. Configure `eks_platform_admin_role_arn` separately from `eks_deployer_role_arn`. The release SHA must equal the protected production branch head.

## ML platform, rather than example-model rollout

The workflow `.github/workflows/aws-production-release.yml` deploys the **synthetic aerospace example application only**, not the shared ML deployment control plane. For the actual platform, apply `production/db/002_platform_control_plane.sql` under an approved migration identity, configure tenant namespace/RBAC resources with `production/scripts/render_tenant_bootstrap.py`, and dispatch `.github/workflows/aws-mlplatform-release.yml` with approved GitHub production environment variables/secrets, including `ML_PLATFORM_ECR_REPOSITORY`, `TENANT_NAMESPACE_MAP`, `MODEL_EVALUATION_POLICIES`, `MLFLOW_TRACKING_URI` and `MLFLOW_TRACKING_TOKEN`. Verify real model registration, separate approval, submission and observed health from an authorized OIDC client before go-live. Do not synchronize the obsolete `production/gitops/application.yaml` blueprint.
