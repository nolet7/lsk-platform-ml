import os
from types import SimpleNamespace
import httpx
import pytest
from mlplatform.mlflow_gate import verify_evidence

def test_mlflow_gate_verifies_signed_metadata(monkeypatch):
    monkeypatch.setenv("MLFLOW_TRACKING_URI","https://mlflow.example.net")
    monkeypatch.setenv("MLFLOW_TRACKING_TOKEN","test-token")
    monkeypatch.setenv("MODEL_EVALUATION_POLICIES",'{"tenant-a":{"blade-quality":{"metric":"validation_auc","operator":"gte","threshold":0.85}}}')
    run="abcd1234"
    body=SimpleNamespace(name="blade-quality",source_run_id=run,model_artifact_uri=f"runs:/{run}/model",
                         evaluation_reference="eval-456",image="oci-image-digest")
    payload={"run":{"info":{"run_id":run,"status":"FINISHED"},
        "data":{"metrics":[{"key":"validation_auc","value":0.91}],
        "tags":[{"key":"tenant_id","value":"tenant-a"},
                {"key":"evaluation_ref","value":"eval-456"},
                {"key":"inference_image","value":"oci-image-digest"},
                {"key":"dataset_sha256","value":"a"*64},
                {"key":"git_sha","value":"f"*40}]}}}
    class FakeClient:
        def __init__(self, **kwargs): pass
        def __enter__(self): return self
        def __exit__(self,*args): pass
        def get(self,url,**kwargs):
            return httpx.Response(200,json=payload,request=httpx.Request("GET",url))
    monkeypatch.setattr("mlplatform.mlflow_gate.httpx.Client",FakeClient)
    verify_evidence("tenant-a",body)
    payload["run"]["data"]["metrics"][0]["value"]=0.30
    with pytest.raises(ValueError):
        verify_evidence("tenant-a",body)
    payload["run"]["data"]["metrics"][0]["value"]=0.91
    payload["run"]["data"]["tags"][0]["value"]="tenant-b"
    with pytest.raises(ValueError):
        verify_evidence("tenant-a",body)

def test_requires_mlflow_configuration(monkeypatch):
    monkeypatch.delenv("MLFLOW_TRACKING_URI",raising=False)
    monkeypatch.delenv("MLFLOW_TRACKING_TOKEN",raising=False)
    with pytest.raises(RuntimeError):
        verify_evidence("tenant-a",SimpleNamespace())
