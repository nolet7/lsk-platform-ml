"""Tenant-scoped, immutable-image KubeRay training jobs.

RayJob's entrypoint is fixed; users cannot inject shell commands, pod specs,
namespace, service-account or arbitrary environment variables through the API.
KubeRay operator, GPU device plugin and tenant S3 identity are prerequisites.
"""
import os
import re
from uuid import UUID
from kubernetes.client.exceptions import ApiException
from mlplatform.manifest import target_namespace, validate_image

def validate_dataset(tenant: str, uri: str):
    bucket = os.environ.get("TRAINING_DATASET_BUCKET","")
    prefix=f"s3://{bucket}/{tenant}/datasets/"
    if not bucket or not uri.startswith(prefix):
        raise ValueError("dataset must reside under approved tenant dataset prefix")
    path=uri[len(prefix):]
    if not path or ".." in path.split("/") or not re.fullmatch(r"[A-Za-z0-9._/-]+",path):
        raise ValueError("invalid dataset object key")

def job_manifest(row):
    tenant,env=row["tenant_id"],row["environment"]
    namespace=target_namespace(tenant,env)
    validate_image(row["image"])
    validate_dataset(tenant,row["dataset_uri"])
    version=os.getenv("RAY_RUNTIME_VERSION","")
    if not re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+",version):
        raise RuntimeError("RAY_RUNTIME_VERSION must be an approved pinned version")
    gpu=int(row["gpu_per_worker"])
    count=int(row["workers"])
    if gpu not in (0,1) or not 1<=count<=4:
        raise ValueError("GPU / worker budget exceeds platform policy")
    job_id=UUID(str(row["id"])).hex[:24]
    name="ml-train-"+job_id
    labels={"lsk.ai/tenant":tenant,"lsk.ai/managed-by":"ml-platform"}
    security={"runAsNonRoot":True,"runAsUser":10001,
              "seccompProfile":{"type":"RuntimeDefault"}}
    mlflow_uri=os.getenv("MLFLOW_TRACKING_URI","")
    if not mlflow_uri.startswith("https://"):
        raise RuntimeError("approved HTTPS MLflow tracking URI is required")
    env_vars=[
        {"name":"LSK_DATASET_URI","value":row["dataset_uri"]},
        {"name":"LSK_TRAINING_JOB_ID","value":str(row["id"])},
        {"name":"LSK_TENANT_ID","value":tenant},
        {"name":"LSK_MODEL_NAME","value":row["name"]},
        {"name":"LSK_EVALUATION_REF","value":str(row["id"])},
        {"name":"TRAINING_DATASET_BUCKET","value":os.environ["TRAINING_DATASET_BUCKET"]},
        {"name":"AWS_REGION","value":os.environ["AWS_REGION"]},
        {"name":"LSK_GPU_PER_WORKER","value":str(gpu)},
        {"name":"MLFLOW_TRACKING_URI","value":mlflow_uri},
        {"name":"MLFLOW_TRACKING_TOKEN","valueFrom":{
            "secretKeyRef":{"name":"ml-training-mlflow","key":"token"}}},
    ]
    def pod(container, cpu, mem, needs_gpu):
        res={"requests":{"cpu":cpu,"memory":mem},"limits":{"cpu":cpu,"memory":mem}}
        if needs_gpu:
            res["limits"]["nvidia.com/gpu"]=str(gpu)
            res["requests"]["nvidia.com/gpu"]=str(gpu)
        spec={"serviceAccountName":"ml-model-training",
              "automountServiceAccountToken":False,
              "securityContext":security,
              "containers":[{"name":container,"image":row["image"],"imagePullPolicy":"IfNotPresent",
                             "env":env_vars,"resources":res,
                             "securityContext":{"allowPrivilegeEscalation":False,
                                                "capabilities":{"drop":["ALL"]}}}]}
        if container=="ray-head":
            spec["containers"][0]["ports"]=[
                {"name":"gcs-server","containerPort":6379},
                {"name":"dashboard","containerPort":8265},
                {"name":"client","containerPort":10001},
            ]
        if needs_gpu:
            spec["nodeSelector"]={"lsk.ai/gpu":"true"}
            spec["tolerations"]=[{"key":"lsk.ai/gpu","operator":"Equal",
                                  "value":"true","effect":"NoSchedule"}]
        return {"spec":spec}
    spec={
       "entrypoint":"python -m lsk_training.entrypoint",
       "shutdownAfterJobFinishes":True,
       "ttlSecondsAfterFinished":86400,
       "activeDeadlineSeconds":14400,
       "rayClusterSpec":{
         "rayVersion":version,
         "headGroupSpec":{"rayStartParams":{},"template":pod("ray-head","1","2Gi",False)},
         "workerGroupSpecs":[{
            "groupName":"trainer","replicas":count,"minReplicas":count,"maxReplicas":count,
            "rayStartParams":{},"template":pod("ray-worker","2","4Gi",gpu>0)}]
       }
    }
    return namespace,{"apiVersion":"ray.io/v1","kind":"RayJob",
        "metadata":{"name":name,"namespace":namespace,"labels":labels},
        "spec":spec}

def apply_training(row):
    from kubernetes import client, config
    namespace,manifest=job_manifest(row)
    config.load_incluster_config()
    custom=client.CustomObjectsApi()
    try:
        custom.create_namespaced_custom_object(
            group="ray.io",version="v1",namespace=namespace,plural="rayjobs",body=manifest)
    except ApiException as exc:
        if exc.status != 409:
            raise
        existing=custom.get_namespaced_custom_object(
            group="ray.io",version="v1",namespace=namespace,plural="rayjobs",
            name=manifest["metadata"]["name"])
        if existing.get("metadata",{}).get("labels") != manifest["metadata"]["labels"] or existing.get("spec") != manifest["spec"]:
            raise PermissionError("existing RayJob does not match immutable request") from exc
    return {"state":"submitted","name":manifest["metadata"]["name"],"namespace":namespace}

def observe_training(row):
    from kubernetes import client, config
    namespace, manifest=job_manifest(row)
    config.load_incluster_config()
    try:
        obj=client.CustomObjectsApi().get_namespaced_custom_object(
            group="ray.io",version="v1",namespace=namespace,plural="rayjobs",
            name=manifest["metadata"]["name"])
    except ApiException as exc:
        if exc.status == 404:
            return {"state":"not_found"}
        raise
    if obj.get("metadata",{}).get("labels") != manifest["metadata"]["labels"]:
        raise PermissionError("cross-tenant RayJob access denied")
    status=obj.get("status",{})
    return {"state":status.get("jobStatus","unknown"),
            "reason":status.get("reason",""),"job_name":manifest["metadata"]["name"]}
