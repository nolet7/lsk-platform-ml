"""Constrained, tenant-scoped Kubernetes inference workload manifest builder."""
import json
import os
import re

_IMAGE = re.compile(
    r"^(?P<account>[0-9]{12})\.dkr\.ecr\.(?P<region>[a-z0-9-]+)\.amazonaws\.com/"
    r"(?P<repo>[a-z0-9][a-z0-9/_.-]*)@sha256:[a-f0-9]{64}$"
)
_LABEL = re.compile(r"^[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?$")

def validate_image(image: str) -> None:
    match = _IMAGE.fullmatch(image)
    if not match:
        raise ValueError("inference image must be an immutable AWS ECR sha256 digest")
    if match.group("account") != os.getenv("AWS_ACCOUNT_ID") or match.group("region") != os.getenv("AWS_REGION"):
        raise ValueError("image must belong to the approved AWS account and region")

def target_namespace(tenant: str, environment: str) -> str:
    if not _LABEL.fullmatch(tenant):
        raise ValueError("invalid tenant identity")
    try:
        mapping = json.loads(os.environ["TENANT_NAMESPACE_MAP"])
        namespace = mapping[tenant][environment]
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError("tenant/environment namespace is not provisioned") from exc
    if not isinstance(namespace, str) or not _LABEL.fullmatch(namespace):
        raise ValueError("invalid namespace mapping")
    return namespace

def resource_name(name: str) -> str:
    if not re.fullmatch(r"[a-z][a-z0-9-]{1,39}", name):
        raise ValueError("invalid deployment name")
    return "ml-" + name

def workload(tenant, name, image, replicas, environment, revision):
    validate_image(image)
    namespace = target_namespace(tenant, environment)
    resource = resource_name(name)
    labels = {"app.kubernetes.io/name": resource, "lsk.ai/tenant": tenant,
              "lsk.ai/managed-by": "ml-platform"}
    annotations = {"lsk.ai/deployment-revision": str(revision)}
    deployment = {
        "apiVersion": "apps/v1", "kind": "Deployment",
        "metadata": {"name": resource, "namespace": namespace, "labels": labels},
        "spec": {
            "replicas": replicas, "revisionHistoryLimit": 5,
            "selector": {"matchLabels": {"app.kubernetes.io/name": resource}},
            "strategy": {"type": "RollingUpdate", "rollingUpdate": {"maxUnavailable": 0, "maxSurge": 1}},
            "template": {
                "metadata": {"labels": labels, "annotations": annotations},
                "spec": {
                    "serviceAccountName": "ml-model-serving", "automountServiceAccountToken": False,
                    "securityContext": {"runAsNonRoot": True, "runAsUser": 10001,
                                        "seccompProfile": {"type": "RuntimeDefault"}},
                    "containers": [{
                        "name": "inference", "image": image, "imagePullPolicy": "IfNotPresent",
                        "ports": [{"name": "http", "containerPort": 8080}],
                        "readinessProbe": {"httpGet": {"path": "/readyz", "port": "http"},
                                           "periodSeconds": 10},
                        "livenessProbe": {"httpGet": {"path": "/healthz", "port": "http"},
                                          "periodSeconds": 20},
                        "securityContext": {"allowPrivilegeEscalation": False,
                                            "readOnlyRootFilesystem": True,
                                            "capabilities": {"drop": ["ALL"]}},
                        "resources": {"requests": {"cpu": "250m", "memory": "512Mi"},
                                      "limits": {"cpu": "2", "memory": "2Gi"}}
                    }]
                }
            }
        }
    }
    service = {
        "apiVersion": "v1", "kind": "Service",
        "metadata": {"name": resource, "namespace": namespace, "labels": labels},
        "spec": {"type": "ClusterIP", "selector": {"app.kubernetes.io/name": resource},
                 "ports": [{"name": "http", "port": 80, "targetPort": "http"}]}
    }
    return namespace, deployment, service
