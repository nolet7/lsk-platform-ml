# Infrastructure-as-code starter — AWS data artifact foundation

The code configures only a versioned, encrypted and public-access-blocked S3 bucket for synthetic artifacts. This is **not** a deployable enterprise EKS platform; a full platform requires landing-zone and KMS approval, VPC, private EKS, node pools, RDS, ECR, OIDC, IRSA/Pod Identity, policies, logging and DR. Do not apply against a real organization without architecture/security approval.

Run: `terraform init`, `terraform fmt -check`, `terraform validate`; use a dedicated sandbox AWS account and backend configuration before `plan`. Never commit tfstate.
