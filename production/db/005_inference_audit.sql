-- Metadata-only prediction access audit; no features or model outputs stored.
CREATE TABLE IF NOT EXISTS platform_inference_events (
  id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  tenant_id TEXT NOT NULL,
  actor TEXT NOT NULL,
  deployment_id UUID NOT NULL REFERENCES platform_deployments(id),
  http_status INTEGER NOT NULL,
  latency_ms DOUBLE PRECISION NOT NULL CHECK(latency_ms >= 0),
  recorded_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS platform_inference_by_tenant
  ON platform_inference_events(tenant_id,recorded_at DESC);
