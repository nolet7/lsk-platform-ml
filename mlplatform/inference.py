"""Tenant-isolated inference gateway to approved Kubernetes inference services.

The service address is built entirely from validated model names and a trusted
server-side namespace map. Callers cannot provide arbitrary destination URLs.
Prediction payloads are not written to audit records.
"""
import json
import re
import time
from uuid import UUID

import httpx
from fastapi import HTTPException
from mlplatform.manifest import target_namespace, resource_name
from mlplatform import controller

MAX_REQUEST_BYTES=65536
MAX_RESPONSE_BYTES=262144

def service_url(tenant,name,environment):
    namespace=target_namespace(tenant,environment)
    service=resource_name(name)
    return f"http://{service}.{namespace}.svc.cluster.local/predict"

def serve(store,tenant,actor,name,environment,raw_body):
    if environment not in ("stage","production"):
        raise HTTPException(422,"unsupported model environment")
    if len(raw_body)>MAX_REQUEST_BYTES:
        raise HTTPException(413,"prediction request exceeds payload limit")
    try:
        payload=json.loads(raw_body)
    except (json.JSONDecodeError,UnicodeDecodeError) as exc:
        raise HTTPException(422,"invalid JSON prediction payload") from exc
    if not isinstance(payload,dict):
        raise HTTPException(422,"prediction payload must be a JSON object")
    try:
        deployment=store.deployment(tenant,name,environment)
        observed=controller.observe(tenant,name,environment,
            expected_image=deployment["image"],expected_revision=deployment["revision"])
    except LookupError as exc:
        raise HTTPException(404,"model deployment not found") from exc
    except ValueError as exc:
        raise HTTPException(422,"invalid tenant/model routing") from exc
    except Exception as exc:
        raise HTTPException(503,"deployment health verification unavailable") from exc
    if deployment.get("revoked"):
        raise HTTPException(403,"model revision has been revoked")
    if deployment["state"]!="submitted" or not observed.get("healthy"):
        raise HTTPException(503,"requested model revision is not healthy")
    url=service_url(tenant,name,environment)
    start=time.monotonic()
    status=502
    result=None
    try:
        with httpx.Client(timeout=httpx.Timeout(10),follow_redirects=False,
                          trust_env=False) as client:
            response=client.post(url,json=payload)
        if len(response.content)>MAX_RESPONSE_BYTES:
            raise HTTPException(502,"upstream response exceeds limit")
        if response.status_code!=200:
            raise HTTPException(502,"inference upstream rejected request")
        if "application/json" not in response.headers.get("content-type",""):
            raise HTTPException(502,"inference upstream response is not JSON")
        result=response.json()
        if not isinstance(result,dict):
            raise HTTPException(502,"inference upstream returned invalid payload")
        status=200
    except httpx.RequestError as exc:
        raise HTTPException(502,"inference upstream unavailable") from exc
    finally:
        latency=round((time.monotonic()-start)*1000,2)
        # Keep only principal, model/version, status and latency. Never input/output.
        store.record_inference(tenant,actor,deployment["id"],status,latency)
    return {"deployment_id":str(deployment["id"]),
            "revision":deployment["revision"],"result":result}
