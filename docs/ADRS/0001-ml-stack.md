# ADR-0001 — ML infrastructure technology selection
**Status:** Proposed for simulated program, accepted for portfolio implementation.

- **AWS EKS** primary compute and API hosting: consistent with role's AWS focus, integrates with IAM/VPC, GPU nodes. Tradeoff: EKS complexity and cost; POC runs locally.
- **Kubernetes Jobs + Ray Jobs** for distributed training. Start with plain Jobs to minimize orchestration; use Ray for parallel CPU/GPU experiments where justified. Not all models require distributed training.
- **Argo Workflows (pilot option)** for reproducible pipelines; not Kubeflow by default because the project prioritizes a lightweight platform and operator ownership. Revisit after evaluating a real multi-stage ML pipeline workload.
- **MLflow** experiment tracking and model registry, backed by PostgreSQL and object storage; registration != authorization to release.
- **FastAPI + typed Python SDK** for developer ergonomics. QMS remains source of truth, and inbound integration is read-only.
- **Terraform + Helm + Argo CD** provision/configure/reconcile. Separate infra deployment from model approval.
- **OpenTelemetry, Prometheus, Grafana** metrics, traces and alerts. Central logs with privacy filters.
- **ONNX or OCI packaged inference** optional for optimized serving; pin model digest and hardware compatibility.
- **S3** immutable dataset snapshots and model artifacts with KMS and retention. Object ACLs denied by default.

Alternatives: SageMaker can reduce managed-service operations, but higher coupling is a tradeoff. Kubeflow brings integrated ML UX at higher operational overhead. KServe may be adopted when serving diversity and autoscaling warrant it; begin with plain FastAPI Deployment and HPA.
