# Enterprise Ray/GPU training on Kubernetes

Training is a separate service capability from online inference. An ML engineer
may submit **only a prebuilt immutable ECR image** that implements the fixed
`python -m lsk_training.entrypoint` contract and uses a declared dataset URI.

The `mlplatform/training.py` builder creates RayJob `ray.io/v1` custom objects
with bounded worker count, CPU/GPU resources, deadline, cleanup and namespace
isolation. KubeRay operator must be installed by a separately approved cluster
admin. Its manifests follow Ray's official RayJob schema. Training pod image
must contain the exact pinned Ray runtime version configured by SRE.

Architecture dependencies:
1. Approved EKS GPU managed-node group (optionally enabled in Terraform).
2. NVIDIA device plugin, schedulable GPU resources and GPU quota.
3. KubeRay operator CRD and controller with approved version.
4. Tenant namespace Role/RoleBinding for RayJob create/get and image policies.
5. IAM Pod Identity scoped to tenant S3 dataset and MLflow access.
6. Approved training image with fixed entrypoint, application-level checkpoints,
   logging, validation metric recording and MLflow run lineage.
7. GPU cost monitoring, job expiry and budget enforcement.

**Not proven:** no GPU nodes, operator or Ray jobs have been provisioned in AWS
during this session. The code implements a supported scheduling contract but
cannot claim GPU training success until cluster and workload acceptance tests.

The AWS infrastructure module now includes an optional GPU managed node group
(`enable_gpu_nodes`, `gpu_instance_types`, `gpu_node_max`). It uses the
AL2023 NVIDIA AMI, `lsk.ai/gpu=true` node label and NoSchedule taint.
GPU node count starts at zero; an authorized cluster autoscaler/Karpenter
strategy is required for scale-from-zero. Device-plugin installation and
GPU capability verification remain separate privileged steps. See
[official EKS AI/ML setup](https://docs.aws.amazon.com/eks/latest/userguide/ml-cluster-setup-tf.html).
