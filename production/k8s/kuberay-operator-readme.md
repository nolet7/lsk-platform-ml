# KubeRay operator — cluster bootstrap

This is a **cluster-scoped privileged dependency**, not installed by application
CI or from a guessed Helm chart version.

Platform/Security administrator must pin and approve a compatible KubeRay
operator Helm chart version and CRDs from the official Ray distribution. Install
operator via approved GitOps/Helm bootstrap using a cluster administrative role,
then verify RayJob CRDs exist and controllers are healthy.

Required checks:
- `kubectl get crd rayjobs.ray.io rayclusters.ray.io`
- `kubectl get pods -n <approved-operator-namespace>`
- `kubectl auth can-i create rayjobs.ray.io -n <tenant-namespace> --as=system:serviceaccount:ml-quality:ml-platform-controller`
- Confirm GPU device plugin and labels/taints on GPU nodes, per-tenant job
  quotas, image provenance, storage identity and alerting.

Do not install unpinned Helm charts into production or give a tenant actor
cluster-admin permissions.
