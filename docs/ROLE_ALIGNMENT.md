# Role alignment — ML Platform Engineer / FDE / SRE

This independent portfolio simulation demonstrates a **platform for ML model deployment** rather than a production employer-owned system.

| Capability | Code evidence | Real-world validation needed |
|---|---|---|
| Developer self service | `sdk/platform_client.py`, `mlplatform/api.py` | OIDC-authenticated ML engineer end-to-end workflow |
| Model governance | `mlplatform/mlflow_gate.py`, `mlplatform/store.py` | Live MLflow run + signed evaluation and separate approver |
| Kubernetes deployment | `mlplatform/controller.py`, `mlplatform/manifest.py` | Authorized per-tenant EKS rollout and rollback drill |
| Cloud platform | `production/terraform/` | AWS account plan/apply and security verification |
| Database and audit | `production/db/002_platform_control_plane.sql` | Applied migration, isolation and backup/restore |
| Runtime interoperability | `examples/sklearn_inference/` | OCI built and run through API with real traffic |
| Operations | `production/k8s/`, `docs/enterprise/` | Live SLOs, monitoring, incident and handover signoff |

Do not claim commercial deployment or measured availability, cost/MTTR benefit or GPU benchmarks based only on these files.
