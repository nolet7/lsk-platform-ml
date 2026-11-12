# Security, compliance and governance
Data classes: public synthetic; internal repair metadata; customer confidential; controlled technical data (potential export controls). This **public repo permits synthetic only**. A real corporate rollout requires legal, compliance and security review (including relevant ITAR/EAR obligations where applicable), formal data handling agreements and customer-specific access policy.

Threats: cross-tenant leakage, dataset/model poisoning, artifact substitution, service account privilege escalation, inference exfiltration, malicious container images, unbounded GPU spend and prompt/label injection in technician notes.

Controls: private endpoints, IAM least privilege, per-project namespaces, Kubernetes NetworkPolicy, workload identity, signed/attested images and model digests, validated schemas, deny-by-default approvals, encrypted storage and transit, secrets externalized, central audit export, redaction and retention schedules, resource quotas and egress allowlists. The POC uses an **explicitly insecure demo key** that must not be used on a public network.

Required evidence before production: threat model reviewed, penetration test, isolation tests, vulnerability scan, SBOM, access review, artifact integrity, backup restore, key rotation, tenant deletion/retention verification.
