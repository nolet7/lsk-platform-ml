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
| Ray/GPU training | pilot manifests/design | Not integrated end to end |
| Model canary / drift | Status and revision checks | Progressive analysis/drift pipeline not complete |
| Security isolation | Scoped namespaces/RBAC, JWT, optional network policy | Need enforced network policy, pen tests and supply chain |
| Disaster recovery | RDS backups, restoration runbook | No restoration exercise evidence |

**Readiness:** source and design improvements do not imply enterprise production approval.
