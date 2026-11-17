import os
from uuid import uuid4
import pytest
from mlplatform.training import validate_dataset,job_manifest

IMAGE="123456789012.dkr.ecr.us-east-1.amazonaws.com/approved-training@sha256:"+"a"*64

@pytest.fixture(autouse=True)
def setup(monkeypatch):
    monkeypatch.setenv("TRAINING_DATASET_BUCKET","lsk-datasets")
    monkeypatch.setenv("TENANT_NAMESPACE_MAP",
        '{"tenant-a":{"stage":"tenant-a-stage","production":"tenant-a-prod"}}')
    monkeypatch.setenv("AWS_REGION","us-east-1")
    monkeypatch.setenv("AWS_ACCOUNT_ID","123456789012")
    monkeypatch.setenv("RAY_RUNTIME_VERSION","2.52.0")
    monkeypatch.setenv("MLFLOW_TRACKING_URI","https://mlflow.example.net")

def row(gpu=0,uri="s3://lsk-datasets/tenant-a/datasets/version-1"):
    return {"id":str(uuid4()),"tenant_id":"tenant-a","environment":"stage",
            "name":"blade-quality","image":IMAGE,"dataset_uri":uri,"workers":2,"gpu_per_worker":gpu}

def test_cpu_rayjob_is_scoped_and_fixed_command():
    namespace,obj=job_manifest(row())
    assert namespace=="tenant-a-stage"
    assert obj["apiVersion"]=="ray.io/v1"
    assert obj["spec"]["entrypoint"]=="python -m lsk_training.entrypoint"
    assert obj["spec"]["shutdownAfterJobFinishes"] is True
    pod=obj["spec"]["rayClusterSpec"]["headGroupSpec"]["template"]["spec"]
    env={e["name"]:e for e in pod["containers"][0]["env"]}
    assert env["LSK_TENANT_ID"]["value"]=="tenant-a"
    assert env["LSK_EVALUATION_REF"]["value"]
    assert env["MLFLOW_TRACKING_TOKEN"]["valueFrom"]["secretKeyRef"]["name"]=="ml-training-mlflow"
    assert obj["spec"]["rayClusterSpec"]["workerGroupSpecs"][0]["replicas"]==2

def test_gpu_limits_and_node_placement():
    _,obj=job_manifest(row(gpu=1))
    worker=obj["spec"]["rayClusterSpec"]["workerGroupSpecs"][0]["template"]["spec"]
    assert worker["containers"][0]["resources"]["limits"]["nvidia.com/gpu"]=="1"
    assert worker["nodeSelector"]=={"lsk.ai/gpu":"true"}

def test_reject_cross_tenant_dataset():
    with pytest.raises(ValueError):
        job_manifest(row(uri="s3://lsk-datasets/tenant-b/datasets/v1"))
    with pytest.raises(ValueError):
        validate_dataset("tenant-a","s3://lsk-datasets/tenant-a/datasets/../secrets")
