# Stage gates and phased build

| Gate | POC | Pilot | Production |
|---|---|---|---|
| Users | 1 simulated quality team | 2 authorized internal teams | multiple governed business units |
| Workload | local CPU, synthetic | staging cluster, real orchestrated jobs on synthetic data | AWS EKS/on-prem deployment blueprint and approved controlled rollout |
| Data | fixtures with lineage | governed snapshots, catalog, encryption | residency controls, retention, backup/DR |
| Model | local sklearn training | MLflow registration, evaluation policy, approval workflow | signed immutable artifact promotion, canary/rollback |
| Security | demo API key, input validation | OIDC, namespace isolation, tenant scoping | IAM, policy as code, supply chain controls, audit evidence |
| Operations | health/metrics | alerts, dashboards, error budgets | SLOs, DR drills, scaling and incident on-call |
| Exit | tests + walkthrough | security, quality, platform signoff | formal CAB, SRE readiness, rollback exercise |

**Branch semantics:** main=charter; poc=executable learning baseline; pilot=poc plus integration and pilot assets; production=pilot plus production design/deployment assets. These are phase snapshots, *not* a claim of deployment or regulatory certification.

## Work packages
1. Business discovery: stakeholders, AS-IS swimlane, integration inventory, data classification, customer journey and success criteria.
2. Architecture review: C4 context/container, ADR, trust model, threat model, API contracts and nonfunctional requirements.
3. POC: legacy-first FastAPI app, synthetic source records, model pipeline, inference, manual review, unit+integration tests and run instructions.
4. Pilot: shared team APIs, OIDC proxy, MLflow, batch pipelines, isolated namespaces, test/stage environments, evaluation, dashboard and adoption feedback.
5. Production: infrastructure-as-code, GitOps promotion, sealed access, cost metering, canary+rollback, DR, load tests, ownership and handover.

Document deviations, unresolved dependencies, signoff dates and measured evidence; never substitute a proposed design for passed tests.
