-- Run under approved migration identity before deploying platform-api.
-- App identity: SELECT, INSERT and narrowly scoped UPDATE on these tables.
CREATE TABLE IF NOT EXISTS platform_models (
  id UUID PRIMARY KEY,
  tenant_id TEXT NOT NULL,
  name TEXT NOT NULL,
  model_version TEXT NOT NULL,
  image TEXT NOT NULL,
  evaluation_reference TEXT NOT NULL,
  source_run_id TEXT NOT NULL,
  model_artifact_uri TEXT NOT NULL,
  created_by TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  approved_by TEXT,
  approval_reason TEXT,
  approved_at TIMESTAMPTZ,
  UNIQUE(tenant_id,name,model_version)
);
CREATE TABLE IF NOT EXISTS platform_deployments (
  id UUID PRIMARY KEY,
  tenant_id TEXT NOT NULL,
  name TEXT NOT NULL,
  environment TEXT NOT NULL CHECK(environment IN ('stage','production')),
  revision INT NOT NULL CHECK(revision>0),
  model_id UUID NOT NULL REFERENCES platform_models(id),
  image TEXT NOT NULL,
  replicas INT NOT NULL CHECK(replicas BETWEEN 2 AND 10),
  namespace TEXT NOT NULL,
  state TEXT NOT NULL CHECK(state IN ('pending','failed','submitted')),
  requested_by TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE(tenant_id,name,environment,revision)
);
CREATE TABLE IF NOT EXISTS platform_audit (
  id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  tenant_id TEXT NOT NULL,
  actor TEXT NOT NULL,
  event TEXT NOT NULL,
  resource_id UUID NOT NULL,
  occurred_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS platform_deployments_lookup
  ON platform_deployments(tenant_id,name,environment,revision DESC);
CREATE INDEX IF NOT EXISTS platform_audit_lookup ON platform_audit(tenant_id,resource_id);
