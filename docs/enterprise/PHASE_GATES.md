# Contractual delivery gates and acceptance evidence

The gate checker `scripts/verify_phase_gates.py` verifies required control IDs and evidence references in a manifest. It **cannot** prove that an external artifact is authentic, that an AWS deployment exists or that a signer was authorized. Human governance is indispensable.

## Gate 0 — discovery/architecture
- Requirements, functional and nonfunctional targets, AS-IS/TO-BE workflow, QMS authority boundary, ERP/QMS interfaces, synthetic-only policy, classified data flows, ADRs, threat model and accountable owners.
- Acceptance by fictional business sponsor, Quality, Data Governance, Security, and Platform.

## Gate 1 — POC (local)
- `POC-API`: API and SDK walkthrough with synthetic repair orders.
- `POC-TESTS`: passing automated authorization, validation, duplicate review and missing-model tests.
- `POC-LINEAGE`: repeatable dataset/model hashes and test report.
- `POC-SAFETY`: proof model cannot write QMS dispositions without human reviewer workflow.
- Signoff roles: Product Owner, Quality Engineering, Platform Lead. No production claim.

## Gate 2 — pilot (authorized staging)
- `PILOT-IDENTITY`: real OIDC scope/tenant isolation and negative authorization cases.
- `PILOT-MLFLOW`: registry integration, metric/policy evaluation and explicit model approval.
- `PILOT-JOBS`: stage Kubernetes/Ray jobs with CPU/GPU scheduling evidence and isolation tests.
- `PILOT-OBS`: alert/dashboards, incident reproduction, latency/load budgets and cost reports.
- `PILOT-ADOPTION`: real trial by 2 authorized teams, onboarding feedback and audit trace.
- Signoff roles: Product Owner, Quality, Security, ML Lead, SRE Lead.

## Gate 3 — production cutover
- `PROD-INFRA`: protected multi-account private EKS and on-prem connectivity verified with actual provider evidence.
- `PROD-SECURITY`: threat testing, signing, OIDC, sensitive-data handling and least privilege signoff.
- `PROD-RELEASE`: approved immutable model/image canary and demonstrated rollback.
- `PROD-DR`: backup integrity, restored service/data, independently measured RPO and RTO.
- `PROD-SLO`: monitored load, 99.9% target review, measured p95 latency, alerts and error budget.
- `PROD-CAB`: approved change record, release owner, go/no-go and customer communications.
- Signoff roles: CTO Delegate, Quality Authority, Security, Platform SRE, Change Manager.

## Gate 4 — operational handover
- `OPS-RUNBOOK`: updated on-call, paging, incident/escalation, service catalog, known failures.
- `OPS-RECOVERY`: SRE completes incident rehearsal + rollback/restore demonstration.
- `OPS-OWNERSHIP`: named accountable owners, rota, budget, capacity and post-launch reviews.
- Signoff roles: Service Owner, Platform SRE, Quality, Product Owner.

## Evidence rules
- Manifest `status=complete` with a nonempty URL or auditable ticket is required for each control.
- Approvals must have role, named signer, timestamp and reference. Reviewer identity must be verified externally.
- Reject URLs pointing at example/placeholder material as production evidence.
- Final go-live authorization requires humans to verify evidence and recorded legal/security decisions.
- An example NOT READY manifest is deliberately committed; no signed deployment claims are in this repository.
