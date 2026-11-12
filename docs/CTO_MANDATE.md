# CTO mandate — aerospace inspection ML platform

**Sponsor:** fictional aerospace repair enterprise CTO; **technical owner:** ML Platform Engineering; **customers:** Quality Engineering, Repair Engineering, Data Science, IT/SRE, Security.

## Problem
Current repair-order status, inspection records, image references and technician comments sit in separate ERP/MRO, QMS and file systems. Data scientists reassemble one-off datasets, experiments are not reproducible, and inference services lack standard deployment, traceability and operational ownership. This creates delays and inconsistent auditability.

## Deliver
A **shared internal ML infrastructure product**, not a one-off classifier:
1. Integrate a pre-existing repair-order/inspection workflow through versioned, read-only connectors.
2. Publish governed, versioned inspection datasets with lineage and retention.
3. Offer self-service Python SDK/CLI and declarative training jobs, standardized CPU/GPU execution on Kubernetes, optional on-prem worker clusters.
4. Track experiments, datasets, model artifacts, metrics and owners in MLflow; support registry/approval and reproducible promotion.
5. Deploy immutable batch/online model versions with safe rollback; quality decisions remain human-controlled.
6. Expose metrics, traces, logs, training queue wait, resource utilization, drift and costs by team; enforce budgets and SLOs.

## Constraints
No real Chromalloy data, designs, images, customers or credentials. Simulation only. Aviation quality/airworthiness dispositions **never automated**. Isolate customer data and service identities; validate export-control eligibility before onboarding real data. Multi-AZ cloud foundation with signed artifacts, private networking, encryption, audit and regulated retention subject to legal review.

## Success measures (targets, not actual results)
- POC: 100% contract, authorization, lineage and manual disposition tests pass; reproducible CPU training and served inference on synthetic data.
- Pilot: >=2 engineering teams; >=90% training runs reproducible; >=95% approved model deployments via pipeline; onboarding <1 business day; zero unapproved model promotion.
- Production SLO candidates: API availability 99.9%; online prediction p95 <400 ms excluding external calls; pipeline success >=99% for valid runs; RPO <=1h, RTO <=4h (confirm with business).
- Cost/throughput: report GPU-hours, job queue time, utilization, inference cost per 1k requests; baseline before assigning improvement claims.

## Acceptance authority
CTO and architecture review board: funding and architecture. Quality: model workflow and manual review. Security and legal/export-control: access boundary. Platform SRE: reliability, incident response, capacity, DR. ML team: reproducibility and evaluation. No production acceptance without all signoffs.
