"""Synthetic aerospace repair inspection API; predictions are advisory only."""
import os
from fastapi import FastAPI, HTTPException, Header, Depends
from fastapi.responses import Response
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST
from app.contracts import PredictRequest, ReviewRequest
from app.legacy import get_order, get_inspection, record_prediction, record_review
from app.model import predict, ModelNotReady
from app.security import auth, require_scope
from app import persistence

app = FastAPI(title="LSK Aerospace Inspection ML", version="1.0.0")
requests_total = Counter("lsk_ml_requests_total", "ML inference request count", ["result"])

@app.get("/healthz")
def health():
    return {"status": "ok", "environment": os.getenv("APP_ENV", "local")}

@app.get("/readyz")
def ready():
    from pathlib import Path
    if not Path(os.getenv("MODEL_PATH", "artifacts/model.json")).is_file():
        raise HTTPException(503, "model artifact missing")
    if os.getenv("APP_ENV") == "production" and not all(
        os.getenv(k) for k in ("OIDC_ISSUER", "OIDC_AUDIENCE", "OIDC_JWKS_URL")
    ):
        raise HTTPException(503, "OIDC not configured")
    if os.getenv("APP_ENV") == "production":
        try:
            if not persistence.check_database():
                raise HTTPException(503, "database unavailable")
        except Exception as exc:
            raise HTTPException(503, "database unavailable") from exc
    return {"status": "ready"}

@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.get("/v1/repair-orders/{order_id}")
def order(order_id: str, claims: dict = Depends(auth)):
    require_scope(claims, "ml:read")
    result = get_order(order_id)
    if result is None:
        raise HTTPException(404, "repair order not found")
    return result

@app.get("/v1/inspections/{inspection_id}")
def inspection(inspection_id: str, claims: dict = Depends(auth)):
    require_scope(claims, "ml:read")
    result = get_inspection(inspection_id)
    if result is None:
        raise HTTPException(404, "inspection not found")
    return result

@app.post("/v1/predictions")
def infer(request: PredictRequest, claims: dict = Depends(auth)):
    require_scope(claims, "ml:predict")
    if not get_inspection(request.inspection_id):
        requests_total.labels("not_found").inc()
        raise HTTPException(404, "inspection not found")
    try:
        outcome = predict(request.signals)
    except ModelNotReady as exc:
        requests_total.labels("model_unavailable").inc()
        raise HTTPException(503, str(exc)) from exc
    prediction_id = (persistence.record_prediction(request.inspection_id, outcome)
                     if os.getenv('APP_ENV') == 'production'
                     else record_prediction(request.inspection_id, outcome))
    requests_total.labels("success").inc()
    return {"prediction_id": prediction_id, "inspection_id": request.inspection_id,
            **outcome, "notice": "Decision support only: authorized human disposition required"}

@app.post("/v1/reviews")
def review(request: ReviewRequest, claims: dict = Depends(auth),
           x_reviewer: str | None = Header(default=None)):
    require_scope(claims, "ml:review")
    if request.disposition not in ("accept_for_next_step", "hold_for_engineer", "reject_for_rework"):
        raise HTTPException(422, "invalid review disposition")
    # The untrusted X-Reviewer header is never accepted as identity in production.
    reviewer = str(claims.get("sub", "")) if os.getenv("APP_ENV") == "production" else x_reviewer
    if not reviewer or not reviewer.strip():
        raise HTTPException(403, "reviewer identity required")
    if not get_inspection(request.inspection_id):
        raise HTTPException(404, "inspection not found")
    try:
        fn = persistence.record_review if os.getenv('APP_ENV') == 'production' else record_review
        return fn(request.inspection_id, request.prediction_id,
                  reviewer, request.disposition, request.rationale)
    except ValueError as exc:
        raise HTTPException(409, str(exc)) from exc
