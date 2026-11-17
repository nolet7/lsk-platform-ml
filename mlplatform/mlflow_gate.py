"""Fail-closed verification of MLflow training, evaluation and tenant lineage."""
import os
from urllib.parse import quote
import httpx

def verify_evidence(tenant: str, body) -> None:
    base = os.getenv("MLFLOW_TRACKING_URI", "").rstrip("/")
    token = os.getenv("MLFLOW_TRACKING_TOKEN", "")
    if not base.startswith("https://") or not token:
        raise RuntimeError("MLflow HTTPS tracking URI and access token must be configured")
    expected_artifact = f"runs:/{body.source_run_id}/model"
    if body.model_artifact_uri != expected_artifact:
        raise ValueError("model artifact must reference this verified MLflow run's model")
    url = f"{base}/api/2.0/mlflow/runs/get"
    with httpx.Client(timeout=httpx.Timeout(8.0), follow_redirects=False) as client:
        response = client.get(url, params={"run_id":body.source_run_id},
                              headers={"Authorization":f"Bearer {token}"})
        if response.status_code != 200:
            raise RuntimeError("MLflow run lookup failed")
        run = response.json().get("run", {})
    info = run.get("info", {})
    data = run.get("data", {})
    if info.get("run_id") != body.source_run_id or info.get("status") != "FINISHED":
        raise ValueError("MLflow run is missing or not FINISHED")
    tags = {m["key"]:m["value"] for m in data.get("tags",[]) if "key" in m and "value" in m}
    metrics = {m["key"]:m["value"] for m in data.get("metrics",[]) if "key" in m and "value" in m}
    if tags.get("tenant_id") != tenant or tags.get("evaluation_ref") != body.evaluation_reference:
        raise ValueError("MLflow tenant or evaluation reference mismatch")
    if tags.get("inference_image") != body.image:
        raise ValueError("MLflow run must attest exact immutable inference image")
    if not tags.get("dataset_sha256") or not tags.get("git_sha"):
        raise ValueError("MLflow dataset/code lineage tags are required")
    minimum = float(os.getenv("MODEL_MIN_VALIDATION_AUC","0.85"))
    if not 0 <= minimum <= 1:
        raise RuntimeError("invalid platform evaluation threshold")
    if not isinstance(metrics.get("validation_auc"), (int,float)) or not minimum <= metrics["validation_auc"] <= 1:
        raise ValueError("model evaluation threshold failed")
