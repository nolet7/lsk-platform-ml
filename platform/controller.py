"""Kubernetes reconciler for explicitly approved model images.

Requires service account RBAC only in allowlisted serving namespaces.
No external cluster credentials or namespaces accepted in user payloads.
"""
from platform.manifest import workload

def apply(tenant, name, environment, image, replicas, revision):
    namespace, deploy, service = workload(
        tenant, name, image, replicas, environment, revision
    )
    from kubernetes import client, config
    from kubernetes.client.exceptions import ApiException
    config.load_incluster_config()
    apps, core = client.AppsV1Api(), client.CoreV1Api()
    resource = deploy["metadata"]["name"]

    try:
        existing = apps.read_namespaced_deployment(resource, namespace)
        if (existing.metadata.labels or {}).get("lsk.ai/tenant") != tenant or (
            existing.metadata.labels or {}
        ).get("lsk.ai/managed-by") != "ml-platform":
            raise PermissionError("refusing to replace unmanaged Kubernetes deployment")
        apps.patch_namespaced_deployment(resource, namespace, deploy)
    except ApiException as exc:
        if exc.status != 404:
            raise
        apps.create_namespaced_deployment(namespace, deploy)

    try:
        existing_service = core.read_namespaced_service(resource, namespace)
        if (existing_service.metadata.labels or {}).get("lsk.ai/tenant") != tenant or (
            existing_service.metadata.labels or {}
        ).get("lsk.ai/managed-by") != "ml-platform":
            raise PermissionError("refusing to replace unmanaged Kubernetes service")
    except ApiException as exc:
        if exc.status != 404:
            raise
        core.create_namespaced_service(namespace, service)

    # API accepted desired state, not a verified healthy rollout.
    return {"namespace": namespace, "deployment": resource,
            "service": resource, "state": "submitted"}
