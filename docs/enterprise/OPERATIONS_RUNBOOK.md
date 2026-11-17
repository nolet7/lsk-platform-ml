# Operational runbook — ML deployment platform

## Alert response
- **Platform API /readyz fails:** check Postgres connectivity, OIDC config, pod health and telemetry; block new model promotions.
- **MLflow unavailable:** registration fails closed. Running immutable models continue serving independently.
- **Reconciler retry backlog:** inspect `platform_deployments` retry_count, next_attempt_at, lease_until and state; verify worker service account RBAC. Do not blindly reset state while reconciliation is active.
- **Model serving unhealthy:** confirm actual image SHA and deployment revision match expected, then inspect readiness, replicas, image pulls, resource quota, and DNS.
- **Data breach/isolation failure:** revoke access, preserve audit records, involve security and data governance.

## Operational SQL (read-only)
```sql
SELECT tenant_id,name,environment,revision,state,retry_count,next_attempt_at
FROM platform_deployments
WHERE state IN ('pending','retry','reconciling','failed')
ORDER BY created_at ASC;
```

## Rollback
Use an approved release revision, verify model approval remains valid, submit a new rollback revision through the SDK, confirm observed Kubernetes image + revision, then run inference checks and attach evidence.

## Restore drill
Use a separate isolated AWS environment; restore encrypted PostgreSQL from managed snapshot/PITR and compare model registry and audit counts/digests. Verify referenced immutable model OCI images remain resolvable. Measure achieved RPO/RTO and record signed results.

## Important
The production AWS account has not been provisioned or verified in this ChatGPT session. This runbook is not an incident log and does not assert successful tests.
