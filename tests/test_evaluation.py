import json
import pytest
from ml.evaluate import evaluate

def test_reject_bad_model_and_accept_good(tmp_path):
    path = tmp_path / "report.json"
    path.write_text(json.dumps({"synthetic_test_auc": 0.7, "dataset_sha256": "abc", "test_count": 100}))
    with pytest.raises(ValueError):
        evaluate(str(path), 0.85)
    path.write_text(json.dumps({"synthetic_test_auc": 0.95, "dataset_sha256": "abc", "test_count": 100}))
    assert evaluate(str(path), 0.85)["approved_for_review"] is True
