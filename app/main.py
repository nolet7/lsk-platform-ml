"""Legacy-first aerospace repair ML POC: predictions never decide part disposition."""
import os
from fastapi import FastAPI, HTTPException, Header, Depends
from fastapi.responses import Response
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST
from app.contracts import PredictRequest, ReviewRequest
from app.legacy import get_order, get_inspection, record_prediction, record_review
from app.model import predict, ModelNotReady

app = FastAPI(title="LSK Aerospace Inspection ML POC", version="0.1.0")
requests_total = Counter("lsk_ml_requests_total", "ML inference request count", ["result"])

def auth(x_demo_key: str | None = Header(default=None)):
    # Deliberately local-only simulation. Pilot must replace with OIDC and scoped authorization.
    if x_demo_key != os.getenv("DEMO_API_KEY", "local-demo-key"):
        raise HTTPException(401, "invalid demo key")

@app.get("/healthz")
def health():
    return {"status": "ok", "phase": "poc"}

@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.get("/v1/repair-orders/{order_id}", dependencies=[Depends(auth)])
def order(order_id: str):
    result = get_order(order_id)
    if result is None:
        raise HTTPException(404, "repair order not found")
    return result

@app.get("/v1/inspections/{inspection_id}", dependencies=[Depends(auth)])
def inspection(inspection_id: str):
    result = get_inspection(inspection_id)
    if result is None:
        raise HTTPException(404, "inspection not found")
    return result

@app.post("/v1/predictions", dependencies=[Depends(auth)])
def infer(request: PredictRequest):
    if not get_inspection(request.inspection_id):
        requests_total.labels("not_found").inc()
        raise HTTPException(404, "inspection not found")
    try:
        outcome = predict(request.signals)
    except ModelNotReady as exc:
        requests_total.labels("model_unavailable").inc()
        raise HTTPException(503, str(exc)) from exc
    prediction_id = record_prediction(request.inspection_id, outcome)
    requests_total.labels("success").inc()
    return {"prediction_id": prediction_id, "inspection_id": request.inspection_id, **outcome,
            "notice": "Decision support only: authorized human disposition required"}

@app.post("/v1/reviews", dependencies=[Depends(auth)])
def review(request: ReviewRequest, x_reviewer: str | None = Header(default=None)):
    if request.disposition not in ("accept_for_next_step", "hold_for_engineer", "reject_for_rework"):
        raise HTTPException(422, "invalid review disposition")
    if not x_reviewer or not x_reviewer.strip():
        raise HTTPException(403, "reviewer identity required")
    if not get_inspection(request.inspection_id):
        raise HTTPException(404, "inspection not found")
    try:
        return record_review(request.inspection_id, request.prediction_id, x_reviewer, request.disposition, request.rationale)
    except ValueError as exc:
        raise HTTPException(409, str(exc)) from exc
