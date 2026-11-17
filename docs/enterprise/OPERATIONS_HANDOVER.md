# Production operational handover — working template, not signed

## Service ownership
| Domain | Accountable role | On-call action |
|---|---|---|
| Business workflows / quality | Quality owner | Use manual inspection during model outage; only authorized QMS actor decides disposition |
| API and Python SDK | ML Platform lead | Check auth failures, p95 latency, 5xx, quotas, contracts, dependency health |
| Model lifecycle | ML engineering | Check dataset lineage, evaluation thresholds, registry and rollback digest |
| Kubernetes/EKS/hybrid | SRE team | Check nodes, autoscaler, GPU device plugin, IRSA/Pod Identity, network policies |
| Data and recovery | Database/storage owner | Validate Postgres PITR, S3 digest/retention and restore location |
| Security | Security incident commander | Rotate secrets, isolate tenants, block promotion and preserve audit artifacts |

## Service catalog record (fill during real rollout)
- Service owner / deputy: **TBD / TBD**
- Pager / team channel / runbook URLs: **TBD / TBD / TBD**
- Environment / AWS accounts / regions / cluster identifiers: **TBD**
- Customer data classification and residency: **synthetic-only currently; real usage TBD**
- SLO, latency budget and availability window: **candidates only**
- RTO / RPO: **4h / 1h proposed, not verified**
- Approved model and image digests: **TBD**
- Dashboard / tracing / cost allocation: **TBD**

## Minimum incident playbooks
1. **API unavailable:** page on-call; verify ingress, auth, pods and dependencies; fail open to **manual inspection only**, never automated acceptance; incident comms at agreed cadence.
2. **Inference latency spike:** correlate version and load, rollback to last approved signed model/image, check CPU/GPU throttling, queue wait and autoscaling.
3. **MLflow/registry unavailable:** freeze model promotions; keep running approved immutable model revision.
4. **Suspected cross-tenant data incident:** disable affected access path, preserve audit logs, invoke incident response and legal/export review.
5. **Backup or AZ failure:** restore into an isolated environment and compare digest, measure achieved RPO/RTO before approving recovery.
6. **Bad model / drift:** stop promotion or roll back serving; quality personnel re-review affected cases in QMS.

## Operational acceptance
- Pager rotation and escalation tested, with backup coverage.
- Alert-to-ticket trace, service logs, traces, metrics, and audit recording reviewed.
- Canary rollback and isolated backup restoration observed with timestamped evidence.
- Synthetic load, cost and failure-injection reports attached.
- Security + Quality + Service Owner + CTO delegate authorize go-live; incident rehearsal validates responders.
- Joint 7/30/90-day reviews: adoption, failed workflows, GPU spend, SLA error budget and unresolved risks.

**Handover status: NOT STARTED.** An unsigned template is not an operations transfer.
