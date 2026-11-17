from fastapi import HTTPException
from mlplatform import inference
import pytest

def test_revoked_model_denied_even_if_k8s_is_healthy(monkeypatch):
    monkeypatch.setenv("TENANT_NAMESPACE_MAP",'{"tenant-a":{"production":"tenant-a-prod"}}')
    monkeypatch.setattr(inference.controller,"observe",lambda *args,**kwargs:{"healthy":True})
    class Store:
        def deployment(self,*args):
            return {"id":"11111111-1111-4111-8111-111111111111","revision":1,
                    "image":"example","state":"submitted","revoked":True}
    with pytest.raises(HTTPException) as exc:
        inference.serve(Store(),"tenant-a","user","model","production",b'{"features":{}}')
    assert exc.value.status_code==403
