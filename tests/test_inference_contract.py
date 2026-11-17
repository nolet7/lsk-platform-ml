from pathlib import Path
from fastapi.testclient import TestClient
import pytest
from examples.sklearn_inference.inference import app
from ml.train import train

def test_serving_contract(tmp_path,monkeypatch):
    client=TestClient(app)
    monkeypatch.setenv("MODEL_PATH",str(tmp_path/"model.json"))
    assert client.get("/healthz").status_code==200
    assert client.get("/readyz").status_code==503
    train(tmp_path)
    assert client.get("/readyz").status_code==200
    response=client.post("/predict",json={"features":{
        "surface_texture":0.4,"edge_irregularity":0.3,"color_variance":0.8}})
    assert response.status_code==200
    assert 0<=response.json()["prediction"]["defect_probability"]<=1
    assert client.post("/predict",json={"features":{"surface_texture":5}}).status_code==422
