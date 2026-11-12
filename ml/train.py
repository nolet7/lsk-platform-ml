"""Synthetic, seeded sample dataset -> reproducible sklearn training -> model JSON + report."""
import csv
import hashlib
import io
import json
from pathlib import Path
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import train_test_split

FEATURE_NAMES = ["surface_texture", "edge_irregularity", "color_variance"]

def build_dataset(seed=42, n=500):
    rng = np.random.default_rng(seed)
    x = rng.random((n, 3))
    score = 3 * x[:, 0] + 2.5 * x[:, 1] + 2 * x[:, 2] - 3.65 + rng.normal(0, 0.3, n)
    y = (score > 0).astype(int)
    buffer = io.StringIO()
    writer = csv.writer(buffer, lineterminator="\n")
    writer.writerow(FEATURE_NAMES + ["synthetic_defect_label"])
    for v, label in zip(x, y):
        writer.writerow([*(f"{p:.8f}" for p in v), int(label)])
    return x, y, buffer.getvalue()

def train(destination="artifacts", seed=42):
    x, y, data = build_dataset(seed=seed)
    digest = hashlib.sha256(data.encode()).hexdigest()
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=seed, stratify=y)
    classifier = LogisticRegression(max_iter=1000, random_state=seed).fit(x_train, y_train)
    auc = float(roc_auc_score(y_test, classifier.predict_proba(x_test)[:, 1]))
    directory = Path(destination)
    directory.mkdir(parents=True, exist_ok=True)
    (directory / "dataset.csv").write_text(data)
    model = {"version": f"synthetic-lr-seed-{seed}", "feature_names": FEATURE_NAMES,
             "weights": classifier.coef_[0].tolist(), "intercept": float(classifier.intercept_[0]), "dataset_sha256": digest}
    (directory / "model.json").write_text(json.dumps(model, indent=2) + "\n")
    report = {"synthetic_test_auc": auc, "train_count": len(x_train), "test_count": len(x_test),
              "seed": seed, "dataset_sha256": digest, "warning": "Synthetic labels are not aerospace validation."}
    (directory / "report.json").write_text(json.dumps(report, indent=2) + "\n")
    return report

if __name__ == "__main__":
    print(json.dumps(train(), indent=2))
