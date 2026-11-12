# Release, rollback, backups and disaster recovery

Deployments require: signed OCI image digest, policy compliance, tests, ML evaluation report, data+code lineage, human model approval, staging load test, SRE release review, change ticket and safe rollback digest.

Argo CD sync applies *approved manifests*, it must **not** independently choose the latest MLflow model. Use progressive rollout (Argo Rollouts or equivalent) for 5%→25%→100% with automated telemetry pauses and human approval. Roll back to last approved immutable revision if error budget or drift breached. Test rollback does not mutate QMS records.

RDS: automated backups, PITR and restore drill. S3: versioning, SSE-KMS, lifecycle and immutability retention when approved. ECR: signed immutable artifacts. Multi-AZ is not a substitute for offsite DR. Establish DR region/legal approval; never replicate controlled data into unauthorized geography.

Proposed RPO <=1h, RTO <=4h; **not validated**. Quarterly restore, annual regional recovery exercise, monthly backup alert checks. DR pass requires measured restoration and data digest verification.

Example GitOps manifests use placeholder images. They are planning assets, not an installable release.
