# Register an inference model with MLflow lineage

This snippet is a reference for **an authorized ML engineer's existing MLflow environment**, not an executed production integration.

1. Train/evaluate with reproducible dataset and pinned commit.
2. Log MLflow tags `tenant_id`, `dataset_sha256`, `git_sha`, `evaluation_ref`.
3. Log metric `validation_auc` meeting the platform's agreed threshold.
4. Log model artifact to path `model` in the **same MLflow run**.
5. Build the separate inference OCI container and push it to approved ECR, retaining the exact immutable `registry/repository@sha256:...` digest.
6. Attach `inference_image` tag with that **exact** OCI digest. Record image signature and supply-chain evidence separately; metadata tagging alone is not an attestation.
7. Pass `runs:/<run_id>/model`, run ID, evaluation reference and OCI digest to `MLPlatformClient.register_model`.
8. Different actor approves, then an authorized deployer chooses environment, model and replicas.

The server calls the actual MLflow REST run API and fails closed on bad/unfinished run, mismatched tenant, metadata or threshold. The application does not pull arbitrary model binaries from MLflow; only approved ECR inference images become Kubernetes pods. A full production implementation should additionally verify signed image-to-run provenance, MLflow authentication/authorization isolation, registry aliases and dataset authorization.

Runtime `MLFLOW_TRACKING_URI` must be HTTPS and `MLFLOW_TRACKING_TOKEN` securely provisioned.
