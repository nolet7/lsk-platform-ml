# POC acceptance checklist
- [ ] Seeded synthetic dataset, dataset SHA-256 and train/test partitions reproducible
- [ ] Model version and dataset digest returned from prediction API
- [ ] Legacy repair-order and inspection APIs respond with versioned contracts
- [ ] Invalid inputs rejected; missing inspections return 404
- [ ] Missing model returns 503, no silent fallback to unknown model
- [ ] API denies requests without local demo key
- [ ] Prediction does not create review or release/accept a part
- [ ] Reviewer header and linked prediction required for manual review; no double review
- [ ] /healthz and /metrics observable; CI pytest passes
- [ ] Security limitations documented and API binds localhost

**Evidence required:** capture terminal pytest, actual training report, curl responses and demo walkthrough. No simulated or fabricated test result counts.
