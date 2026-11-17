# Enterprise release evidence — unresolved security and deployment gates

This repository is a **production deployment implementation candidate** with a reusable ML platform.
It is **not certified, running or approved for live enterprise customers**.

## Code and integration evidence

Python API, training, inference and controller tests run in GitHub Actions.
The ML platform CI tests initialize a temporary real PostgreSQL database and execute
model and deployment migrations, approvals, leasing and revision tests.
Terraform formatting, dependency initialization and validation have been exercised.
The Kubernetes and Ray integrations still need live integration and failure testing.

## Security results and disposition

The GitHub `Enterprise ML platform security gates` workflow runs Bandit,
Python dependency audit, Trivy scans and CycloneDX SBOMs. It is deliberately
configured to **fail for high/critical container vulnerabilities**.

The initial Trivy scan of the Debian-based control-plane image reported
**48 HIGH OS findings and zero CRITICAL** on the tested image snapshot.
A number of the reported packages had no upstream fixed version indicated.
This is a **production blocker**, not a waiver or permission to disable scanning.
The report is attached to the GitHub Actions logs / SBOM artifacts.

Required remediations:
1. Evaluate pinned supported patched/distroless/minimal base images by digest.
2. Rebuild all API, worker, inference and Ray images and rerun vulnerability scans.
3. Capture specific CVE-to-fixed-image evidence or an authorized time-limited
   compensating-control exception by the organization's security owner.
4. Verify runtime operation, TLS, signatures/attestations, and live network policy
   with least-privilege identities before release.

## External gates not completed

- Approved AWS account, explicit paid provisioning authorization, `terraform apply`
- Live EKS deployment, AWS OIDC trust, workload role/session verification
- Real MLflow, RDS migrations, KubeRay operator, device plugin, GPU/CPU jobs
- End-to-end model train → register → approve → deploy → infer → rollback → revoke
- Production API ingress TLS, secrets rotation and signed model image admission
- Per-tenant networking and data isolation penetration testing
- Automated progressive rollout/canary metric analysis and drift monitoring
- Measured availability, latency, error budget, GPU spend, backups/restore and DR
- Quality, InfoSec, change management, FinOps and SRE handover signatures

The repository documents the tests required to close these gates. No passed
unit test or Markdown file should be treated as a signed enterprise acceptance.
