# LSK Enterprise ML Infrastructure Platform — Aerospace Repair Operations

**Independent portfolio simulation using synthetic data.** This repository is not a Chromalloy system and does not establish that a production platform was deployed for any employer. Model output is decision support only; qualified inspectors retain final disposition authority.

## Business outcome and CTO mandate
The fictional CTO has commissioned a shared, secure, self-service ML platform for aerospace inspection triage. Replace fragmented, manually assembled inspection datasets and one-off model deployment with traceable training, governed promotion, human-reviewed inference, operational accountability, and a repeatable POC → pilot → production handover process.

**In scope:** synthetic ERP/MRO and QMS integration, data lineage, Python/FastAPI platform API and SDK, reproducible training and evaluation, reference MLflow/Ray/EKS/on-prem integration, approval and audit boundaries, observability, cost controls and disaster recovery readiness.
**Out of scope:** automated airworthiness disposition, use of proprietary/export-controlled data, and claims of real-company production deployments.

## User journey
1. Quality engineer opens a synthetic repair order and inspection in the legacy simulator.
2. ML engineer creates a reproducible dataset and trains a synthetic classifier with `python -m ml.train`.
3. Platform API serves an approved local POC artifact through `POST /v1/predictions`; it records the prediction, never a part acceptance.
4. Qualified simulated reviewer records disposition through `POST /v1/reviews`. Duplicate decisions are rejected.
5. Platform engineer checks service metrics and tests; pilot/production targets add governed registry, OIDC, GPU jobs, approval gates, GitOps and on-call operations.
6. Delivery lead records evidence and obtains explicit phase signoffs before promoting any environment.

## Branches
- `poc`: runnable synthetic Python/FastAPI POC, SDK, training and contract tests.
- `pilot`: pilot manifests and MLflow/Ray integration design; not proof of an operational pilot.
- `production`: gated AWS/EKS/hybrid target blueprint; **not deployed**.
- `feature/bulletin-1-enterprise-lifecycle`: integrated lifecycle-management upgrade plus runnable evidence gate (based on `production`).
- `main`: original executive charter/reference materials.

## Run the implemented POC
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m ml.train
python -m pytest -q
uvicorn app.main:app --host 127.0.0.1 --port 8000
```
On Windows use `.venv\Scripts\activate`. The POC uses a demo key; it is **not** suitable for exposure on a public network.

## Enterprise delivery evidence
- [CTO charter](docs/CTO_MANDATE.md) and [Bulletin 1 traceability](docs/BULLETIN_1_TRACEABILITY.md)
- [Stakeholders and requirements](docs/enterprise/REQUIREMENTS_AND_DISCOVERY.md)
- [Prioritized engineering backlog](docs/enterprise/IMPLEMENTATION_BACKLOG.md)
- [POC/pilot/production acceptance gates](docs/enterprise/PHASE_GATES.md)
- [Cutover, runbooks and ownership](docs/enterprise/OPERATIONS_HANDOVER.md)
- [Risk and decision register](docs/enterprise/RISK_REGISTER.md)
- [Evidence template](evidence/phase-gates.example.json) and [validator](scripts/verify_phase_gates.py)

Check the example without creating a false deployment claim:
```bash
python scripts/verify_phase_gates.py evidence/phase-gates.example.json
```
This should report **NOT READY**, as the example has no executed test artifacts or authorized signoffs. Use `--phase poc` (or pilot/production) to check a specific gate. Evidence verification checks completeness and references, not authenticity of external documents.

## Deployment status
**Implemented:** synthetic legacy workflows, FastAPI inference/review, SDK, deterministic local training and pytest coverage.
**Designed/partly scaffolded:** Kubernetes namespace isolation, evaluation policies, MLflow, Ray, GPU scheduling, EKS networking, identity, multi-environment promotion, logging, DR, SRE handover.
**Not verified:** real AWS deployment, real production usage, capacity benchmarks, backup restoration, security assessment, pilot signoffs or operational SLOs. See traceability and backlog for outstanding delivery work.
