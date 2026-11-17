# Enterprise ML platform: production target

**Implementation status:** the production-specific AWS EKS runtime and ML deployment control plane exist in feature branch `feature/ml-deployment-platform-control-plane`; they have not yet been merged into this branch or installed in AWS. The original `production` branch contains reference architectures and a synthetic single-service application.

Reusable ML deployment platform elements to review:
- `mlplatform/`: self-service registration, real MLflow run verification, approval, version history, Kubernetes reconciliation and rollback interface
- `production/db/002_platform_control_plane.sql`: model/revision/audit schema
- `production/k8s/ml-platform-api.yaml`: control-plane Kubernetes deployment
- `production/scripts/render_tenant_bootstrap.py`: tenant-scoped namespace/RBAC
- `sdk/platform_client.py`: ML engineer-facing API client
- `examples/sklearn_inference/`: standard model-serving inference container
- `.github/workflows/aws-mlplatform-release.yml`: protected CI/CD build and release design

For actual rollout, use `docs/ML_PLATFORM_DEPLOYMENT.md` and `production/terraform/DEPLOY.md`, then collect real gate evidence. Do not describe this public portfolio as a deployed corporate production environment.
