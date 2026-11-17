"""PostgreSQL model registry, approval and deployment revision store.

Enforces tenant in each SQL predicate. No client-supplied tenant or namespace.
Rollout status is recorded as submitted until separately reconciled/observed.
"""
import os
from uuid import uuid4

import psycopg
from psycopg.rows import dict_row

def connect():
    return psycopg.connect(os.environ["DATABASE_URL"], connect_timeout=5, row_factory=dict_row)

class Store:
    def register(self, tenant, actor, body):
        model_id = str(uuid4())
        with connect() as conn, conn.cursor() as cur:
            cur.execute(
                """INSERT INTO platform_models
                    (id,tenant_id,name,model_version,image,evaluation_reference,source_run_id,model_artifact_uri,created_by)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                (model_id,tenant,body.name,body.version,body.image,
                 body.evaluation_reference,body.source_run_id,body.model_artifact_uri,actor))
            cur.execute("INSERT INTO platform_audit (tenant_id,actor,event,resource_id) VALUES (%s,%s,%s,%s)",
                        (tenant,actor,"model_registered",model_id))
        return {"id": model_id, "tenant": tenant, "state": "pending_review"}

    def approve(self, tenant, actor, model_id, reason):
        with connect() as conn, conn.cursor() as cur:
            cur.execute(
                "SELECT created_by,approved_by FROM platform_models WHERE tenant_id=%s AND id=%s FOR UPDATE",
                (tenant,model_id))
            row = cur.fetchone()
            if not row:
                raise LookupError("model not found")
            if row["created_by"] == actor:
                raise PermissionError("submitter cannot approve own model")
            if row["approved_by"]:
                raise ValueError("model already approved")
            cur.execute(
                "UPDATE platform_models SET approved_by=%s, approval_reason=%s,approved_at=now() WHERE tenant_id=%s AND id=%s",
                (actor,reason,tenant,model_id))
            cur.execute("INSERT INTO platform_audit (tenant_id,actor,event,resource_id) VALUES (%s,%s,%s,%s)",
                        (tenant,actor,"model_approved",model_id))
        return {"id": model_id, "state": "approved"}

    def deployment(self, tenant, name, environment):
        with connect() as conn, conn.cursor() as cur:
            cur.execute(
                """SELECT id,model_id,revision,image,replicas,state,namespace
                   FROM platform_deployments WHERE tenant_id=%s AND name=%s AND environment=%s
                   ORDER BY revision DESC LIMIT 1""",
                (tenant,name,environment))
            row=cur.fetchone()
        if not row:
            raise LookupError("deployment not found")
        return dict(row)

    def history(self, tenant, name, environment):
        with connect() as conn, conn.cursor() as cur:
            cur.execute(
                """SELECT id,model_id,revision,image,replicas,state,namespace
                   FROM platform_deployments WHERE tenant_id=%s AND name=%s AND environment=%s
                   ORDER BY revision DESC LIMIT 20""",
                (tenant,name,environment))
            return [dict(r) for r in cur.fetchall()]

    def prepare(self, tenant, actor, model_id, name, environment, replicas, namespace):
        deployment_id = str(uuid4())
        # Advisory transaction lock serializes revisions for a tenant/name/env.
        lock_key = "|".join((tenant,name,environment))
        with connect() as conn, conn.cursor() as cur:
            cur.execute("SELECT pg_advisory_xact_lock(hashtextextended(%s,0))", (lock_key,))
            cur.execute(
                """SELECT image,approved_by FROM platform_models
                   WHERE tenant_id=%s AND id=%s FOR SHARE""", (tenant,model_id))
            model = cur.fetchone()
            if not model:
                raise LookupError("model not found")
            if not model["approved_by"]:
                raise PermissionError("model approval required before deployment")
            cur.execute(
                """SELECT COALESCE(MAX(revision),0)+1 AS revision FROM platform_deployments
                   WHERE tenant_id=%s AND name=%s AND environment=%s""",
                (tenant,name,environment))
            revision=cur.fetchone()["revision"]
            cur.execute(
                """INSERT INTO platform_deployments
                   (id,tenant_id,name,environment,revision,model_id,image,replicas,namespace,state,requested_by)
                   VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,'pending',%s)""",
                (deployment_id,tenant,name,environment,revision,model_id,model["image"],
                 replicas,namespace,actor))
            cur.execute("INSERT INTO platform_audit (tenant_id,actor,event,resource_id) VALUES (%s,%s,%s,%s)",
                        (tenant,actor,"deployment_requested",deployment_id))
        return {"id":deployment_id,"model_id":model_id,"revision":revision,
                "image":model["image"],"replicas":replicas,"namespace":namespace}

    def mark(self, tenant, actor, deployment_id, state):
        with connect() as conn, conn.cursor() as cur:
            cur.execute("UPDATE platform_deployments SET state=%s,updated_at=now() WHERE tenant_id=%s AND id=%s",
                        (state,tenant,deployment_id))
            cur.execute("INSERT INTO platform_audit (tenant_id,actor,event,resource_id) VALUES (%s,%s,%s,%s)",
                        (tenant,actor,"deployment_"+state,deployment_id))
