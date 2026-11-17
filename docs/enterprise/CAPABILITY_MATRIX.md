# Enterprise ML platform capability coverage

| Capability | Implementation | Readiness |
|---|---|---|
| Model registration/versioning | mlplatform/api.py, store.py, 002 schema | Unit-tested; live DB migration pending |
| MLflow experiment lineage/evaluation | mlplatform/mlflow_gate.py | Unit-tested with fake API; live integration pending |
| Separation of duty | Store approval rules, OIDC claims | Unit-tested; identity provider pending |
| ML engineer self-service SDK | sdk/platform_client.py | Source present; live usage pending |
| Kubernetes deployment | manifest/controller, tenant RBAC bootstrap | Manifest tests; live EKS pending |
| Durable reconciliation | reconciler.py, 003 DB migration | Unit tests; live failure/drill pending |
| Observability | Prometheus API metrics, ServiceMonitor/PrometheusRule | Manifests; alert routing pending |
| Multi-AZ AWS infrastructure | production/terraform | Static validation, no Terraform apply |
| Secrets and signing | Workflows/config contracts | External Secrets, signing and attestation verification not complete |
| Ray/GPU training | mlplatform/training.py, 004 schema, queued worker, optional GPU Terraform group | API/manifest/DB tests; live KubeRay/GPU pending |
| Model canary / drift | Image/revision health checks, revocation and rollback | Progressive analysis/model drift pipeline pending |
| Security isolation | JWT, tenant quotas/RBAC, default-deny policies, scoped inference gateway | Need live enforcement, signing, pen tests and supply chain |
| Disaster recovery | Multi-AZ RDS/PITR, KMS, restoration runbook | No restoration exercise evidence |
| Durable deployment lifecycle | 003 DB schema, worker lease/retry + revision fencing | PostgreSQL CI tests; failover drills pending |
| Inference serving access | Signed-tenant gateway + metadata-only audit + revocation | Unit tests; real TLS ingress and live traffic pending |
| FinOps + encryption | Customer KMS, AWS cost budget, RDS alarms | Terraform validation; account/alerts not provisioned |

**Readiness:** source and design improvements do not imply enterprise production approval.
