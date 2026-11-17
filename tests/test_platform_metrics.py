from fastapi.testclient import TestClient
from mlplatform.api import app

def test_platform_metrics_export():
    response=TestClient(app).get("/healthz")
    assert response.status_code==200
    metrics=TestClient(app).get("/metrics")
    assert metrics.status_code==200
    assert "lsk_ml_platform_http_requests_total" in metrics.text
