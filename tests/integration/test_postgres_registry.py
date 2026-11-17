"""Real PostgreSQL registry + work-queue contract test; CI uses an ephemeral DB."""
import os
from uuid import uuid4
from types import SimpleNamespace

import psycopg
import pytest

from mlplatform.store import Store

pytestmark=pytest.mark.skipif(not os.getenv("DATABASE_URL_TEST"),reason="requires isolated PostgreSQL CI service")

def test_model_registration_approval_queue_and_reconcile(monkeypatch):
    dsn=os.environ["DATABASE_URL_TEST"]
    monkeypatch.setenv("DATABASE_URL",dsn)
    tenant="integration-"+uuid4().hex[:12]
    model=SimpleNamespace(name="model-example",version="v1",image="immutable-test-image",
        evaluation_reference="integration-eval-1",source_run_id="test-run",
        model_artifact_uri="runs:/test-run/model")
    store=Store()
    try:
        row=store.register(tenant,"builder",model)
        mid=row["id"]
        with pytest.raises(PermissionError):
            store.approve(tenant,"builder",mid,"self approval must not succeed")
        store.approve(tenant,"quality-reviewer",mid,"Valid synthetic integration review")
        with pytest.raises(ValueError):
            store.prepare(tenant,"deployer",mid,"wrong-name","stage",2,"tenant-stage")
        new=store.prepare(tenant,"deployer",mid,model.name,"stage",2,"tenant-stage")
        assert new["revision"]==1
        assert not store.has_newer_revision(tenant,model.name,"stage",1)
        claimed=store.claim()
        assert str(claimed["id"])==new["id"]
        assert claimed["claim_token"]
        store.retry(tenant,"worker",str(claimed["id"]),claimed["claim_token"])
        with psycopg.connect(dsn) as conn,conn.cursor() as cur:
            cur.execute("UPDATE platform_deployments SET next_attempt_at=now() WHERE id=%s",(new["id"],))
        again=store.claim()
        assert str(again["id"])==new["id"]
        store.complete(tenant,"worker",new["id"],again["claim_token"],"submitted")
        latest=store.deployment(tenant,model.name,"stage")
        assert latest["state"]=="submitted"
        second=store.prepare(tenant,"deployer",mid,model.name,"stage",2,"tenant-stage")
        assert second["revision"]==2
        assert store.has_newer_revision(tenant,model.name,"stage",1)
        assert len(store.history(tenant,model.name,"stage"))==2
    finally:
        with psycopg.connect(dsn) as conn,conn.cursor() as cur:
            cur.execute("DELETE FROM platform_audit WHERE tenant_id=%s",(tenant,))
            cur.execute("DELETE FROM platform_deployments WHERE tenant_id=%s",(tenant,))
            cur.execute("DELETE FROM platform_models WHERE tenant_id=%s",(tenant,))
