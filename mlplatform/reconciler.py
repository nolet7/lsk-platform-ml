"""Durable, bounded Kubernetes deployment reconciler.

Run as a separate single-purpose worker Deployment with scoped Kubernetes RBAC.
Every request is written to PostgreSQL before reconciliation. Worker retries
transient failures and prevents stale revisions from replacing newer ones.
"""
import logging
import os
import signal
import time
from mlplatform import controller, training
from prometheus_client import Counter, start_http_server

WORKER_OPERATIONS=Counter('lsk_ml_platform_worker_operations_total',
                          'Deployment and RayJob reconciliation results', ['type','result'])
from mlplatform.store import Store

LOG = logging.getLogger("mlplatform.reconciler")
running = True

def stop(*_):
    global running
    running = False

def run_once(store=None):
    db = store or Store()
    job = db.claim()
    if not job:
        return run_training_once(db)
    actor = "ml-platform-reconciler"
    try:
        if db.has_newer_revision(job["tenant_id"], job["name"], job["environment"], job["revision"]):
            db.complete(job["tenant_id"], actor, job["id"], job["claim_token"], "superseded")
            WORKER_OPERATIONS.labels("deployment","superseded").inc()
            return True
        controller.apply(job["tenant_id"], job["name"], job["environment"],
                         job["image"], job["replicas"], job["revision"])
        db.complete(job["tenant_id"], actor, job["id"], job["claim_token"], "submitted")
        WORKER_OPERATIONS.labels("deployment","submitted").inc()
    except Exception:
        LOG.exception("reconciliation failed for id=%s", job["id"])
        db.retry(job["tenant_id"], actor, job["id"], job["claim_token"])
        WORKER_OPERATIONS.labels("deployment","retry").inc()
    return True

def main():
    logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
    start_http_server(int(os.getenv("WORKER_METRICS_PORT","9100")),"0.0.0.0")
    signal.signal(signal.SIGTERM, stop)
    signal.signal(signal.SIGINT, stop)
    while running:
        try:
            if not run_once():
                time.sleep(float(os.getenv("RECONCILE_POLL_SECONDS", "3")))
        except Exception:
            LOG.exception("reconciler loop failure")
            time.sleep(5)

if __name__ == "__main__":
    main()

def run_training_once(db):
    job=db.claim_training()
    if not job:
        return False
    actor="ml-platform-reconciler"
    try:
        training.apply_training(job)
        db.finish_training(job["tenant_id"],actor,str(job["id"]),job["claim_token"],"submitted")
        WORKER_OPERATIONS.labels("rayjob","submitted").inc()
    except Exception:
        LOG.exception("RayJob reconciliation failed for id=%s",job["id"])
        db.retry_training(job["tenant_id"],actor,str(job["id"]),job["claim_token"])
        WORKER_OPERATIONS.labels("rayjob","retry").inc()
    return True
