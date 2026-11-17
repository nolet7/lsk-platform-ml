import json
import pytest
from fastapi import HTTPException
from mlplatform import inference

class FakeStore:
    def __init__(self):self.events=[]
    def deployment(self,tenant,name,env):
        assert tenant=="tenant-a"
        return {"id":"11111111-1111-4111-8111-111111111111",
                "image":"image-a","revision":3,"state":"submitted"}
    def record_inference(self,tenant,actor,deployment_id,status,latency):
        self.events.append((tenant,status,latency))

def test_url_is_derived_from_tenant_mapping(monkeypatch):
    monkeypatch.setenv("TENANT_NAMESPACE_MAP",'{"tenant-a":{"production":"tenant-a-prod"}}')
    assert inference.service_url("tenant-a","model-a","production")==(
        "http://ml-model-a.tenant-a-prod.svc.cluster.local/predict")
    with pytest.raises(ValueError):
        inference.service_url("tenant-b","model-a","production")

def test_gateway_blocks_unhealthy_revision(monkeypatch):
    monkeypatch.setattr(inference.controller,"observe",lambda *a,**k:{"healthy":False})
    with pytest.raises(HTTPException) as exc:
        inference.serve(FakeStore(),"tenant-a","actor","model-a","production",b'{"features":{}}')
    assert exc.value.status_code==503

def test_gateway_forwards_only_approved_route(monkeypatch):
    import httpx
    monkeypatch.setenv("TENANT_NAMESPACE_MAP",'{"tenant-a":{"production":"tenant-a-prod"}}')
    monkeypatch.setattr(inference.controller,"observe",lambda *a,**k:{"healthy":True})
    calls=[]
    class Client:
        def __init__(self,**kwargs):
            assert kwargs["trust_env"] is False
            assert kwargs["follow_redirects"] is False
        def __enter__(self):return self
        def __exit__(self,*args):pass
        def post(self,url,json):
            calls.append((url,json))
            return httpx.Response(200,headers={"content-type":"application/json"},
                                  json={"prediction":0.2},request=httpx.Request("POST",url))
    monkeypatch.setattr(inference.httpx,"Client",Client)
    store=FakeStore()
    result=inference.serve(store,"tenant-a","actor","model-a","production",
                           b'{"features":{"x":1}}')
    assert result["result"]["prediction"]==0.2
    assert calls[0][0]=="http://ml-model-a.tenant-a-prod.svc.cluster.local/predict"
    assert store.events[0][0:2]==("tenant-a",200)

def test_gateway_input_limit():
    with pytest.raises(HTTPException) as exc:
        inference.serve(FakeStore(),"tenant-a","actor","model","production",
                        b"x"*(inference.MAX_REQUEST_BYTES+1))
    assert exc.value.status_code==413
