import json
from fastapi.testclient import TestClient
from app.security import auth
from mlplatform.api import app
import mlplatform.api as api

def test_training_request_queued_with_tenant_scope(monkeypatch):
    monkeypatch.setenv("APP_ENV","production")
    monkeypatch.setenv("AWS_ACCOUNT_ID","123456789012")
    monkeypatch.setenv("AWS_REGION","us-east-1")
    monkeypatch.setenv("TRAINING_DATASET_BUCKET","lsk-datasets")
    monkeypatch.setenv("TENANT_NAMESPACE_MAP",
        json.dumps({"tenant-a":{"stage":"tenant-a-stage","production":"tenant-a-prod"}}))
    class Fake:
        def create_training(self,tenant,actor,body,namespace):
            assert tenant=="tenant-a" and namespace=="tenant-a-stage"
            return {"id":"test-job","state":"pending","namespace":namespace}
    monkeypatch.setattr(api,"store",Fake())
    app.dependency_overrides[auth]=lambda:{
        "sub":"ml-engineer","tenant_id":"tenant-a","scope":"ml:train ml:read"}
    client=TestClient(app)
    try:
        image="123456789012.dkr.ecr.us-east-1.amazonaws.com/model@sha256:"+"a"*64
        body={"name":"training","image":image,
              "dataset_uri":"s3://lsk-datasets/tenant-a/datasets/v1",
              "environment":"stage","workers":2,"gpu_per_worker":1}
        assert client.post("/v1/platform/training-jobs",json=body).status_code==202
        body["dataset_uri"]="s3://lsk-datasets/other/datasets/v1"
        assert client.post("/v1/platform/training-jobs",json=body).status_code==422
    finally:
        app.dependency_overrides.clear()
