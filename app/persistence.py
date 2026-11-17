"""PostgreSQL-backed append-only synthetic prediction and review records."""
import os
from uuid import uuid4
import psycopg
from psycopg.rows import dict_row

def connection():
    url = os.getenv("DATABASE_URL")
    if not url:
        raise RuntimeError("DATABASE_URL is required in production")
    return psycopg.connect(url, connect_timeout=5, row_factory=dict_row)

def check_database():
    with connection() as conn, conn.cursor() as cur:
        cur.execute("SELECT 1")
        return cur.fetchone() is not None

def record_prediction(inspection_id, prediction):
    ref = str(uuid4())
    with connection() as conn, conn.cursor() as cur:
        cur.execute(
            "INSERT INTO predictions (prediction_id,inspection_id,model_version,dataset_sha256,probability,triage) VALUES (%s,%s,%s,%s,%s,%s)",
            (ref,inspection_id,prediction["model_version"],prediction["dataset_sha256"],prediction["defect_probability"],prediction["triage"]))
    return ref

def record_review(inspection_id,prediction_id,reviewer,disposition,rationale):
    ref = str(uuid4())
    with connection() as conn, conn.cursor() as cur:
        cur.execute(
            """INSERT INTO reviews (event_id,inspection_id,prediction_id,reviewer,disposition,rationale)
            SELECT %s,%s,prediction_id,%s,%s,%s FROM predictions
            WHERE prediction_id=%s AND inspection_id=%s
            ON CONFLICT (prediction_id) DO NOTHING
            RETURNING event_id,inspection_id,prediction_id,reviewer,disposition,rationale,recorded_at""",
            (ref,inspection_id,reviewer,disposition,rationale,prediction_id,inspection_id))
        row = cur.fetchone()
        if row is None:
            raise ValueError("prediction missing, mismatched or already reviewed")
        return dict(row)
