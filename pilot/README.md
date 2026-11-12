# Pilot: shared ML platform for 2 engineering teams

**Status:** reference implementation assets; no claim cluster deployed.
Scope: Quality Engineering and Repair Engineering run synthetic projects with separate namespaces, MLflow experiments and Kubernetes training jobs. Pilot evidence includes access controls, reproducibility, workload queue, metrics, failure handling and onboarding feedback.

## Pilot readiness gates
- Staging EKS (or local kind) and artifact registry provisioned, workloads isolated
- Namespace network policies, resource limits, Pod Security and project ownership verified
- Training job uses unique run ID and immutable image + dataset digest
- Tracking and artifact storage deployed privately, backups tested
- Evaluation pipeline blocks low-quality models; release approval distinct from MLflow registration
- AuthN/AuthZ via OIDC JWT gateway, **not POC demo header**
- Dashboards/alerts live, multi-team adoption measured, rollback exercised

## Manual commands (requires cluster and approved registry)
```bash
kubectl apply -f pilot/k8s/namespaces.yaml
kubectl apply -f pilot/k8s/networkpolicy.yaml
kubectl apply -f pilot/k8s/quotas.yaml
kubectl -n ml-quality apply -f pilot/k8s/training-job.yaml
kubectl -n ml-quality logs job/synthetic-inspection-train
```
The training image below is a placeholder until built, scanned, signed, pushed, and pinned to a real SHA256 digest. Do not deploy placeholder image.
