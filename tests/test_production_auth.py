import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_production_rejects_demo_key(monkeypatch):
    monkeypatch.setenv("APP_ENV", "production")
    r = client.get("/v1/repair-orders/RO-1001", headers={"X-Demo-Key": "local-demo-key"})
    assert r.status_code in (401, 503)
    assert r.status_code != 200

def test_production_requires_real_oidc_config(monkeypatch):
    monkeypatch.setenv("APP_ENV", "production")
    for name in ("OIDC_ISSUER", "OIDC_AUDIENCE", "OIDC_JWKS_URL"):
        monkeypatch.delenv(name, raising=False)
    assert client.get("/readyz").status_code == 503

def test_readiness_local_missing_model(monkeypatch, tmp_path):
    monkeypatch.setenv("APP_ENV", "local")
    monkeypatch.setenv("MODEL_PATH", str(tmp_path / "missing.json"))
    assert client.get("/readyz").status_code == 503

def test_jwt_bad_signature_denied(monkeypatch):
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("OIDC_ISSUER", "https://issuer.example.net")
    monkeypatch.setenv("OIDC_AUDIENCE", "lsk-platform-api")
    monkeypatch.setenv("OIDC_JWKS_URL", "https://issuer.example.net/.well-known/jwks.json")
    assert client.get("/v1/repair-orders/RO-1001",
          headers={"Authorization": "Bearer malformed"}).status_code == 401
