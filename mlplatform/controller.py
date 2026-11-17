"""Kubernetes reconciler for explicitly approved model images.

Requires service account RBAC only in allowlisted serving namespaces.
No external cluster credentials or namespaces accepted in user payloads.
"""
from mlplatform.manifest import workload

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

def observe(tenant, name, environment):
    """Return observed rollout health from Kubernetes, not database submission state."""
    from kubernetes import client, config
    from kubernetes.client.exceptions import ApiException
    from mlplatform.manifest import target_namespace, resource_name
    namespace=target_namespace(tenant,environment)
    config.load_incluster_config()
    try:
        deployment=client.AppsV1Api().read_namespaced_deployment(
            resource_name(name),namespace)
    except ApiException as exc:
        if exc.status==404:
            return {"healthy":False,"state":"not_found","available_replicas":0}
        raise
    labels=deployment.metadata.labels or {}
    if labels.get("lsk.ai/tenant") != tenant or labels.get("lsk.ai/managed-by") != "ml-platform":
        raise PermissionError("observed workload is not managed for requesting tenant")
    desired=deployment.spec.replicas or 0
    available=deployment.status.available_replicas or 0
    observed=deployment.status.observed_generation or 0
    generation=deployment.metadata.generation or 0
    healthy=desired>0 and available>=desired and observed>=generation
    return {"healthy":healthy,"state":"healthy" if healthy else "progressing",
            "available_replicas":available,"desired_replicas":desired,
            "observed_generation":observed,"metadata_generation":generation}
