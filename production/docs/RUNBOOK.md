# On-call runbooks

## 1. Model inference regression
Trigger: model p95 or 5xx SLO burn, unusual output distribution, inspector escalation.
- Page serving SRE and ML owner; capture trace IDs, image/model digests and exact stage.
- Pause Argo CD rollout or canary, route humans to manual inspection.
- Verify dataset/schema compatibility, rollback **only** to last approved and signed revision.
- Check prediction queue/outbound dependencies and compare baseline.
- Preserve incident log and QMS human decisions; do not auto-release hardware.
- Close after documented root cause and controlled recovery.

## 2. GPU queue saturation
Inspect pending pod reasons, taints, device plugin, cluster autoscaler/Karpenter, AWS quotas, cost caps, Ray health, node pressure and storage throughput. Increase within approved budget, prioritize safety-critical authorized workloads, stop runaway jobs, monitor queue time and utilization.

## 3. Registry / object storage outage
Block new model promotions. Existing serving uses pinned local/cache model if integrity validated. Confirm RDS and S3 service health, restore separately and reconcile hashes before enabling promotion.

## 4. Dataset integrity or suspected leakage
Freeze training and artifact promotion, revoke implicated workload identity, preserve logs, engage security/legal/export-control owner, quarantine affected dataset versions; do not publicize confidential incident contents.

## Required records
Incident severity/impact start-end, customer impact, SLO burn, exact OCI/model digest, approval chain, runbook steps, restoration evidence, corrective actions and owner.
