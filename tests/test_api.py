import pytest
from fastapi.testclient import TestClient
from app.main import app
from app import legacy
from ml.train import train

client = TestClient(app)
AUTH = {"X-Demo-Key": "local-demo-key"}

def test_legacy_auth_and_lookup():
    assert client.get("/v1/repair-orders/RO-1001").status_code == 401
    assert client.get("/v1/repair-orders/RO-1001", headers=AUTH).status_code == 200
    assert client.get("/v1/repair-orders/none", headers=AUTH).status_code == 404

def test_training_reproducibility(tmp_path):
    a, b = tmp_path / "a", tmp_path / "b"
    assert train(a)["dataset_sha256"] == train(b)["dataset_sha256"]
    assert (a / "model.json").read_bytes() == (b / "model.json").read_bytes()

def test_inference_requires_human_disposition(tmp_path, monkeypatch):
    train(tmp_path)
    monkeypatch.setenv("MODEL_PATH", str(tmp_path / "model.json"))
    old_reviews = len(legacy.REVIEWS)
    request = {"inspection_id": "INSP-1001", "signals": {"surface_texture": 0.8, "edge_irregularity": 0.7, "color_variance": 0.8}}
    prediction = client.post("/v1/predictions", json=request, headers=AUTH)
    assert prediction.status_code == 200
    assert len(legacy.REVIEWS) == old_reviews  # model never decides release
    assert prediction.json()["model_version"]
    event = {"inspection_id": "INSP-1001", "prediction_id": prediction.json()["prediction_id"],
             "disposition": "hold_for_engineer", "rationale": "Inspect anomalies before disposition"}
    assert client.post("/v1/reviews", json=event, headers=AUTH).status_code == 403
    approved = client.post("/v1/reviews", json=event, headers={**AUTH, "X-Reviewer": "synthetic-inspector"})
    assert approved.status_code == 200
    assert len(legacy.REVIEWS) == old_reviews + 1
    assert client.post("/v1/reviews", json=event, headers={**AUTH, "X-Reviewer": "synthetic-inspector"}).status_code == 409

def test_invalid_or_missing_inspection():
    body = {"inspection_id": "missing", "signals": {"surface_texture": 0.5, "edge_irregularity": 0.2, "color_variance": 0.3}}
    assert client.post("/v1/predictions", json=body, headers=AUTH).status_code == 404
    body["signals"]["surface_texture"] = 10
    assert client.post("/v1/predictions", json=body, headers=AUTH).status_code == 422

def test_health_metrics():
    assert client.get("/healthz").json()["status"] == "ok"
    assert "lsk_ml_requests_total" in client.get("/metrics").text
