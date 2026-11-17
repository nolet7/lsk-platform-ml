"""Durable, bounded Kubernetes deployment reconciler.

Run as a separate single-purpose worker Deployment with scoped Kubernetes RBAC.
Every request is written to PostgreSQL before reconciliation. Worker retries
transient failures and prevents stale revisions from replacing newer ones.
"""
import logging
import os
import signal
import time
from mlplatform import controller
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
        return False
    actor = "ml-platform-reconciler"
    try:
        if db.has_newer_revision(job["tenant_id"], job["name"], job["environment"], job["revision"]):
            db.complete(job["tenant_id"], actor, job["id"], job["claim_token"], "superseded")
            return True
        controller.apply(job["tenant_id"], job["name"], job["environment"],
                         job["image"], job["replicas"], job["revision"])
        db.complete(job["tenant_id"], actor, job["id"], job["claim_token"], "submitted")
    except Exception:
        LOG.exception("reconciliation failed for id=%s", job["id"])
        db.retry(job["tenant_id"], actor, job["id"], job["claim_token"])
    return True

def main():
    logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
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
