# Example: Ray training → MLflow → model deployment

The platform expects a Ray-compatible training image with
`python -m lsk_training.entrypoint`. This sample implements that contract for
a **synthetic CSV binary classifier**, using Ray parallel hyperparameter
evaluation and MLflow experiment tracking. This example uses CPU algorithms;
GPU RayJob scheduling is available but this code is **not GPU training**.

1. Generate synthetic CSV:

```bash
python examples/ray_training/generate_synthetic_dataset.py \
  --output /tmp/synthetic-training.csv
```

2. Platform administrator grants per-tenant AWS Pod Identity read-only S3
   access and an MLflow token in a **tenant-local** Kubernetes Secret named
   `ml-training-mlflow` with key `token`. Do not use cluster-wide root
   credentials. Approve tenant egress to private S3/MLflow endpoints.
3. Upload the generated CSV under approved
   `s3://<TRAINING_DATASET_BUCKET>/<tenant>/datasets/<version>.csv`.
4. Build the Ray image from a reviewed source revision (example):

```bash
docker build -f examples/ray_training/Dockerfile \
  --build-arg SOURCE_GIT_SHA="$(git rev-parse HEAD)" \
  -t lsk-training:local .
```

5. Scan, sign and push the image to approved ECR; supply immutable `@sha256`
   digest to the platform SDK `train_model()`. Do not deploy local tags.
6. Confirm KubeRay operator, CPU/GPU quotas and RAY_RUNTIME_VERSION match
   the training image. Observe `RayJob` completion and MLflow `FINISHED` run.
7. Package a separate inference serving image compatible with `/predict`.
   Bind its immutable digest to the completed MLflow run `inference_image` tag
   through authorized model-build automation and independent provenance
   attestation. Model registration then checks evaluation and image matching.
8. A different authorized ML reviewer approves the model; use
   `deploy_model()`, `status()`, `predict()`, and `rollback()`.

**Evidence missing:** there is no real AWS/S3/MLflow/Ray job run from this chat.
The sample is for controlled integration validation, not an audited production
model or aerospace quality decision.
