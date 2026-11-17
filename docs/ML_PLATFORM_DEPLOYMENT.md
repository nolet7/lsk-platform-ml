# ML deployment platform runtime (not the aerospace POC)

This folder separates **ML platform control plane** from **example inference workload**. The platform provisions approved, immutable model-serving images; it does not train arbitrary user-supplied code or make aerospace airworthiness decisions.

## Platform user journey

1. ML engineer trains in an authorized external compute environment and logs run, dataset SHA, code SHA, tenant ID, evaluation reference and `validation_auc` to MLflow. The inference service is independently packaged as a non-root OCI image implementing `/healthz`, `/readyz`, `/predict` on TCP 8080 and pushed to the configured AWS ECR account using an immutable digest.
2. ML engineer calls `MLPlatformClient.register_model(...)` with MLflow run ID, artifact URI `runs:/<run_id>/model`, evaluation reference and OCI digest. Control plane validates MLflow metadata and evaluation threshold by API.
3. A **different** authorized engineer approves the registered model with `ml:approve` permission. That is a distinct step from model acceptance by aerospace Quality.
4. Deployment engineer calls `deploy_model(name,model_id,environment,replicas)`. Server derives tenant from signed OIDC `tenant_id` claim and destination namespace from approved server-side map; client cannot specify a namespace.
5. PostgreSQL stores revision/audit, Kubernetes Deployment and Service are created or updated in that tenant environment's pre-provisioned namespace. API returns `submitted`, **not healthy**.
6. User reads deployment history and can request a rollback. Cluster monitoring, actual readiness/traffic acceptance and SLO checks must be independently verified.

## API and SDK

- POST /v1/platform/models : scope `ml:register`
- POST /v1/platform/models/{id}/approve : scope `ml:approve`, different actor
- POST /v1/platform/deployments : scope `ml:deploy`
- GET /v1/platform/deployments/{name}?environment=stage : scope `ml:read`
- GET /v1/platform/deployments/{name}/history?environment=stage : scope `ml:read`
- POST /v1/platform/deployments/{name}/rollback?environment=stage : scope `ml:rollback`

SDK: `sdk/platform_client.py`. All API operations require signed OIDC tokens and per-tenant claims. Production registrations require MLflow HTTPS API and authentication; no fake demo keys.

## Production components and prerequisites

- `mlplatform/`: FastAPI control plane, PostgreSQL registry, MLflow verification, Kubernetes reconciler
- `production/db/002_platform_control_plane.sql`: schema migration, execute separately using approved DBA identity
- `production/k8s/ml-platform-api.yaml`: 3-replica control plane deployment, internal service
- `production/k8s/platform-serviceaccount.yaml`: dedicated controller identity
- `production/scripts/render_tenant_bootstrap.py`: cluster-admin-reviewed tenant namespace, Role, RoleBinding and workload SA resources
- `.github/workflows/aws-mlplatform-release.yml`: standalone approval-gated ECR/EKS deployment
- `production/terraform/platform-registry.tf`: independent ECR repository for platform API

**Example mapping** (not a production namespace grant): `{"tenant-a":{"stage":"tenant-a-stage","production":"tenant-a-prod"}}`. Security/Platform approves each tenant namespace, then runs `python production/scripts/render_tenant_bootstrap.py --mapping approved-tenant-map.json > tenant-bootstrap.json` followed by privileged review and `kubectl apply -f tenant-bootstrap.json`. Ingress/egress isolation is separate and must be tested.

Environment variables `AWS_ACCOUNT_ID`, `AWS_REGION`, `TENANT_NAMESPACE_MAP`, `MLFLOW_TRACKING_URI`, `MLFLOW_TRACKING_TOKEN`, `OIDC_ISSUER`, `OIDC_AUDIENCE`, `OIDC_JWKS_URL`, and `DATABASE_URL` must come from approved managed configuration. Production GitHub environment must enforce reviewers, OIDC role trust and secret protection.

## Known limitations / blockers

**No live cluster, database, MLflow run, production tenant approval, or user traffic has been validated in this project.** Current POC runs locally; platform API tests use mocks for PostgreSQL, MLflow, and Kubernetes. Reconciliation returns desired-state submission; it is not a monitored healthy rollout. There is no GPU training operator, Ray platform, automated image signature validation, deployment canary analysis, secure API ingress, customer ERP/QMS connection or end-to-end disaster recovery evidence. Replace direct secrets with workload identity/External Secrets, implement request idempotency and persistent job-level reconciliation before regulated production. Do not claim production readiness from CI alone.

## Platform telemetry

`/metrics` exposes bounded-cardinality HTTP method/route/status counters and request-duration histograms. `production/k8s/mlplatform-monitoring.yaml` contains Prometheus Operator ServiceMonitor and alert rules. The config is **not** installed automatically: review namespace network policy, scrape permissions, monitoring release selectors and alert routing before deploying in any real cluster. Image-serving traffic and drift require separate workload instrumentation.

## Model-specific evaluation policy

Production requires an externally approved `MODEL_EVALUATION_POLICIES` JSON map keyed by tenant ID then model name, for example `{"tenant-a":{"blade-quality":{"metric":"validation_auc","operator":"gte","threshold":0.85},"demand-forecast":{"metric":"validation_rmse","operator":"lte","threshold":5.0}}}`. The client may not choose its own success threshold. Missing/invalid policies fail closed; actual MLflow metrics must satisfy the configured comparator. Configure the same map as the GitHub production environment variable and platform ConfigMap; independently verify it against domain Quality/ML governance. AUC is an example, not a universal metric for every model type.
