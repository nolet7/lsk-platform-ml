"""Self-service ML deployment API: register -> independent approve -> deploy -> rollback.

The workload is an independently built OCI inference image implementing GET
/healthz, GET /readyz and POST /predict. The API itself never trains a model.
"""
import os
from fastapi import FastAPI, HTTPException, Depends
from app.security import auth, require_scope
from mlplatform.manifest import validate_image, target_namespace
from mlplatform.schemas import ModelRegistration, Approval, DeploymentRequest, RollbackRequest
from mlplatform.store import Store
from mlplatform.mlflow_gate import verify_evidence
from mlplatform import controller

app = FastAPI(title="LSK ML Deployment Platform", version="1.0.0")
store = Store()

def identity(claims: dict = Depends(auth)):
    if os.getenv("APP_ENV") != "production":
        raise HTTPException(503, "platform requires production OIDC")
    tenant = claims.get("tenant_id")
    actor = claims.get("sub")
    if not isinstance(tenant, str) or not isinstance(actor, str) or not actor:
        raise HTTPException(403, "OIDC tenant_id and subject are required")
    return {"tenant": tenant, "actor": actor, "claims": claims}

def check(ctx, scope):
    require_scope(ctx["claims"], scope)

@app.get("/healthz")
def health():
    return {"status": "up"}

@app.get("/readyz")
def ready():
    import psycopg
    try:
        with psycopg.connect(os.environ["DATABASE_URL"], connect_timeout=3) as conn:
            conn.execute("SELECT 1")
        return {"status": "ready"}
    except Exception as exc:
        raise HTTPException(503, "database unavailable") from exc

@app.post("/v1/platform/models", status_code=201)
def register(body: ModelRegistration, ctx: dict = Depends(identity)):
    check(ctx,"ml:register")
    try:
        validate_image(body.image)
        verify_evidence(ctx['tenant'],body)
        return store.register(ctx["tenant"],ctx["actor"],body)
    except ValueError as exc:
        raise HTTPException(422,str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(503,'MLflow verification unavailable') from exc
    except Exception as exc:
        if isinstance(exc, HTTPException): raise
        from psycopg.errors import UniqueViolation
        if isinstance(exc, UniqueViolation):
            raise HTTPException(409,"model version already registered") from exc
        raise

@app.post("/v1/platform/models/{model_id}/approve")
def approve(model_id: str, body: Approval, ctx: dict = Depends(identity)):
    check(ctx,"ml:approve")
    try:
        return store.approve(ctx["tenant"],ctx["actor"],model_id,body.reason)
    except LookupError as exc:
        raise HTTPException(404,str(exc)) from exc
    except PermissionError as exc:
        raise HTTPException(403,str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(409,str(exc)) from exc

@app.post("/v1/platform/deployments", status_code=202)
def deploy(body: DeploymentRequest, ctx: dict = Depends(identity)):
    check(ctx,"ml:deploy")
    try:
        namespace=target_namespace(ctx["tenant"],body.environment)
        row=store.prepare(ctx["tenant"],ctx["actor"],body.model_id,
                          body.name,body.environment,body.replicas,namespace)
        validate_image(row["image"])
    except LookupError as exc:
        raise HTTPException(404,str(exc)) from exc
    except PermissionError as exc:
        raise HTTPException(403,str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(422,str(exc)) from exc

    try:
        controller.apply(ctx["tenant"],body.name,body.environment,
                         row["image"],body.replicas,row["revision"])
    except Exception as exc:
        store.mark(ctx["tenant"],ctx["actor"],row["id"],"failed")
        raise HTTPException(502,"Kubernetes reconciliation failed; inspect internal logs") from exc
    store.mark(ctx["tenant"],ctx["actor"],row["id"],"submitted")
    return {"id":row["id"],"revision":row["revision"],"state":"submitted",
            "namespace":namespace,"note":"rollout health is not yet verified"}

@app.get("/v1/platform/deployments/{name}")
def status(name: str, environment: str, ctx: dict = Depends(identity)):
    check(ctx,"ml:read")
    if environment not in ("stage","production"):
        raise HTTPException(422,"invalid environment")
    try:
        return store.deployment(ctx["tenant"],name,environment)
    except LookupError as exc:
        raise HTTPException(404,str(exc)) from exc

@app.get("/v1/platform/deployments/{name}/history")
def history(name: str, environment: str, ctx: dict = Depends(identity)):
    check(ctx,"ml:read")
    if environment not in ("stage","production"):
        raise HTTPException(422,"invalid environment")
    return store.history(ctx["tenant"],name,environment)

@app.post("/v1/platform/deployments/{name}/rollback", status_code=202)
def rollback(name: str, environment: str, body: RollbackRequest,
             ctx: dict = Depends(identity)):
    check(ctx,"ml:rollback")
    if environment not in ("stage","production"):
        raise HTTPException(422,"invalid environment")
    rows=store.history(ctx["tenant"],name,environment)
    if len(rows)<2:
        raise HTTPException(409,"no previous revision to roll back to")
    target=rows[1]
    # Previous revision has a previously approved model_id; a rollback is a new auditable revision.
    try:
        namespace=target_namespace(ctx["tenant"],environment)
        row=store.prepare(ctx["tenant"],ctx["actor"],str(target["model_id"]),
                          name,environment,target["replicas"],namespace)
        controller.apply(ctx["tenant"],name,environment,row["image"],
                         row["replicas"],row["revision"])
    except Exception as exc:
        if "row" in locals():
            store.mark(ctx["tenant"],ctx["actor"],row["id"],"failed")
        raise HTTPException(502,"rollback reconciliation failed") from exc
    store.mark(ctx["tenant"],ctx["actor"],row["id"],"submitted")
    return {"id":row["id"],"revision":row["revision"],"rolled_back_to":target["revision"],
            "state":"submitted","reason":body.reason}
