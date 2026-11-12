# Platform operations, SLOs and runbooks

Proposed SLOs (validate with workload owners): platform API 99.9% 30-day availability; inference p95 <=400ms; 99% valid pipeline completion; >=99.5% approved registry artifact pulls; training job admission p95 <=10 min when quota available. Separate manual inspection business SLAs from inference SLAs.

Golden signals: request rate/errors/latency, saturation (CPU/GPU/VRAM), worker queue depth, GPU allocation/cost, dataset freshness, model skew/drift, blocked promotions, failed DAGs, model digest and rollout health. Alert on user-impacting symptoms, not arbitrary CPU thresholds.

Runbooks:
1. **Inference errors:** check canary/version, correlation ID, per-tenant limits and object-store access; stop rollout; roll back to previous approved digest; direct operators to manual inspection.
2. **Training backlog:** check quotas/taints, autoscaler, GPU capacity, stuck pods; scale within budget or throttle low-priority queues.
3. **Dataset mismatch:** quarantine snapshot, freeze affected training, reconcile schema+checksums, require dataset owner approval.
4. **Registry down:** block promotions, maintain pinned serving revision, restore PostgreSQL and artifacts from verified backups.
5. **Security event:** disable affected workloads, rotate scoped credentials, preserve logs and follow incident escalation; do not disclose controlled repair data.

Drills: quarterly rollback, backup restore, AZ failure, compromise simulation; record actual RTO/RPO and owner signoff.
