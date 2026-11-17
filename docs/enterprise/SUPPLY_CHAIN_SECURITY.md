# ML model artifact and image provenance

Approved production model workflows must bind a reproducible MLflow run
(dataset hash, code hash, evaluation metric and independent signoff) to an
immutable image digest. A tag or a self-written run tag does not cryptographically
prove that an image was built from the evaluated model.

The repository's CI now runs dependency and source audits, container
vulnerability scans and CycloneDX SBOM generation. **This does not yet implement
an enforceable image signature admission policy.** For enterprise production:

1. Build an OCI model image from a reviewed source commit and locked dependencies.
2. Generate SBOM and scan for high/critical vulnerabilities.
3. Sign the image and a separate provenance statement tying model run ID,
   source commit and dataset digest to the image SHA256.
4. Verify signature, trusted issuer, builder identity, attestation subject digest,
   evaluation policy and tenant authority at model registration and cluster admission.
5. Enforce non-bypassable verification (e.g., security-approved admission policy).
6. Store evidence in immutable audit retention and rehearse key revocation/rollback.

This requirement is a formal external **release blocker**, not a pass from
placing these instructions in source control.
