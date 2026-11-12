# Pilot identity / tenancy requirements

POC's `X-Demo-Key` and `X-Reviewer` are **not** security boundaries. Do not expose POC endpoints to shared environments.

Pilot ingress: corporate OIDC → JWT validation at identity-aware API gateway → scoped token claims (issuer, audience, expiry, tenant/team, roles) → application enforcement. Platform ML user actions require membership in the exact project. Training jobs use distinct workload identities scoped to project buckets, MLflow, and registry, with service-account tokens projected and no long-lived AWS keys. Human QMS decisions require corporate identity and QMS roles. Never use headers claimed directly by unauthenticated clients.

Partition MLflow experiments, datasets, artifacts, job metadata, GPU quotas and cost tags by project. Negative tests: cross-team read/list/register/infer; privilege escalation; tampered JWT; expired token; insecure direct object references. A namespace alone is not sufficient tenant isolation.

**Not implemented in code yet:** OIDC gateway, JWT authorization middleware and scoped storage. Pilot admission is blocked until implemented and tested.
