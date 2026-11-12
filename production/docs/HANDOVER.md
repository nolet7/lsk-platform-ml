# Production ownership, signoff and handover

| Capability | Accountable owner | Evidence before signoff |
|---|---|---|
| ML control plane | ML platform lead | SLA, deployment, OIDC and access tests |
| Data lineage | Data governance | catalog, retention and validation |
| Model evaluation | ML/Quality engineering | thresholds, domain qualification, approval trail |
| Serving | Platform SRE | dashboards, probes, capacity, canary and rollback |
| Kubernetes/GPU | Cloud/platform team | autoscaling, cost controls, node upgrades |
| Security | InfoSec + legal/export | threat model, IAM, residency decision |
| QMS decisions | Authorized quality personnel | SOP, qualified reviewer and audit |

Create service catalog entry, on-call rotation, paging escalation, release checklist, known issues, incident and DR playbooks, API contract, SDK, developer onboarding, IAM request procedure, cost/usage report and quarterly risk register. Schedule post-launch reviews (7/30/90 days) and record genuine performance, accuracy and engineer productivity measurements.

**Portfolio demonstration rule:** Do not put "deployed production AWS ML platform" or enterprise savings on a resume based solely on these files. Show the implemented POC and designed pilot/production artifacts until deployment evidence exists.
