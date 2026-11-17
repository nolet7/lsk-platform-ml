from pathlib import Path

def test_review_uniqueness_and_attribution():
    schema = Path("production/db/001_init.sql").read_text()
    assert "prediction_id UUID NOT NULL UNIQUE" in schema
    assert "REFERENCES predictions(prediction_id)" in schema
    assert "reviewer TEXT NOT NULL" in schema
