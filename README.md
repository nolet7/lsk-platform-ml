# LSK Platform ML — Aerospace Repair ML Infrastructure

> **Independent portfolio simulation.** Inspired by aerospace component repair workflows at companies such as Chromalloy. This project is **not** a Chromalloy-owned system, and uses synthetic data only. No customer, export-controlled, proprietary, or production data.

## CTO mandate
Provide one governed, self-service ML platform for Quality Engineering, Repair Engineering, Data Science, and Platform/SRE teams. Start from existing ERP/MRO repair orders, inspection imaging and engineering quality workflows. Add reproducible datasets, experiment tracking, model registration, batch and online inference, and auditable human review without granting models authority to accept or reject flight-critical hardware.

Business scenario: aerospace turbine component inspection triage. Simulated repair orders and synthetic inspection images flow through ingestion and labeling, distributed training, review of model artifacts, and GPU-ready Kubernetes inference. Model predictions **assist** qualified inspectors; final disposition stays in the existing quality management workflow.

## Phases / branches
- [poc](../../tree/poc): runnable local legacy MRO/quality simulator plus ML experiment/inference, contract and isolation tests.
- [pilot](../../tree/pilot): adds infrastructure manifests, workflow orchestration, registry, approval gates and team onboarding.
- [production](../../tree/production): target multi-environment AWS/EKS hybrid architecture with GitOps, policy, SRE runbooks and promotion gates. **Blueprint only until deployed and validated.**
- [main](../../tree/main): CTO charter, reference architecture, ADRs and program delivery contract.

## End-to-end flow
Repair order (synthetic ERP/MRO) → inspection image metadata → approved dataset snapshot → training job → MLflow experiment/model candidate → evaluation gates → human quality/platform approval → versioned inference service → inspector work queue → recorded human disposition → model monitoring and retraining triggers.

## Engineering principles
Python/FastAPI, typed SDK, versioned APIs; MLflow for experiment/registry; Ray Jobs for scale-out option; Kubernetes/EKS as the common runtime; S3-compatible object storage; PostgreSQL for transactional metadata; OpenTelemetry + Prometheus/Grafana; least-privilege and network boundaries; GitHub Actions gates; Terraform + Helm/Argo CD promotion. Use synthetic data, pin dependencies, never store credentials in Git.

## Business and operational safety
- Human approval remains mandatory for all quality and airworthiness decisions.
- Predictions must never mutate ERP/QMS disposition records directly.
- Export-controlled and customer-proprietary data are prohibited from this public repository.
- The pilot/production environments are *designed*, not claimed deployed.
- No performance improvements or savings are claimed without measured evidence.

See `docs/` for architecture, ADRs, service boundaries, delivery phases, SLOs and acceptance tests.
