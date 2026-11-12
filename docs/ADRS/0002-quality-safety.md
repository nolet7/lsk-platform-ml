# ADR-0002 — human-controlled inspection decisions
**Status:** Accepted for simulation.

No model output can automatically approve, reject, scrap, or release an aerospace component. A human quality inspector with the appropriate identity and role approves or rejects an inspection recommendation in the existing QMS. Inference API is read-only with respect to part disposition. Each prediction returns model version, feature digest, confidence and trace ID. A review command stores reviewer identity, time, decision and the associated model version in an append-only audit stream. Mock API does **not** imply regulated audit compliance.

Design alternatives rejected: direct AI write-back into QMS; model confidence thresholds as autonomous accept/reject. Failure mode: when model unavailable or uncertain, switch to existing manual workflow.
