# Security policy — LSK ML Deployment Platform

This repository is an independent synthetic demonstration and should not be
treated as a deployed, certified aerospace system.

Report security issues privately through GitHub's security advisories or the
repository owner's approved private contact method. Do not publish tokens,
tenant datasets, reproduction payloads or customer data in public issues.

## Enterprise security controls

- OIDC JWT authorization with model and tenant scopes
- Strict model digest, provider account/region, MLflow evaluation and approval
- Self-approval prevention, audit events, model revocation, metadata-only inference
- Namespace quotas, admission boundaries, NetworkPolicy default deny and distinct
  Kubernetes ServiceAccounts for API and reconciler
- Container vulnerability scans, Python dependency auditing, source analysis,
  generated SBOMs and independently reviewed CI/CD release approvals
- Private cluster, RDS and S3 storage with customer-managed KMS and TLS policies

## Unfinished external validation

No tenant isolation penetration test, customer-data handling approval, production
secrets rotation, signed model image admission, SLSA/in-toto provenance verification,
live IAM drift test or supply-chain attestation has been established here.
Use signed image admission (Cosign/Sigstore or organization-approved equivalent)
and verify ECR image provenance **before** allowing regulated production workloads.
The repository's scans do not substitute for independently authorized security
assessment, operator rollout and observed evidence.
