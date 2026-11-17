-- Run after 002 and 003 with migration role. Training requires KubeRay CRD.
CREATE TABLE IF NOT EXISTS platform_training_jobs (
  id UUID PRIMARY KEY,
  tenant_id TEXT NOT NULL,
  created_by TEXT NOT NULL,
  name TEXT NOT NULL,
  environment TEXT NOT NULL CHECK(environment IN ('stage','production')),
  image TEXT NOT NULL,
  dataset_uri TEXT NOT NULL,
  namespace TEXT NOT NULL,
  workers INTEGER NOT NULL CHECK(workers BETWEEN 1 AND 4),
  gpu_per_worker INTEGER NOT NULL CHECK(gpu_per_worker BETWEEN 0 AND 1),
  state TEXT NOT NULL DEFAULT 'pending'
    CHECK(state IN ('pending','reconciling','retry','failed','submitted')),
  retry_count INTEGER NOT NULL DEFAULT 0,
  next_attempt_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  lease_until TIMESTAMPTZ,
  claim_token UUID,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS platform_training_queue
  ON platform_training_jobs(next_attempt_at,created_at)
  WHERE state IN ('pending','retry','reconciling');
CREATE INDEX IF NOT EXISTS platform_training_tenant
  ON platform_training_jobs(tenant_id,created_at DESC);
