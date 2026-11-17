import json
from fastapi.testclient import TestClient
from app.security import auth
from mlplatform.api import app, identity
import mlplatform.api as api

class FakeStore:
    def __init__(self):
        self.calls=[]
    def register(self,tenant,actor,body):
        self.calls.append(("register",tenant,actor))
        return {"id":"m1","state":"pending_review"}
    def approve(self,tenant,actor,model_id,reason):
        self.calls.append(("approve",tenant,actor))
        return {"id":model_id,"state":"approved"}
    def prepare(self,tenant,actor,model_id,name,env,replicas,namespace):
        self.calls.append(("prepare",tenant,namespace))
        return {"id":"d1","revision":1,"image":IMAGE,"replicas":replicas,"namespace":namespace}
    def mark(self,tenant,actor,id,state):
        self.calls.append(("mark",state))
    def revoke(self,tenant,actor,model_id,reason):
        self.calls.append(("revoke",tenant,model_id))
        return {"id":model_id,"state":"revoked"}
    def deployment(self,tenant,name,environment):
        return {"id":"d1","state":"submitted","tenant_id":tenant,"image":IMAGE,"revision":1}
    def history(self,tenant,name,environment):
        return []

IMAGE="123456789012.dkr.ecr.us-east-1.amazonaws.com/ml-model@sha256:"+"b"*64

def test_platform_registration_approval_and_deploy(monkeypatch):
    monkeypatch.setenv("APP_ENV","production")
    monkeypatch.setenv("AWS_ACCOUNT_ID","123456789012")
    monkeypatch.setenv("AWS_REGION","us-east-1")
    monkeypatch.setenv("TENANT_NAMESPACE_MAP",json.dumps({"tenant-a":{"stage":"a-stage","production":"a-prod"}}))
    fake=FakeStore()
    monkeypatch.setattr(api,"store",fake)
    monkeypatch.setattr(api,"verify_evidence",lambda tenant, body: None)
    monkeypatch.setattr(api.controller,"apply",lambda *args:{"state":"submitted"})
    monkeypatch.setattr(api.controller,"observe",lambda *args, **kwargs:{"healthy":True,"state":"healthy"})
    app.dependency_overrides[auth]=lambda:{"sub":"engineer","tenant_id":"tenant-a","scope":"ml:register ml:approve ml:deploy ml:read ml:rollback ml:revoke"}
    client=TestClient(app)
    try:
        body={"name":"blade-quality","version":"v1","image":IMAGE,
              "evaluation_reference":"approved-eval-123","source_run_id":"run-1","model_artifact_uri":"models:/blade/1"}
        assert client.post("/v1/platform/models",json=body).status_code==201
        assert client.post("/v1/platform/models/m1/approve",json={"reason":"Quality and platform review complete"}).status_code==200
        assert client.post("/v1/platform/models/m1/revoke",json={"reason":"Model failed quality audit; revoke approval"}).status_code==200
        response=client.post("/v1/platform/deployments",
                             json={"name":"blade-quality","model_id":"m1","environment":"production","replicas":3})
        assert response.status_code==202
        assert response.json()["state"]=="pending"
        assert ("prepare","tenant-a","a-prod") in fake.calls
        assert client.get("/v1/platform/deployments/blade-quality?environment=production").status_code==200
    finally:
        app.dependency_overrides.clear()

def test_no_demo_key_bypass(monkeypatch):
    monkeypatch.setenv("APP_ENV","production")
    app.dependency_overrides.clear()
    response=TestClient(app).get("/v1/platform/deployments/x?environment=production",
                                headers={"X-Demo-Key":"local-demo-key"})
    assert response.status_code in (401,503)
