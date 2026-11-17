# Enterprise ML platform — mandatory production gates

No checkboxes in source control constitute a completed production signoff.
This file defines auditable release requirements.

## Infrastructure and identity
- [ ] Corporate AWS account/region, cost caps and business owner verified
- [ ] Terraform plan approved; remote encrypted, locked state and DR storage tested
- [ ] Private EKS with multi-AZ nodes; pod readiness across zones demonstrated
- [ ] Private PostgreSQL with PITR and restore exercise; separate app/migration identities
- [ ] OIDC issuer/audience/JWKS integration tested with negative authorization cases
- [ ] Workload identity, external secret rotation, ECR digest and signature verification
- [ ] Tenant namespace + network policy + quota + limit range + resource identities tested

## Model life cycle
- [ ] Reproducible training dataset digest and code commit
- [ ] Authenticated MLflow run, model registry, metrics and human approval evidence
- [ ] Training GPU/Ray or CPU job completes under per-tenant quotas
- [ ] A signed OCI serving image is bound to evaluated run and scanned
- [ ] Independent approver cannot self-approve; cross-tenant tests are blocked
- [ ] Model registration → approval → stage → performance/security verification → production
- [ ] Live inference test validates model's version, input schema, response and latency
- [ ] Canary promotion and rollback under injected faults verified

## Operations and handover
- [ ] API / worker error budgets, alert rules, dashboards and runbooks validated
- [ ] Reconciliation retries and stale deployment rejection tested
- [ ] Dependency failures and replay/duplicate requests addressed
- [ ] Restore of RDS and model artifacts tested with measured RPO/RTO
- [ ] Security and Quality authority approve workload/tenant-specific rollout
- [ ] CTO, Platform/SRE and ML owner sign deployment and on-call transfer
- [ ] 7/30/90 day performance, adoption and cost reviews scheduled

This is a **gate list**, not proof that any gate passed.
