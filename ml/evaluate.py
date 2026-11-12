"""Evaluation CLI; fails closed if a report/metric does not meet the declared gate."""
import argparse
import json
from pathlib import Path

def evaluate(report_path: str, min_auc: float = 0.85):
    report = json.loads(Path(report_path).read_text())
    auc = report.get("synthetic_test_auc")
    if not isinstance(auc, (float, int)) or not (min_auc <= auc <= 1):
        raise ValueError(f"evaluation gate failed: auc={auc!r} threshold={min_auc}")
    if not report.get("dataset_sha256") or report.get("test_count", 0) < 10:
        raise ValueError("evaluation report missing lineage or adequate test set")
    return {"approved_for_review": True, "auc": auc, "dataset_sha256": report["dataset_sha256"]}

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", default="artifacts/report.json")
    parser.add_argument("--min-auc", type=float, default=0.85)
    args = parser.parse_args()
    print(json.dumps(evaluate(args.report, args.min_auc)))
