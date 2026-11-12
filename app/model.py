"""Load a reproducible CPU logistic-regression model exported as simple JSON."""
import json
import math
import os
from pathlib import Path

FEATURES = ("surface_texture", "edge_irregularity", "color_variance")

class ModelNotReady(RuntimeError):
    pass

def predict(signals):
    path = Path(os.getenv("MODEL_PATH", "artifacts/model.json"))
    if not path.is_file():
        raise ModelNotReady("train a model first: python -m ml.train")
    model = json.loads(path.read_text())
    if model.get("feature_names") != list(FEATURES) or len(model.get("weights", [])) != len(FEATURES):
        raise ModelNotReady("model artifact schema mismatch")
    logit = model["intercept"] + sum(w * float(getattr(signals, f)) for f, w in zip(FEATURES, model["weights"]))
    prob = 1 / (1 + math.exp(-max(-80, min(80, logit))))
    return {"defect_probability": round(prob, 6), "triage": "manual_review_priority" if prob >= 0.5 else "routine_manual_review",
            "model_version": model["version"], "dataset_sha256": model["dataset_sha256"]}
