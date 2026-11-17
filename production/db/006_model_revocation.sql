-- Governance override for faulty, unsafe or superseded model artifacts.
ALTER TABLE platform_models
  ADD COLUMN IF NOT EXISTS revoked_by TEXT,
  ADD COLUMN IF NOT EXISTS revocation_reason TEXT,
  ADD COLUMN IF NOT EXISTS revoked_at TIMESTAMPTZ;
CREATE INDEX IF NOT EXISTS platform_models_active
  ON platform_models(tenant_id,name,model_version)
  WHERE revoked_at IS NULL;
