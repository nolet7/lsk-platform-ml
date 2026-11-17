-- Apply after 002_platform_control_plane.sql, with a controlled migration role.
-- Durable queue: request transaction commits before Kubernetes operations.
ALTER TABLE platform_deployments
  ADD COLUMN IF NOT EXISTS retry_count INTEGER NOT NULL DEFAULT 0,
  ADD COLUMN IF NOT EXISTS next_attempt_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  ADD COLUMN IF NOT EXISTS lease_until TIMESTAMPTZ;
ALTER TABLE platform_deployments DROP CONSTRAINT IF EXISTS platform_deployments_state_check;
ALTER TABLE platform_deployments ADD CONSTRAINT platform_deployments_state_check
  CHECK(state IN ('pending','reconciling','retry','failed','submitted','superseded'));
CREATE INDEX IF NOT EXISTS platform_deployments_work_queue
  ON platform_deployments(next_attempt_at,created_at)
  WHERE state IN ('pending','retry','reconciling');
-- Deployment audit is append only; application identity must not get UPDATE/DELETE on platform_audit.
