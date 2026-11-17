# Runtime delivery status

- Added: AWS three-AZ VPC, private EKS general worker pool, immutable ECR, S3, Multi-AZ RDS.
- Added: signed-by-issuer RS256 OIDC access-token check, scope gating, removal of demo-key authentication in production.
- Added: image-bundled deterministic synthetic model, non-root runtime, internal 3-replica Kubernetes deployment, smoke-test workflow.
- Added: PostgreSQL prediction/review persistence with unique one-time review semantics and schema.
- Not executed: AWS Terraform plan/apply, provisioning, database migration, ECR image push, EKS deployment, production IAM and SRE validation.
- Not complete: Ray/MLflow/GPU production integrations, real ERP/QMS integrations, full observability + hardening, backup/restore drills and signed handover.
- Thus the work is a deployable baseline and NOT a proven production deployment.
See production/terraform/DEPLOY.md for the account execution sequence.
