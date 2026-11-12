# Threat model / control validation

| Threat | Control | Evidence |
|---|---|---|
| Cross-project object access | IAM workload identity + S3 key prefix policy + API project scope | negative read/list tests |
| Malicious training artifact | pinned digest, signature verification, SBOM, restricted egress | admission denial proof |
| Unauthorized model promotion | evaluated report + separate approvers + immutable deployment config | tampered approval blocked |
| Data exfiltration | private VPC endpoints and allowlisted destinations, tenant egress control | flow logs and synthetic leak test |
| GPU resource exhaustion | quotas, priority, budget and rate limiting | load/cost test |
| Poisoned dataset/labels | signed manifest, validation, provenance and quality-owner signoff | quarantine and rollback |
| QMS disposition automation | inference identity has no QMS write permissions | enforced auth negative test |
| Compromised runtime | Pod Security restricted, read-only root FS, no privilege escalation, network policy | policy scan |

Review ITAR/EAR applicability, customer contracts, regional residency, retention and qualified quality system controls before any real aerospace data is used. This repo contains no such data.
