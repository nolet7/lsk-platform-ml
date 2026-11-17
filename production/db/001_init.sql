CREATE TABLE IF NOT EXISTS predictions (
  prediction_id UUID PRIMARY KEY,
  inspection_id TEXT NOT NULL,
  model_version TEXT NOT NULL,
  dataset_sha256 CHAR(64) NOT NULL,
  probability DOUBLE PRECISION NOT NULL CHECK (probability >= 0 AND probability <= 1),
  triage TEXT NOT NULL,
  recorded_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE TABLE IF NOT EXISTS reviews (
  event_id UUID PRIMARY KEY,
  inspection_id TEXT NOT NULL,
  prediction_id UUID NOT NULL UNIQUE REFERENCES predictions(prediction_id),
  reviewer TEXT NOT NULL,
  disposition TEXT NOT NULL CHECK (disposition IN ('accept_for_next_step','hold_for_engineer','reject_for_rework')),
  rationale TEXT NOT NULL,
  recorded_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS predictions_by_inspection ON predictions(inspection_id);
CREATE INDEX IF NOT EXISTS reviews_by_inspection ON reviews(inspection_id);
