"""Synthetic legacy ERP/MRO + QMS adapter. No real enterprise connectivity."""
from copy import deepcopy
from threading import RLock
from datetime import datetime, timezone
from uuid import uuid4

_LOCK = RLock()
ORDERS = {
 "RO-1001": {"repair_order_id": "RO-1001", "customer_ref": "SYNTH-CUST-A", "component": "turbine_blade", "status": "inspection"},
 "RO-1002": {"repair_order_id": "RO-1002", "customer_ref": "SYNTH-CUST-B", "component": "nozzle_guide_vane", "status": "inspection"},
}
INSPECTIONS = {
 "INSP-1001": {"inspection_id": "INSP-1001", "repair_order_id": "RO-1001", "image_ref": "synthetic://blade/1001", "status": "awaiting_review"},
 "INSP-1002": {"inspection_id": "INSP-1002", "repair_order_id": "RO-1002", "image_ref": "synthetic://vane/1002", "status": "awaiting_review"},
}
REVIEWS = []
PREDICTIONS = {}

def get_order(order_id):
    return deepcopy(ORDERS.get(order_id))

def get_inspection(inspection_id):
    return deepcopy(INSPECTIONS.get(inspection_id))

def record_prediction(inspection_id, prediction):
    with _LOCK:
        ref = str(uuid4())
        PREDICTIONS[ref] = {"inspection_id": inspection_id, **prediction}
        return ref

def record_review(inspection_id, prediction_id, reviewer, disposition, rationale):
    with _LOCK:
        if prediction_id not in PREDICTIONS or PREDICTIONS[prediction_id]["inspection_id"] != inspection_id:
            raise ValueError("prediction does not belong to inspection")
        if any(r["prediction_id"] == prediction_id for r in REVIEWS):
            raise ValueError("prediction already reviewed")
        event = {"event_id": str(uuid4()), "inspection_id": inspection_id, "prediction_id": prediction_id,
                 "reviewer": reviewer, "disposition": disposition, "rationale": rationale,
                 "recorded_at": datetime.now(timezone.utc).isoformat()}
        REVIEWS.append(event)
        return deepcopy(event)
