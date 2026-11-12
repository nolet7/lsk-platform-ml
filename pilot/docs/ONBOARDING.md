# Internal developer portal / onboarding contract

Developer workflow: request ML project → manager/data-owner approval → namespace, workload identity, S3 prefix, MLflow experiment and quota provisioned → obtain scoped API credentials → submit dataset manifest → run training template → view metrics and artifacts → request registration → evaluation policy → separate quality/platform approval → deploy to stage → smoke test and rollback.

Portal API target:
POST /v1/projects; POST /v1/datasets; POST /v1/runs; GET /v1/runs/{id}; POST /v1/models/{id}/approval-requests; GET /v1/quotas. All mutations idempotent and audited; project scoping on every request. SDK returns stable errors, run IDs and trace IDs.

Adoption measurements: time-to-first-run, successful deployments, manual tickets avoided, run queue wait, developer satisfaction, weekly active projects, cost by project. No unmeasured improvement claims.
