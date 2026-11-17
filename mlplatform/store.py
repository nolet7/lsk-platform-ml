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
                """SELECT image,name,approved_by FROM platform_models
                   WHERE tenant_id=%s AND id=%s FOR SHARE""", (tenant,model_id))
            model = cur.fetchone()
            if not model:
                raise LookupError("model not found")
            if not model["approved_by"]:
                raise PermissionError("model approval required before deployment")
            if model["name"] != name:
                raise ValueError("deployment name must match registered model name")
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

    def claim(self):
        """Atomically lease the oldest runnable job. Claim token fences stale workers."""
        with connect() as conn, conn.cursor() as cur:
            cur.execute("""
              WITH candidate AS (
                SELECT id FROM platform_deployments
                WHERE ((state IN ('pending','retry') AND next_attempt_at <= now())
                    OR (state = 'reconciling' AND lease_until < now()))
                ORDER BY created_at, id FOR UPDATE SKIP LOCKED LIMIT 1
              )
              UPDATE platform_deployments AS d SET state='reconciling',
                lease_until=now()+interval '5 minutes',
                claim_token=gen_random_uuid(),updated_at=now()
              FROM candidate WHERE d.id=candidate.id
              RETURNING d.id,d.tenant_id,d.name,d.environment,d.revision,d.image,
                        d.replicas,d.claim_token
            """)
            row=cur.fetchone()
            return dict(row) if row else None

    def has_newer_revision(self, tenant, name, environment, revision):
        with connect() as conn, conn.cursor() as cur:
            cur.execute("""SELECT EXISTS(SELECT 1 FROM platform_deployments
                         WHERE tenant_id=%s AND name=%s AND environment=%s
                           AND revision>%s AND state IN
                              ('pending','retry','reconciling','submitted')) AS newer""",
                        (tenant,name,environment,revision))
            return cur.fetchone()["newer"]

    def complete(self, tenant, actor, deployment_id, claim_token, state):
        if state not in ("submitted","superseded"):
            raise ValueError("invalid terminal reconciliation state")
        with connect() as conn, conn.cursor() as cur:
            cur.execute("""UPDATE platform_deployments
                SET state=%s,lease_until=NULL,claim_token=NULL,updated_at=now()
                WHERE id=%s AND tenant_id=%s AND state='reconciling'
                  AND claim_token=%s RETURNING id""",
                (state,deployment_id,tenant,claim_token))
            if not cur.fetchone():
                raise RuntimeError("reconciliation lease expired or moved")
            cur.execute("""INSERT INTO platform_audit (tenant_id,actor,event,resource_id)
                           VALUES (%s,%s,%s,%s)""",
                        (tenant,actor,"deployment_"+state,deployment_id))

    def retry(self, tenant, actor, deployment_id, claim_token):
        with connect() as conn, conn.cursor() as cur:
            cur.execute("""UPDATE platform_deployments
                SET retry_count=retry_count+1,
                    state=CASE WHEN retry_count+1>=5 THEN 'failed' ELSE 'retry' END,
                    next_attempt_at=now()+(make_interval(secs=>LEAST(300,POWER(2,retry_count+1)::integer*5))),
                    lease_until=NULL,claim_token=NULL,updated_at=now()
                WHERE id=%s AND tenant_id=%s AND state='reconciling'
                  AND claim_token=%s
                RETURNING state""", (deployment_id,tenant,claim_token))
            row=cur.fetchone()
            if not row:
                raise RuntimeError("reconciliation lease expired or moved")
            cur.execute("""INSERT INTO platform_audit (tenant_id,actor,event,resource_id)
                           VALUES (%s,%s,%s,%s)""",
                        (tenant,actor,"deployment_"+row["state"],deployment_id))

    def create_training(self,tenant,actor,body,namespace):
        job_id=str(uuid4())
        with connect() as conn,conn.cursor() as cur:
            cur.execute("""INSERT INTO platform_training_jobs
                (id,tenant_id,created_by,name,environment,image,dataset_uri,namespace,workers,gpu_per_worker)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                (job_id,tenant,actor,body.name,body.environment,body.image,
                 body.dataset_uri,namespace,body.workers,body.gpu_per_worker))
            cur.execute("""INSERT INTO platform_audit (tenant_id,actor,event,resource_id)
                           VALUES (%s,%s,'training_requested',%s)""",
                        (tenant,actor,job_id))
        return {"id":job_id,"state":"pending","namespace":namespace}

    def training_detail(self,tenant,job_id):
        with connect() as conn,conn.cursor() as cur:
            cur.execute("""SELECT id,tenant_id,name,environment,image,dataset_uri,namespace,
                       workers,gpu_per_worker,state,retry_count,created_at
                       FROM platform_training_jobs WHERE id=%s AND tenant_id=%s""",
                        (job_id,tenant))
            row=cur.fetchone()
        if row is None:
            raise LookupError("training job not found")
        return dict(row)

    def claim_training(self):
        with connect() as conn,conn.cursor() as cur:
            cur.execute("""WITH candidate AS (
                  SELECT id FROM platform_training_jobs
                  WHERE (state IN ('pending','retry') AND next_attempt_at<=now())
                    OR (state='reconciling' AND lease_until<now())
                  ORDER BY created_at,id FOR UPDATE SKIP LOCKED LIMIT 1
                )
                UPDATE platform_training_jobs j
                SET state='reconciling',lease_until=now()+interval '5 minutes',
                    claim_token=gen_random_uuid(),updated_at=now()
                FROM candidate WHERE j.id=candidate.id
                RETURNING j.id,j.tenant_id,j.name,j.environment,j.image,
                          j.dataset_uri,j.workers,j.gpu_per_worker,j.claim_token""")
            row=cur.fetchone()
            return dict(row) if row else None

    def finish_training(self,tenant,actor,job_id,claim_token,state):
        if state!="submitted":
            raise ValueError("invalid training completion state")
        with connect() as conn,conn.cursor() as cur:
            cur.execute("""UPDATE platform_training_jobs
                SET state=%s,claim_token=NULL,lease_until=NULL,updated_at=now()
                WHERE id=%s AND tenant_id=%s AND claim_token=%s
                  AND state='reconciling' RETURNING id""",
                (state,job_id,tenant,claim_token))
            if not cur.fetchone():
                raise RuntimeError("training lease expired")
            cur.execute("""INSERT INTO platform_audit (tenant_id,actor,event,resource_id)
                           VALUES (%s,%s,'training_submitted',%s)""",
                        (tenant,actor,job_id))

    def retry_training(self,tenant,actor,job_id,claim_token):
        with connect() as conn,conn.cursor() as cur:
            cur.execute("""UPDATE platform_training_jobs
                SET retry_count=retry_count+1,
                    state=CASE WHEN retry_count+1>=5 THEN 'failed' ELSE 'retry' END,
                    next_attempt_at=now()+make_interval(secs=>LEAST(300,POWER(2,retry_count+1)::integer*5)),
                    claim_token=NULL,lease_until=NULL,updated_at=now()
                WHERE id=%s AND tenant_id=%s AND claim_token=%s
                  AND state='reconciling' RETURNING state""",
                (job_id,tenant,claim_token))
            row=cur.fetchone()
            if not row:
                raise RuntimeError("training lease expired")
            cur.execute("""INSERT INTO platform_audit (tenant_id,actor,event,resource_id)
                           VALUES (%s,%s,%s,%s)""",
                        (tenant,actor,"training_"+row["state"],job_id))

    def record_inference(self,tenant,actor,deployment_id,status,latency_ms):
        with connect() as conn,conn.cursor() as cur:
            cur.execute("""INSERT INTO platform_inference_events
                (tenant_id,actor,deployment_id,http_status,latency_ms)
                VALUES (%s,%s,%s,%s,%s)""",
                (tenant,actor,deployment_id,status,latency_ms))
