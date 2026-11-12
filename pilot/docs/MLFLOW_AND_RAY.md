# MLflow + Ray integration design

MLflow server: private ClusterIP + RDS/PostgreSQL backend + S3 artifact store with KMS; access via authenticated gateway and project-scoped policy. Model evaluation generates dataset hash, algorithm/config, training image SHA, Git commit, seed, ROC AUC, calibration and subgroup tests. Registration creates a **candidate** model; it cannot trigger production deployment automatically.

Ray Jobs: dedicated RayCluster and KubeRay operator to run parallelized feature extraction and CPU/GPU jobs. GPU workloads use vendor device plugin, nvidia.com/gpu requests, taints/tolerations, topology affinity, queue budgets and timeouts. Benchmark single-node first; Ray only for workloads shown to benefit. Collect VRAM, accelerator utilization, GPU-hours, queue depth and cost per successful run.

Cross-plane data placement: do not move controlled customer artifacts into public cloud unless legal and information-security authorize it. On-prem ML worker can train against local storage and publish only approved, non-sensitive aggregate metadata.

Pilot task: replace POC local file model with MLflow artifact retrieval, implement authenticated registration and evaluation policy, create actual MLflow+Ray Helm deployments, plus tested data movement restrictions. This is an integration design, not an operational deployment claim.
