"""Example model-serving HTTP interface compatible with LSK ML Platform."""
import os
from pathlib import Path
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from app.contracts import Signals
from app.model import predict, ModelNotReady

app=FastAPI(title="LSK Generic Model Serving Example",version="1.0.0")

class PredictPayload(BaseModel):
    features: Signals

@app.get("/healthz")
def live():
    return {"status":"up"}

@app.get("/readyz")
def ready():
    if not Path(os.getenv("MODEL_PATH","artifacts/model.json")).is_file():
        raise HTTPException(503,"model artifact missing")
    return {"status":"ready"}

@app.post("/predict")
def infer(payload: PredictPayload):
    try:
        result=predict(payload.features)
    except ModelNotReady as exc:
        raise HTTPException(503,str(exc)) from exc
    return {"prediction":result,"disclaimer":"Demonstration only; human review required for aerospace disposition"}
